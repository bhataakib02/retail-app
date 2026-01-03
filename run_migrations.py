from sqlalchemy import create_engine, text
import os
import sys

# Read DATABASE_URL from environment (Supabase connection string)
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("ERROR: environment variable DATABASE_URL not set")
    sys.exit(1)

print("Using DATABASE_URL:", database_url.split("@", 1)[0] + "@...")

# Create engine for PostgreSQL
# Supabase uses SSL by default, so we enable SSL mode
engine = create_engine(database_url, connect_args={"sslmode": "require"})

# -------------------------------------------------------------------
# SQL to create tables (PostgreSQL syntax)
# -------------------------------------------------------------------
schema_sql = """
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(150),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  price DECIMAL(10,2),
  stock INTEGER DEFAULT 0,
  image VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  payment_method VARCHAR(50),
  payment_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS order_items (
  id SERIAL PRIMARY KEY,
  order_id INTEGER,
  product_id INTEGER,
  quantity INTEGER,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
"""

# -------------------------------------------------------------------
# Run migration by splitting the SQL and executing each statement.
# -------------------------------------------------------------------
try:
    statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
    with engine.begin() as conn:
        print("Running schema SQL...")
        for stmt in statements:
            if stmt:  # ensure each ends without trailing semicolon for safety
                conn.execute(text(stmt))
    print("✅ Tables created (or already existed).")
except Exception as e:
    print("ERROR running migration:", e)
    raise
