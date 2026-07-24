#!/usr/bin/env bash
# Script de build usado pelo Render (definido em render.yaml -> buildCommand).
# Instala as dependências e aplica as migrações do banco de dados a cada deploy,
# de forma automática — sem precisar de SSH nem de comandos manuais.
set -o errexit

pip install -r requirements.txt

export FLASK_APP=wsgi.py
flask db upgrade
