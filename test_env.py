import os
from dotenv import load_dotenv
import pathlib

env_path = pathlib.Path('.') / '.env'
print(f"Buscando .env en: {env_path.absolute()}")
print(f"Existe: {env_path.exists()}")

load_dotenv(dotenv_path=env_path, override=True)

db_url = os.getenv('DATABASE_URL', 'NOT_FOUND')
print(f"\nDATABASE_URL = {db_url[:80] if db_url != 'NOT_FOUND' else 'NOT_FOUND'}")
print(f"GEMINI_API_KEY = {os.getenv('GEMINI_API_KEY', 'NOT_FOUND')[:20]}...")

