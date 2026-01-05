import psycopg2
from werkzeug.security import generate_password_hash

DB_HOST = "catedge-db.cxgwqaw8y8rv.ap-southeast-2.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "skdn1418"
DB_PORT = "5432"

try:
    # Connect to cloud database
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    cursor = conn.cursor()

    # Create users table if not exists
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
    print("✅ Users table created or exists!")

    # Create admin user if not exists
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
    print("🎉 Login module ready on AWS RDS!")

except Exception as e:
    print(f"❌ Error: {e}")
