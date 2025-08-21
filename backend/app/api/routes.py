from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from passlib.context import CryptContext

from fastapi.params import Body

from app.data.dependencies import get_db
from sqlalchemy.orm import Session
from app.data.models import (
    Category,
    Empresa,
    Transaction as TransactionModel,
    UserModel,
)
from app.api.models.models import (
    BusinessSchema,
    Transaction,
    PutTransaction,
    UserLoginSchema,
    UserSchema,
)
from app.api.models.models_response import (
    CategoryResponse,
    TransactionResponse,
    UserResponse,
)

from .auth.auth_handler import sign_jwt
from .auth.auth_bearer import JWTBearer

router = APIRouter()


def validate_transaction(transaction):
    if transaction.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Transaction amount must be greater than zero"
        )
    if transaction.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=400, detail="Transaction type must be 'income' or 'expense'"
        )
    if not transaction.date:
        raise HTTPException(status_code=400, detail="Transaction date is required")
    if not transaction.description:
        raise HTTPException(
            status_code=400, detail="Transaction description is required"
        )
    return transaction


def to_response(
    transaction: TransactionModel, category_name: str
) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        amount=float(transaction.amount),
        category_name=category_name,
        createdAt=transaction.created_at.isoformat(),
        date=transaction.date.isoformat(),
        description=transaction.description,
        type=transaction.type,
        empresa_id=transaction.empresa_id,
        usuario_id=transaction.usuario_id,
        notes=transaction.notes,
    )


def get_category_name(db: Session, category_id: int) -> str:
    category = db.query(Category).filter(Category.id == category_id).first()
    return category.name if category else "Unknown Category"


def build_transaction_model(data: Transaction | PutTransaction) -> TransactionModel:
    return TransactionModel(
        amount=data.amount,
        category_id=data.category_id,
        created_at=(
            datetime.fromisoformat(data.createdAt)
            if data.createdAt
            else datetime.utcnow()
        ),
        date=datetime.fromisoformat(data.date),
        description=data.description,
        type=data.type,
        notes=data.notes,
    )


def check_user(db: Session, data: UserLoginSchema):
    user = db.query(UserSchema).filter(UserSchema.email == data.email).first()
    if user and user.password == data.password:
        return sign_jwt(user.email)
    return None


def get_business(db: Session):
    business = db.query(Empresa).all()
    if not business:
        raise HTTPException(status_code=404, detail="No business found")
    return business


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def check_user(db: Session, data: UserLoginSchema):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()
    if user and verify_password(data.password, user.password):
        # if business exists, get its name
        business_name = None
        if user.empresa:
            business = db.query(Empresa).filter(Empresa.id == user.empresa_id).first()
            business_name = business.nome if business else None

        user_to_hash = UserResponse(
            id=user.id,
            nome=user.nome,
            email=user.email,
            cargo=user.cargo,
            telefone=user.telefone,
            empresa_nome=business_name,
        )
        return sign_jwt(user_to_hash)
    return None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    empresa_id = None
    if user.empresa:
        business = db.query(Empresa).filter(Empresa.nome == user.empresa).first()
        if not business:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        empresa_id = business.id

    new_user = UserModel(
        nome=user.nome,
        email=user.email,
        cargo=user.cargo,
        telefone=user.telefone,
        empresa_id=empresa_id,
        password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user_to_hash = UserResponse(
        id=new_user.id,
        nome=new_user.nome,
        email=new_user.email,
        cargo=new_user.cargo,
        telefone=new_user.telefone,
        empresa_nome=business.nome if empresa_id else None,
    )
    return sign_jwt(user_to_hash)


@router.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema, db: Session = Depends(get_db)):
    token = check_user(db, user)
    if token:
        return token
    return {"error": "Credenciais inválidas"}


@router.post("/user/logout", tags=["user"], dependencies=[Depends(JWTBearer())])
async def user_logout(db: Session = Depends(get_db), email: str = Body(...)):
    # Implement logout logic if needed, e.g., invalidate token
    # For JWT, this is typically handled on the client side by deleting the token
    if not email:
        raise HTTPException(status_code=400, detail="Email is required for logout")
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User logged out successfully"}


@router.get("/user/profile", tags=["user"], dependencies=[Depends(JWTBearer())])
async def get_user_profile(db: Session = Depends(get_db), email: str = Body(...)):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # get business name by id
    empresa_nome = None
    if user.empresa_id:
        business = db.query(Empresa).filter(Empresa.id == user.empresa_id).first()
        if business:
            empresa_nome = business.nome

    return UserResponse(
        id=user.id,
        nome=user.nome,
        email=user.email,
        cargo=user.cargo,
        telefone=user.telefone,
        empresa_nome=empresa_nome,
    )


