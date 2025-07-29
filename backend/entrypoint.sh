#!/bin/bash

echo "Executando migrações..."
alembic upgrade head

echo "Inserindo categorias..."
PYTHONPATH=. python app/data/seed.py

echo "Iniciando servidor..."
exec "$@"
