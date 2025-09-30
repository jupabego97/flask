"""
Arreglar la secuencia de IDs en PostgreSQL
"""
import os
from dotenv import load_dotenv
import psycopg2

# Cargar variables de entorno
load_dotenv()

# Leer URL de Supabase del .env
SUPABASE_URL = None
try:
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL='):
                SUPABASE_URL = line.split('=', 1)[1]
                break
except:
    pass

def fix_sequence():
    """Ajustar la secuencia para que no haya conflictos de ID"""
    if not SUPABASE_URL:
        print("❌ No se encontró DATABASE_URL")
        return

    conn = psycopg2.connect(SUPABASE_URL)
    cur = conn.cursor()

    try:
        # Obtener el máximo ID actual
        cur.execute("SELECT MAX(id) FROM repair_cards")
        max_id = cur.fetchone()[0] or 0

        # Actualizar la secuencia para que empiece después del máximo ID
        next_id = max_id + 1
        cur.execute(f"ALTER SEQUENCE repair_cards_id_seq RESTART WITH {next_id}")
        conn.commit()

        print(f"✅ Secuencia ajustada. Próximo ID: {next_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    fix_sequence()

