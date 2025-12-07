import os

# Database
DB_HOST = os.getenv('DB_HOST', 'database')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hacknation')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# LLM Provider: 'cloudflare' or 'ollama'
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')

# Cloudflare Workers AI
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID', '')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN', '')
CLOUDFLARE_MODEL_EN = os.getenv('CLOUDFLARE_MODEL_EN', '@cf/meta/llama-3.1-70b-instruct')
CLOUDFLARE_MODEL_PL = os.getenv('CLOUDFLARE_MODEL_PL', '@cf/meta/llama-3.1-70b-instruct')

# Ollama
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'host.docker.internal')
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:30b-a3b')

# Flask
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', '8080'))

