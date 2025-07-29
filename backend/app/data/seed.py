from sqlalchemy.orm import Session
from app.data.database import SessionLocal
from app.data.models import Category

# Dados padrão para categorias
default_categories = {
    "income": ["Salário", "Freelance", "Investimentos", "Outros"],
    "expense": ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Educação", "Contas", "Mercearia", "Outros"]
}

def seed_categories(db: Session):
    for tipo, nomes in default_categories.items():
        for nome in nomes:
            # Verifica se a categoria já existe
            exists = db.query(Category).filter_by(name=nome, type=tipo).first()
            if not exists:
                categoria = Category(name=nome, type=tipo)
                db.add(categoria)
    db.commit()

def main():
    db = SessionLocal()
    try:
        seed_categories(db)
        print("Categorias inseridas com sucesso.")
    except Exception as e:
        print("Erro ao inserir categorias:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
