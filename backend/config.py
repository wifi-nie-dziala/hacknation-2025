import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_HOST = os.getenv('DB_HOST', 'database')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hacknation')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Cloudflare Workers AI
USE_CLOUDFLARE_AI = os.getenv('USE_CLOUDFLARE_AI', 'false').lower() == 'true'
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID', '')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN', '')
CLOUDFLARE_MODEL_EN = os.getenv('CLOUDFLARE_MODEL_EN', '@cf/meta/llama-3.1-70b-instruct')
CLOUDFLARE_MODEL_PL = os.getenv('CLOUDFLARE_MODEL_PL', '@cf/meta/llama-3.1-70b-instruct')

# Legacy Ollama
LLM_EN_HOST = os.getenv('LLM_EN_HOST', 'llm-en')
LLM_EN_PORT = os.getenv('LLM_EN_PORT', '11434')
LLM_PL_HOST = os.getenv('LLM_PL_HOST', 'llm-pl')
LLM_PL_PORT = os.getenv('LLM_PL_PORT', '11434')

# Flask
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', '8080'))

