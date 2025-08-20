# backend/app/api/llm/tools/functions.py
from typing import List, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.data.models import Category, Transaction as TransactionModel
from app.api.models.models import Transaction, PutTransaction, BulkTransaction
from datetime import datetime
from langchain_core.tools import tool
import logging

# Logger configurado
logger = logging.getLogger(__name__)

# Variável global para armazenar a sessão do banco
_db_session: Session = None

def set_db_session(db: Session):
    """Define a sessão do banco de dados para as ferramentas"""
    global _db_session
    _db_session = db

def get_db_session() -> Session:
    """Obtém a sessão do banco de dados"""
    global _db_session
    if _db_session is None:
        raise RuntimeError("Sessão do banco de dados não foi definida. Chame set_db_session() primeiro.")
    return _db_session

# --- Funções de Ajuda ---
def _get_category_name(category_id: int) -> str:
    """Busca o nome da categoria pelo ID."""
    db = get_db_session()
    category = db.query(Category).filter(Category.id == category_id).first()
    return category.name if category else "Unknown"

def _to_response_format(transaction: TransactionModel) -> Dict:
    """Converte um objeto de transação em um dicionário para a resposta."""
    category_name = _get_category_name(transaction.category_id)
    return {
        "id": transaction.id,
        "amount": float(transaction.amount),  # Garante que é JSON serializável
        "type": transaction.type,
        "description": transaction.description,
        "date": transaction.date.isoformat(),
        "category_id": transaction.category_id,
        "category_name": category_name,
        "notes": transaction.notes if hasattr(transaction, 'notes') else None
    }

# --- Ferramentas LangChain ---

