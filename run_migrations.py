from sqlalchemy import create_engine, text
import os
import sys
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Read DATABASE_URL from environment
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("ERROR: environment variable DATABASE_URL not set")
    sys.exit(1)

print("Using DATABASE_URL:", database_url.split("@", 1)[0] + "@...")

# -------------------------------------------------------------------
# Remove ssl-mode from the URL query (PyMySQL doesn't accept it)
# and enable TLS for PyMySQL via connect_args.
# -------------------------------------------------------------------
parts = urlsplit(database_url)
qs = dict(parse_qsl(parts.query))
qs.pop("ssl-mode", None)  # remove if present
parts = parts._replace(query=urlencode(qs))
database_url = urlunsplit(parts)

connect_args = {"connect_timeout": 10, "ssl": {}}
engine = create_engine(database_url, connect_args=connect_args)

# -------------------------------------------------------------------
# SQL to create tables (idempotent)
# Note: we will split by ';' and execute each statement separately.
# -------------------------------------------------------------------
schema_sql = """
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  role VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  price DECIMAL(10,2),
  stock INT DEFAULT 0,
  image VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  payment_method VARCHAR(50),
  payment_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  product_id INT,
  quantity INT
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
            # ensure each ends without trailing semicolon for safety
            conn.execute(text(stmt))
    print("✅ Tables created (or already existed).")
except Exception as e:
    print("ERROR running migration:", e)
    raise
