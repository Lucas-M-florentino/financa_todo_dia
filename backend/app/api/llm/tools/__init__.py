# app/api/llm/tools/__init__.py
from .functions import (
    create_transaction,
    get_all_transactions,
    get_transactions_by_category,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
    bulk_create_transactions,
    get_categories,
    get_transactions_by_date_range,
    get_transactions_by_type,
    get_transactions_by_description,
)


FUNCTION_REGISTRY = {
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
    "get_transactions_by_description": get_transactions_by_description,
}


def get_function_by_name(name: str):
    return FUNCTION_REGISTRY.get(name)