@tool
def create_transaction(amount: float, category_id: int, date: str, 
                      description: str, type: str, notes: str = None) -> dict:
    """Adiciona uma nova transação ao banco de dados.

    Args:
        amount: Valor da transação
        category_id: ID da categoria
        date: Data no formato YYYY-MM-DDTHH:MM:SS ou YYYY-MM-DD
        description: Descrição da transação
        type: Tipo da transação (income ou expense)
        notes: Notas adicionais (opcional)

    Returns:
        dict: Status da operação
    """
    try:
        db = get_db_session()
        
        # Parse da data
        if 'T' in date:
            parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        else:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        
        transaction_data = {
            "amount": amount,
            "category_id": category_id,
            "date": parsed_date,
            "description": description,
            "type": type,
            "notes": notes
        }
        
        transaction_model = TransactionModel(**transaction_data)
        db.add(transaction_model)
        db.commit()
        db.refresh(transaction_model)
        return {"status": "success", "message": f"Transação criada com sucesso com ID: {transaction_model.id}"}
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar transação: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_all_transactions() -> dict:
    """Obtém todas as transações do banco de dados e as agrupa por categoria.
    
    Returns:
        dict: Dicionário com as transações agrupadas
    """
    try:
        db = get_db_session()
        transactions = db.query(TransactionModel).all()
        categories = db.query(Category).all()
        
        # Agrupa por categoria
        categorized_transactions = {category.name: [] for category in categories}
        
        for transaction in transactions:
            category_name = _get_category_name(transaction.category_id)
            if category_name not in categorized_transactions:
                categorized_transactions[category_name] = []
            categorized_transactions[category_name].append(_to_response_format(transaction))
        
        return {"status": "success", "data": categorized_transactions}
    except Exception as e:
        logger.error(f"Erro ao obter todas as transações: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_transaction_by_id(transaction_id: int) -> dict:
    """Obtém uma transação específica pelo ID.

    Args:
        transaction_id: ID da transação

    Returns:
        dict: Detalhes da transação ou erro
    """
    try:
        db = get_db_session()
        transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
        if not transaction:
            return {"status": "error", "message": f"Transação com ID {transaction_id} não encontrada."}
        
        return {"status": "success", "data": _to_response_format(transaction)}
    except Exception as e:
        logger.error(f"Erro ao buscar transação por ID: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_top_spending_category(start_date: str, end_date: str) -> dict:
    """Retorna a categoria com o maior gasto total em um período de datas."""
    try:
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        db = get_db_session()
        result = db.query(
            Category.name,
            func.sum(TransactionModel.amount).label("total")
        ).join(TransactionModel, TransactionModel.category_id == Category.id
        ).filter(
            TransactionModel.type == "expense",
            TransactionModel.date >= start,
            TransactionModel.date <= end
        ).group_by(Category.name
        ).order_by(func.sum(TransactionModel.amount).desc()
        ).first()
        if not result:
            return {"status": "error", "message": "Nenhuma transação encontrada para o período especificado."}
        return {
            "status": "success",
            "data": {
                "category": result.name,
                "total": float(result.total)
            }
        }
    except Exception as e:
        logger.error(f"Erro ao buscar categoria com maior gasto: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def update_transaction(transaction_id: int, amount: float = None, 
                      category_id: int = None, date: str = None, 
                      description: str = None, type: str = None, 
                      notes: str = None) -> dict:
    """Atualiza uma transação existente com novos dados.

    Args:
        transaction_id: ID da transação a ser atualizada
        amount: Novo valor (opcional)
        category_id: Novo ID da categoria (opcional)
        date: Nova data (opcional)
        description: Nova descrição (opcional)
        type: Novo tipo (opcional)
        notes: Novas notas (opcional)

    Returns:
        dict: Status da operação
    """
    try:
        db = get_db_session()
        transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
        if not transaction:
            return {"status": "error", "message": f"Transação com ID {transaction_id} não encontrada."}
        
        # Atualiza apenas os campos fornecidos
        if amount is not None:
            transaction.amount = amount
        if category_id is not None:
            transaction.category_id = category_id
        if date is not None:
            if 'T' in date:
                transaction.date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            else:
                transaction.date = datetime.strptime(date, "%Y-%m-%d")
        if description is not None:
            transaction.description = description
        if type is not None:
            transaction.type = type
        if notes is not None:
            transaction.notes = notes
            
        db.commit()
        db.refresh(transaction)
        return {"status": "success", "message": f"Transação com ID {transaction_id} atualizada com sucesso."}
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar transação: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def delete_transaction(transaction_id: int) -> dict:
    """Deleta uma transação pelo ID.

    Args:
        transaction_id: ID da transação a ser excluída

    Returns:
        dict: Status da operação
    """
    try:
        db = get_db_session()
        transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
        if not transaction:
            return {"status": "error", "message": f"Transação com ID {transaction_id} não encontrada."}
        
        db.delete(transaction)
        db.commit()
        return {"status": "success", "message": f"Transação com ID {transaction_id} deletada com sucesso."}
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar transação: {str(e)}")
        return {"status": "error", "message": str(e)}

# @tool
# def bulk_create_transactions(transactions_data: list[dict]) -> dict:
#     """Cria várias transações de uma só vez.

#     Args:
#         transactions_data: Lista de dicionários com dados das transações

#     Returns:
#         dict: Status da operação e IDs criados
#     """
#     try:
#         db = get_db_session()
#         created_ids = []
#         bulk = BulkTransaction(transactions=[Transaction(**t) for t in transactions_data])
#         for data in bulk.transactions:
#             # Parse da data se necessário
#             if 'date' in data:
#                 if 'T' in data['date']:
#                     data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
#                 else:
#                     data['date'] = datetime.strptime(data['date'], "%Y-%m-%d")
            
#             transaction_model = TransactionModel(**data)
#             db.add(transaction_model)
#             db.flush()  # Flush para obter o ID sem commit
#             created_ids.append(transaction_model.id)
            
#         db.commit()
#         return {"status": "success", "message": "Transações criadas com sucesso.", "created_ids": created_ids}
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Erro ao criar transações em massa: {str(e)}")
#         return {"status": "error", "message": str(e)}

@tool
def get_categories() -> dict:
    """Obtém todas as categorias de transação disponíveis.
        
    Returns:
        dict: Lista de categorias com ID e nome
    """
    try:
        db = get_db_session()
        categories = db.query(Category).all()
        categories_data = [{"id": cat.id, "name": cat.name, "type": cat.type if hasattr(cat, 'type') else None} for cat in categories]
        return {"status": "success", "data": categories_data}
    except Exception as e:
        logger.error(f"Erro ao obter categorias: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_transactions_by_category(category_id: int, start_date: str = None, end_date: str = None) -> dict:
    """Obtém transações por categoria e opcionalmente por período.

    Args:
        category_id: ID da categoria
        start_date: Data inicial (opcional)
        end_date: Data final (opcional)

    Returns:
        dict: Lista de transações da categoria
    """
    try:
        db = get_db_session()
        query = db.query(TransactionModel).filter(TransactionModel.category_id == category_id)
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(TransactionModel.date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(TransactionModel.date <= end)
        
        transactions = query.all()
        result = [_to_response_format(t) for t in transactions]
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Erro ao buscar transações por categoria: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_transactions_by_date_range(start_date: str, end_date: str) -> dict:
    """Obtém transações dentro de um intervalo de datas.

    Args:
        start_date: Data de início no formato 'YYYY-MM-DD'
        end_date: Data de fim no formato 'YYYY-MM-DD'

    Returns:
        dict: Lista de transações encontradas
    """
    try:
        db = get_db_session()
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        transactions = db.query(TransactionModel).filter(
            TransactionModel.date >= start,
            TransactionModel.date <= end
        ).all()
        result = [_to_response_format(t) for t in transactions]
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Erro ao buscar transações por data: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_transactions_by_type(type: str) -> dict:
    """Obtém transações por tipo (ex: 'income', 'expense').

    Args:
        type: Tipo da transação ('income' ou 'expense')

    Returns:
        dict: Lista de transações encontradas
    """
    try:
        db = get_db_session()
        transactions = db.query(TransactionModel).filter(TransactionModel.type == type).all()
        result = [_to_response_format(t) for t in transactions]
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Erro ao buscar transações por tipo: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_transactions_by_description(description_keyword: str) -> dict:
    """Obtém transações por descrição, buscando por correspondências parciais (case-insensitive).

    Args:
        description_keyword: Palavra-chave para buscar na descrição

    Returns:
        dict: Lista de transações encontradas
    """
    try:
        db = get_db_session()
        transactions = db.query(TransactionModel).filter(
            TransactionModel.description.ilike(f"%{description_keyword}%")
        ).all()
        result = [_to_response_format(t) for t in transactions]
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Erro ao buscar transações por descrição: {str(e)}")
        return {"status": "error", "message": str(e)}

@tool
def get_transactions_by_type_and_date_range(transaction_type: str, start_date: str, end_date: str) -> dict:
    """Filtra transações por tipo e intervalo de datas.

    Args:
        transaction_type: Tipo da transação ('income' ou 'expense')
        start_date: Data de início no formato 'YYYY-MM-DD'
        end_date: Data de fim no formato 'YYYY-MM-DD'

    Returns:
        dict: Lista de transações encontradas
    """
    try:
        db = get_db_session()
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        transactions = db.query(TransactionModel).filter(
            TransactionModel.type == transaction_type,
            TransactionModel.date >= start,
            TransactionModel.date <= end
        ).all()
        result = [_to_response_format(t) for t in transactions]
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Erro ao buscar transações por tipo e data: {str(e)}")
        return {"status": "error", "message": str(e)}

# --- Ponto de Entrada para as Ferramentas ---

def get_tools():
    """Retorna uma lista de todas as ferramentas disponíveis para o agente."""
    return [
        create_transaction,
        get_all_transactions,
        get_transaction_by_id,
        get_top_spending_category,
        update_transaction,
        delete_transaction,
        # bulk_create_transactions,
        get_categories,
        get_transactions_by_category,
        get_transactions_by_date_range,
        get_transactions_by_type,
        get_transactions_by_description,
        get_transactions_by_type_and_date_range,
    ]