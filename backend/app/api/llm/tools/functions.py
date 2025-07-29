# app/api/llm/tools/functions.py
from asyncio.log import logger
from sqlalchemy.orm import Session

from app.data.dependencies import get_db
from app.data.models import Category, Transaction as TransactionModel
from app.api.routes import build_transaction_model, to_response, update_transaction, get_transactions, get_categories, get_category_name, create_transaction, get_transaction_by_id

def create_transaction(transaction) -> dict:
    """
    Função para adicionar uma transação ao banco de dados.
    :param amount: Valor da transação.
    :param category: Categoria da transação.
    :param db: Sessão do banco de dados.
    :return: Dicionário com o status da operação.
    """
    try:
        # Lógica para adicionar transação
        db = next(get_db())
        transaction_model = build_transaction_model(transaction)
        db.add(transaction_model)
        db.commit()
        db.refresh(transaction_model)
        return {"status": "success", "transaction_id": transaction_model.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_transactions() -> dict:
    """
    Função para obter todas as transações.
    :param db: Sessão do banco de dados.
    :return: Dicionário com todas as transações.
    """
    try:
        db = next(get_db())
        transactions = get_transactions(db)
        categories = get_categories(db)
        categorized_transactions = {category.name: [] for category in categories}
        
        for transaction in transactions:
            category_name = get_category_name(db, transaction.category_id)
            categorized_transactions[category_name].append(transaction)
        
        return {"status": "success", "data": categorized_transactions}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_transactions_by_category() -> dict:
    """
    Função para obter transações por categoria.
    :param category: Nome da categoria.
    :param db: Sessão do banco de dados.
    :return
: Dicionário com as transações da categoria.
    """
    try:
        db = next(get_db())
        transactions = get_transactions(db)
        categories = get_categories(db)
        categorized_transactions = {category.name: [] for category in categories}
        
        for transaction in transactions:
            category_name = get_category_name(db, transaction.category_id)
            categorized_transactions[category_name].append(transaction)
        
        return {"status": "success", "data": categorized_transactions}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_transaction_by_id(transaction_id: int) -> dict:
    """    Função para obter uma transação pelo ID.
    :param transaction_id: ID da transação.
    :param db: Sessão do banco de dados.
    :return: Dicionário com os detalhes da transação.
    """
    try:
        db = next(get_db())
        transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
        if not transaction:
            return {"status": "error", "message": "Transaction not found"}
        
        category_name = get_category_name(db, transaction.category_id)
        return {"status": "success", "data": to_response(transaction, category_name)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_transaction(transaction_id: int, transaction_data) -> dict:
    """
    Função para atualizar uma transação existente.
    :param transaction_id: ID da transação a ser atualizada.
    :param transaction_data: Dados atualizados da transação.
    :param db: Sessão do banco de dados.
    :return: Dicionário com o status da operação.
    """
    try:
        db = next(get_db())
        transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
        if not transaction:
            return {"status": "error", "message": "Transaction not found"}
        
        updated_transaction = build_transaction_model(transaction_data)
        for key, value in updated_transaction.__dict__.items():
            setattr(transaction, key, value)
        
        db.commit()
        return {"status": "success", "transaction_id": transaction.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_transaction(transaction_id: int) -> dict:
    """
    Função para deletar uma transação pelo ID.
    :param transaction_id: ID da transação a ser deletada.
    :param db: Sessão do banco de dados.
    :return: Dicionário com o status da operação.
    """
    try:
        db = next(get_db())
        transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
        if not transaction:
            return {"status": "error", "message": "Transaction not found"}
        
        db.delete(transaction)
        db.commit()
        return {"status": "success", "message": "Transaction deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}    

def bulk_create_transactions(transactions: list) -> dict:
    """
    Função para criar várias transações de uma vez.
    :param transactions: Lista de dicionários representando transações.
    :param db: Sessão do banco de dados.
    :return: Dicionário com o status da operação.
    """
    try:
        db = next(get_db())
        created_transactions = []
        for transaction in transactions:
            transaction_model = build_transaction_model(transaction)
            db.add(transaction_model)
            db.commit()
            db.refresh(transaction_model)
            created_transactions.append({"id": transaction_model.id, "status": "created"})
        
        return {"status": "success", "transactions": created_transactions}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_categories() -> dict:
    """
    Função para obter todas as categorias.
    :param db: Sessão do banco de dados.
    :return: Dicionário com todas as categorias.
    """
    try:
        db = next(get_db())
        categories = db.query(Category).all()
        return {"status": "success", "data": [category.name for category in categories]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_transactions_by_date_range(start_date: str, end_date: str) -> dict:
    """    Função para obter transações dentro de um intervalo de datas especificado.
    :param start_date: Data de início no formato 'YYYY-MM-DD'.
    :param end_date: Data de fim no formato 'YYYY-MM-DD'.
    :param db: Sessão do banco de dados.
    :return: Dicionário com as transações dentro do intervalo de datas.
    """
    try:
        db = next(get_db())
        transactions = db.query(TransactionModel).filter(
            TransactionModel.date >= start_date,
            TransactionModel.date <= end_date
        ).all()
        
        return {"status": "success", "data": [to_response(transaction) for transaction in transactions]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_transactions_by_type(transaction_type: str) -> dict:
    """    Função para obter transações por tipo (ex: 'income', 'expense').
    :param transaction_type: Tipo de transação.
    :param db: Sessão do banco de dados.
    :return: Dicionário com as transações do tipo especificado.
    """
    try:
        db = next(get_db())
        transactions = db.query(TransactionModel).filter(TransactionModel.type == transaction_type).all()
        
        return {"status": "success", "data": [to_response(transaction) for transaction in transactions]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_transactions_by_description(description: str) -> dict:
    """    Função para obter transações por descrição.
    :param description: Descrição da transação.
    :param db: Sessão do banco de dados.
    :return: Dicionário com as transações que contêm a descrição especificada.
    """
    try:
        db = next(get_db())
        transactions = db.query(TransactionModel).filter(TransactionModel.description.ilike(f"%{description}%")).all()
        
        return {"status": "success", "data": [to_response(transaction) for transaction in transactions]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_function_by_name(function_name: str):
    """
    Obtém a função de ferramenta pelo nome.
    :param function_name: Nome da função.
    :return: Função correspondente ou None se não encontrada.
    """
    tools = {
        "add_transaction": create_transaction,
        "get_all_transactions": get_all_transactions,
        "get_transactions_by_category": get_transactions_by_category,
        "get_transaction_by_id": get_transaction_by_id,
        "update_transaction": update_transaction,
        "delete_transaction": delete_transaction,
        "bulk_create_transactions": bulk_create_transactions,
        "get_categories": get_categories,
        "get_transactions_by_date_range": get_transactions_by_date_range,
        "get_transactions_by_type": get_transactions_by_type,
        "get_transactions_by_description": get_transactions_by_description
    }
    return tools.get(function_name, None)

