# Defina suas ferramentas para o Gemini
class Tools:

    _tools = [
        {
            "name": "create_transaction",
            "description": "Adiciona uma nova transação financeira, especificando valor, tipo (receita ou despesa), ID da categoria, descrição e data. A categoria deve ser um ID numérico. Se o usuário fornecer um nome de categoria, você DEVE primeiro chamar a ferramenta 'get_categories' para encontrar o 'category_id' correspondente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Valor da transação, e.g., 50.75",
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "ID numérico da categoria da transação (obrigatório).",
                    },
                    "date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Data da transação no formato YYYY-MM-DDTHH:MM:SS, e.g., '2025-07-29T10:00:00'. Para o dia atual, pode ser 'YYYY-MM-DD'. O Gemini tentará converter datas informadas para este formato.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Uma breve descrição da transação, e.g., 'Conta de luz' ou 'Salário de julho'.",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                        "description": "Tipo da transação: 'income' para receita ou 'expense' para despesa.",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notas adicionais sobre a transação (opcional).",
                    },
                },
                "required": ["amount", "category_id", "date", "description", "type"],
            },
        },
        {
            "name": "get_all_transactions",
            "description": "Recupera uma lista de todas as transações financeiras registradas sem filtros. Útil para ver o panorama completo.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_transaction_by_id",
            "description": "Recupera os detalhes de uma transação financeira específica usando seu ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "integer",
                        "description": "O ID numérico da transação a ser recuperada.",
                    },
                },
                "required": ["transaction_id"],
            },
        },
        {
            "name": "update_transaction",
            "description": "Atualiza os detalhes de uma transação financeira existente usando seu ID. Você pode atualizar o valor, ID da categoria, descrição, tipo, data ou notas. A categoria deve ser um ID numérico. Se o usuário fornecer um nome de categoria, você DEVE primeiro chamar a ferramenta 'get_categories' para encontrar o 'category_id' correspondente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "integer",
                        "description": "O ID numérico da transação a ser atualizada.",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Novo valor da transação (opcional).",
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "Novo ID numérico da categoria da transação (opcional).",
                    },
                    "date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Nova data da transação no formato YYYY-MM-DDTHH:MM:SS (opcional).",
                    },
                    "description": {
                        "type": "string",
                        "description": "Nova descrição da transação (opcional).",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                        "description": "Novo tipo da transação ('income' ou 'expense') (opcional).",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Novas notas adicionais sobre a transação (opcional).",
                    },
                },
                "required": ["transaction_id"],
            },
        },
        {
            "name": "delete_transaction",
            "description": "Deleta uma transação financeira do registro usando seu ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "integer",
                        "description": "O ID numérico da transação a ser deletada.",
                    },
                },
                "required": ["transaction_id"],
            },
        },
        {
            "name": "bulk_create_transactions",
            "description": "Adiciona múltiplas transações financeiras de uma vez. Cada transação deve incluir valor, tipo, ID da categoria, descrição e data. Use quando houver várias transações a serem adicionadas simultaneamente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transactions_data": {
                        "type": "array",
                        "description": "Uma lista de objetos de transação a serem criados.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number"},
                                "category_id": {"type": "integer"},
                                "date": {
                                    "type": "string",
                                    "format": "date-time",
                                    "description": "Data da transação no formato YYYY-MM-DDTHH:MM:SS",
                                },
                                "description": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": ["income", "expense"],
                                },
                                "notes": {"type": "string"},
                            },
                            "required": [
                                "amount",
                                "category_id",
                                "date",
                                "description",
                                "type",
                            ],
                        },
                    },
                },
                "required": ["transactions_data"],
            },
        },
        {
            "name": "get_categories",
            "description": "Recupera uma lista de todas as categorias de transações disponíveis, separadas por tipo (receita ou despesa). Útil para encontrar o 'category_id' com base no nome da categoria ou para listar as categorias disponíveis para o usuário.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        # --- NOVAS FUNÇÕES DE LEITURA ---
        {
            "name": "get_transactions_by_category",
            "description": "Retorna transações filtradas por uma categoria específica e, opcionalmente, por um período de datas. Se o usuário fornecer um nome de categoria, você DEVE primeiro chamar a ferramenta 'get_categories' para encontrar o 'category_id' correspondente antes de chamar esta ferramenta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {
                        "type": "integer",
                        "description": "ID numérico da categoria para filtrar as transações.",
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Data inicial para o filtro no formato YYYY-MM-DD (opcional).",
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Data final para o filtro no formato YYYY-MM-DD (opcional).",
                    },
                },
                "required": [
                    "category_id"
                ],  
            },
        },
        {
            "name": "get_transactions_by_date_range",
            "description": "Recupera transações dentro de um intervalo de datas especificado (início e fim).",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Data de início do período no formato YYYY-MM-DD (obrigatório).",
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Data de fim do período no formato YYYY-MM-DD (obrigatório).",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
        {
            "name": "get_transactions_by_type",
            "description": "Retorna transações filtradas por tipo (receita ou despesa).",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                        "description": "Tipo de transação para filtrar ('income' ou 'expense').",
                    },
                },
                "required": ["type"],
            },
        },
        {
            "name": "get_transactions_by_description",
            "description": "Busca transações cuja descrição contenha um texto específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description_keyword": {
                        "type": "string",
                        "description": "Palavra-chave ou frase para buscar na descrição da transação.",
                    },
                },
                "required": ["description_keyword"],
            },
        },
    ]

    @classmethod
    def get_tools(cls):
        """Retorna a lista de ferramentas disponíveis."""
        return cls._tools

    @classmethod
    def get_tool_by_name(cls, name):
        """Retorna uma ferramenta pelo nome."""
        return next((tool for tool in cls._tools if tool["name"] == name), None)

    @classmethod
    def add_tool(cls, tool):
        """Adiciona uma nova ferramenta à lista."""
        if not isinstance(tool, dict) or "name" not in tool:
            raise ValueError(
                "Tool deve ser um dicionário com pelo menos a chave 'name'."
            )
        if cls.get_tool_by_name(tool["name"]):
            raise ValueError(f"Tool '{tool['name']}' já existe.")
        cls._tools.append(tool)

    @classmethod
    def get_tools(cls):
        return cls._tools
