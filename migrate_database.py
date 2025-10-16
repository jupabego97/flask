"""
Script para migrar datos de Supabase a Neon PostgreSQL con seguridad
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

# Credenciales de las bases de datos
SUPABASE_URL = "postgresql://postgres.hdjpdhnmmbjskttucvlx:90tZPmctuBEnRK4Y@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
NEON_URL = "postgresql://neondb_owner:npg_c48DVpgJWZQT@ep-odd-breeze-adieoy6s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def log(message):
    """Log con timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def connect_db(url, name):
    """Conectar a base de datos con manejo de errores"""
    try:
        log(f"🔌 Conectando a {name}...")
        conn = psycopg2.connect(url)
        log(f"✅ Conectado a {name}")
        return conn
    except Exception as e:
        log(f"❌ Error conectando a {name}: {e}")
        sys.exit(1)

def get_table_structure(cursor, table_name):
    """Obtener estructura de la tabla"""
    cursor.execute(f"""
        SELECT column_name, data_type, character_maximum_length, 
               column_default, is_nullable
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;
    """)
    return cursor.fetchall()

def get_table_data(cursor, table_name):
    """Obtener todos los datos de la tabla"""
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id;")
    return cursor.fetchall()

def create_table_if_not_exists(cursor, table_name):
    """Crear tabla repair_cards en Neon si no existe"""
    log(f"📋 Creando tabla {table_name} en Neon si no existe...")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS repair_cards (
        id SERIAL PRIMARY KEY,
        owner_name TEXT NOT NULL,
        whatsapp_number TEXT NOT NULL,
        problem TEXT NOT NULL,
        status TEXT NOT NULL,
        start_date TIMESTAMP NOT NULL,
        due_date TIMESTAMP NOT NULL,
        image_url TEXT,
        has_charger TEXT,
        ingresado_date TIMESTAMP NOT NULL,
        diagnosticada_date TIMESTAMP,
        para_entregar_date TIMESTAMP,
        entregados_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cursor.execute(create_table_sql)
    log(f"✅ Tabla {table_name} verificada/creada")

def create_indexes(cursor):
    """Crear índices para mejorar performance"""
    log("📊 Creando índices para optimización...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_repair_cards_owner_name ON repair_cards(owner_name);",
        "CREATE INDEX IF NOT EXISTS idx_repair_cards_whatsapp ON repair_cards(whatsapp_number);",
        "CREATE INDEX IF NOT EXISTS idx_repair_cards_status ON repair_cards(status);",
        "CREATE INDEX IF NOT EXISTS idx_repair_cards_start_date ON repair_cards(start_date);",
        "CREATE INDEX IF NOT EXISTS idx_repair_cards_due_date ON repair_cards(due_date);",
    ]
    
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            log(f"✅ Índice creado: {idx_sql.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            log(f"⚠️ Error creando índice: {e}")

def migrate_data():
    """Función principal de migración"""
    log("🚀 Iniciando migración de Supabase a Neon PostgreSQL")
    log("=" * 60)
    
    # Conectar a Supabase
    supabase_conn = connect_db(SUPABASE_URL, "Supabase")
    supabase_cursor = supabase_conn.cursor(cursor_factory=RealDictCursor)
    
    # Conectar a Neon
    neon_conn = connect_db(NEON_URL, "Neon")
    neon_cursor = neon_conn.cursor()
    
    try:
        # Verificar si la tabla existe en Supabase
        log("🔍 Verificando tabla repair_cards en Supabase...")
        supabase_cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'repair_cards'
            );
        """)
        result = supabase_cursor.fetchone()
        table_exists = result['exists'] if result else False
        
        if not table_exists:
            log("⚠️ Tabla repair_cards no existe en Supabase")
            log("📋 Creando tabla vacía en Neon...")
            create_table_if_not_exists(neon_cursor, 'repair_cards')
            create_indexes(neon_cursor)
            neon_conn.commit()
            log("✅ Migración completada (tabla vacía)")
            return
        
        # Obtener estructura de la tabla
        log("📋 Obteniendo estructura de tabla...")
        structure = get_table_structure(supabase_cursor, 'repair_cards')
        log(f"✅ Estructura obtenida: {len(structure)} columnas")
        
        # Obtener datos
        log("📦 Obteniendo datos de Supabase...")
        data = get_table_data(supabase_cursor, 'repair_cards')
        log(f"✅ Se encontraron {len(data)} registros")
        
        if len(data) == 0:
            log("⚠️ No hay datos para migrar")
            create_table_if_not_exists(neon_cursor, 'repair_cards')
            create_indexes(neon_cursor)
            neon_conn.commit()
            log("✅ Migración completada (sin datos)")
            return
        
        # Crear tabla en Neon
        create_table_if_not_exists(neon_cursor, 'repair_cards')
        
        # Limpiar datos existentes en Neon (opcional, comentar si quieres mantener datos)
        log("🧹 Limpiando datos existentes en Neon...")
        neon_cursor.execute("DELETE FROM repair_cards;")
        log("✅ Datos limpiados")
        
        # Insertar datos
        log(f"📥 Insertando {len(data)} registros en Neon...")
        
        insert_sql = """
        INSERT INTO repair_cards (
            owner_name, whatsapp_number, problem, status, 
            start_date, due_date, image_url, has_charger,
            ingresado_date, diagnosticada_date, 
            para_entregar_date, entregados_date
        ) VALUES (
            %(owner_name)s, %(whatsapp_number)s, %(problem)s, %(status)s,
            %(start_date)s, %(due_date)s, %(image_url)s, %(has_charger)s,
            %(ingresado_date)s, %(diagnosticada_date)s,
            %(para_entregar_date)s, %(entregados_date)s
        );
        """
        
        inserted = 0
        for row in data:
            try:
                neon_cursor.execute(insert_sql, row)
                inserted += 1
                if inserted % 10 == 0:
                    log(f"   📝 Insertados {inserted}/{len(data)} registros...")
            except Exception as e:
                log(f"⚠️ Error insertando registro {row.get('id', '?')}: {e}")
        
        log(f"✅ Se insertaron {inserted} registros exitosamente")
        
        # Crear índices
        create_indexes(neon_cursor)
        
        # Resetear secuencia de ID
        log("🔢 Ajustando secuencia de IDs...")
        neon_cursor.execute("""
            SELECT setval('repair_cards_id_seq', 
                         (SELECT MAX(id) FROM repair_cards));
        """)
        log("✅ Secuencia ajustada")
        
        # Commit
        log("💾 Guardando cambios...")
        neon_conn.commit()
        log("✅ Cambios guardados")
        
        # Verificar migración
        log("🔍 Verificando migración...")
        neon_cursor.execute("SELECT COUNT(*) FROM repair_cards;")
        count = neon_cursor.fetchone()[0]
        log(f"✅ Registros en Neon: {count}")
        
        if count == len(data):
            log("🎉 ¡Migración completada exitosamente!")
        else:
            log(f"⚠️ Advertencia: Se esperaban {len(data)} registros pero hay {count}")
        
    except Exception as e:
        log(f"❌ Error durante migración: {e}")
        neon_conn.rollback()
        raise
    
    finally:
        # Cerrar conexiones
        log("🔌 Cerrando conexiones...")
        supabase_cursor.close()
        supabase_conn.close()
        neon_cursor.close()
        neon_conn.close()
        log("✅ Conexiones cerradas")
    
    log("=" * 60)
    log("✨ Proceso de migración finalizado")

if __name__ == "__main__":
    try:
        migrate_data()
    except KeyboardInterrupt:
        log("\n⚠️ Migración cancelada por usuario")
        sys.exit(1)
    except Exception as e:
        log(f"\n❌ Error fatal: {e}")
        sys.exit(1)