@router.put("/user/profile", tags=["user"], dependencies=[Depends(JWTBearer())])
async def update_user_profile(user: UserSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.id == user.id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_user.nome = user.nome
    existing_user.email = user.email
    existing_user.cargo = user.cargo
    existing_user.telefone = user.telefone
    # get empresa by name
    if user.empresa:
        business = db.query(Empresa).filter(Empresa.id == user.empresa).first()
        if not business:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        existing_user.empresa_id = business.id

    if user.password:
        existing_user.password = hash_password(user.password)

    db.commit()
    db.refresh(existing_user)
    return UserSchema(
        id=existing_user.id,
        nome=existing_user.nome,
        email=existing_user.email,
        cargo=existing_user.cargo,
        telefone=existing_user.telefone,
        empresa_id=existing_user.empresa_id,
    )


@router.get(
    "/users",
    tags=["user"],
    response_model=List[UserResponse],
    dependencies=[Depends(JWTBearer())],
)
async def get_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    list_users = []
    for user in users:
        empresa_nome = None
        if user.empresa_id:
            business = db.query(Empresa).filter(Empresa.id == user.empresa_id).first()
            empresa_nome = business.nome if business else None
        list_users.append(
            UserResponse(
                id=user.id,
                nome=user.nome,
                email=user.email,
                cargo=user.cargo,
                telefone=user.telefone,
                empresa_nome=empresa_nome,
            )
        )
    if not list_users:
        raise HTTPException(status_code=404, detail="No users found")
    return list_users


@router.post("/business", tags=["business"])
async def create_business(business: BusinessSchema, db: Session = Depends(get_db)):
    db_business = db.query(Empresa).filter(Empresa.cnpj == business.cnpj).first()
    if db_business:
        raise HTTPException(status_code=400, detail="CNPJ já registrado")
    new_business = Empresa(
        nome=business.nome_empresa,
        cnpj=business.cnpj,
        telefone=business.telefone_empresa,
        endereco=business.endereco,
    )
    db.add(new_business)
    db.commit()
    db.refresh(new_business)

    return {"message": "Business created successfully", "business_id": new_business.id}


@router.get("/business", tags=["business"])
async def get_business(db: Session = Depends(get_db)):
    business = db.query(Empresa).all()
    if not business:
        raise HTTPException(status_code=404, detail="No business found")
    return business


@router.put("/business/{business_id}", tags=["business"])
async def update_business(
    business_id: int, business: BusinessSchema, db: Session = Depends(get_db)
):
    existing_business = db.query(Empresa).filter(Empresa.id == business_id).first()
    if not existing_business:
        raise HTTPException(status_code=404, detail="Business not found")

    existing_business.nome = business.nome_empresa
    existing_business.cnpj = business.cnpj
    existing_business.telefone = business.telefone_empresa
    existing_business.endereco = business.endereco

    db.commit()
    db.refresh(existing_business)
    return {"message": "Business updated successfully"}


@router.get(
    "/transactions",
    tags=["transactions"],
    response_model=List[TransactionResponse],
    dependencies=[Depends(JWTBearer())],
)
async def get_transactions(db: Session = Depends(get_db)):
    transactions_db = db.query(TransactionModel).all()
    if not transactions_db:
        raise HTTPException(status_code=404, detail="No transactions found")
    categories = {c.id: c.name for c in db.query(Category).all()}
    return [
        to_response(t, categories.get(t.category_id, "Unknown Category"))
        for t in transactions_db
    ]


@router.post(
    "/transactions",
    tags=["transactions"],
    response_model=TransactionResponse,
    dependencies=[Depends(JWTBearer())],
)
async def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    validate_transaction(transaction)
    if not transaction.category_id:
        raise HTTPException(status_code=400, detail="Category ID is required")
    category = db.query(Category).filter(Category.id == transaction.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    new_transaction = build_transaction_model(transaction)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return to_response(new_transaction, category.name)


@router.put(
    "/transactions/{transaction_id}",
    tags=["transactions"],
    response_model=TransactionResponse,
    dependencies=[Depends(JWTBearer())],
)
async def update_transaction(
    transaction: PutTransaction, transaction_id: int, db: Session = Depends(get_db)
):
    existing_transaction = (
        db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    )
    if not existing_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    validate_transaction(transaction)
    for attr in ["amount", "category_id", "description", "type", "notes"]:
        setattr(existing_transaction, attr, getattr(transaction, attr))
    existing_transaction.created_at = (
        datetime.fromisoformat(transaction.createdAt)
        if transaction.createdAt
        else datetime.utcnow()
    )
    existing_transaction.date = datetime.fromisoformat(transaction.date)
    db.commit()
    db.refresh(existing_transaction)
    category_name = get_category_name(db, existing_transaction.category_id)
    return to_response(existing_transaction, category_name)


@router.get(
    "/transactions/{transaction_id}",
    tags=["transactions"],
    response_model=TransactionResponse,
    dependencies=[Depends(JWTBearer())],
)
async def get_transaction_by_id(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(TransactionModel).filter_by(id=transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    category_name = get_category_name(db, transaction.category_id)
    return to_response(transaction, category_name)


@router.delete(
    "/transactions/{transaction_id}",
    tags=["transactions"],
    dependencies=[Depends(JWTBearer())],
)
async def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = (
        db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}


@router.post(
    "/transactions/bulk", tags=["transactions"], dependencies=[Depends(JWTBearer())]
)
async def save_transactions(
    transactions_data: List[Transaction], db: Session = Depends(get_db)
):
    if not transactions_data:
        raise HTTPException(status_code=400, detail="No transactions provided")
    for transaction in transactions_data:
        validate_transaction(transaction)
        category = (
            db.query(Category).filter(Category.id == transaction.category_id).first()
        )
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"Category with ID {transaction.category_id} not found",
            )
        new_transaction = build_transaction_model(transaction)
        db.add(new_transaction)
    db.commit()
    return {"message": "Transactions saved successfully"}


@router.get(
    "/categories",
    response_model=dict[str, List[CategoryResponse]],
    dependencies=[Depends(JWTBearer())],
)
async def get_categories(db: Session = Depends(get_db)):
    income = db.query(Category).filter_by(type="income").all()
    expense = db.query(Category).filter_by(type="expense").all()
    return {"income": income, "expense": expense}
