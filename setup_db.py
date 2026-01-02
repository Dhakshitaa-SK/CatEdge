import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash

DB_HOST = "localhost"
DB_NAME = "catedge_db"
DB_USER = "postgres"
DB_PASSWORD = "skdn1418"
DB_PORT = "5432"

try:
    # Create database
    conn = psycopg2.connect(host=DB_HOST, database="postgres", user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}';")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"✅ Database '{DB_NAME}' created!")
    cursor.close()
    conn.close()

    # Connect to catedge_db and create users table
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(120) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('student', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    print("✅ Users table created!")

    # Create admin user
    cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@gmail.com',))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            ('admin@gmail.com', generate_password_hash('admin123', method='pbkdf2:sha256'), 'admin')
        )
        conn.commit()
        print("✅ Admin created: admin@gmail.com / admin123")

    cursor.close()
    conn.close()
    print("🎉 Login module ready!")

except Exception as e:
    print(f"❌ Error: {e}")
