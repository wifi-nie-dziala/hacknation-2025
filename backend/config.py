import os

DB_HOST = os.getenv('DB_HOST', 'database')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hacknation')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

LLM_EN_HOST = os.getenv('LLM_EN_HOST', 'llm-en')
LLM_EN_PORT = os.getenv('LLM_EN_PORT', '11434')
LLM_PL_HOST = os.getenv('LLM_PL_HOST', 'llm-pl')
LLM_PL_PORT = os.getenv('LLM_PL_PORT', '11434')

FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', '8080'))

