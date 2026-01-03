# app.py - Updated for Supabase (PostgreSQL)
import os
from flask import (
    Flask, g, render_template, request, redirect, session, url_for,
    flash, jsonify
)
from werkzeug.utils import secure_filename

# SQLAlchemy for database connection
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine
from sqlalchemy.engine import make_url
from urllib.parse import urlparse, quote_plus
import psycopg2
from psycopg2.extras import RealDictCursor

# create app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_me_in_prod")

# -------------------- DATABASE / SQLALCHEMY CONFIG --------------------
# Priority: use DATABASE_URL (Supabase connection string)
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASS = os.environ.get("DB_PASS", "")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "retail_db")
    # URL encode password to handle special characters
    encoded_password = quote_plus(DB_PASS)
    database_url = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configure Flask-SQLAlchemy for PostgreSQL/Supabase
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"sslmode": "require"} if "supabase.co" in database_url else {}
}

# init SQLAlchemy
db = SQLAlchemy(app)

# -------------------- PostgreSQL compatibility layer --------------------
def get_db_conn():
    """
    Return a psycopg2 connection for raw SQL queries.
    Reads DB connection info from DATABASE_URL environment variable.
    Uses the connection string directly for psycopg2 (it handles URL parsing internally).
    """
    try:
        # psycopg2 can accept connection strings directly, which handles URL encoding automatically
        conn = psycopg2.connect(database_url, sslmode="require" if "supabase.co" in database_url else "prefer")
        return conn
    except Exception as e:
        # Fallback: try parsing the URL manually if direct connection fails
        try:
            url_obj = make_url(database_url)
            conn = psycopg2.connect(
                host=url_obj.host or "localhost",
                port=url_obj.port or 5432,
                user=url_obj.username or "postgres",
                password=url_obj.password or "",
                database=url_obj.database or "postgres",
                sslmode="require" if "supabase.co" in database_url else "prefer"
            )
            return conn
        except Exception:
            # Last resort: use environment variables
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", 5432)),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASS", ""),
                database=os.environ.get("DB_NAME", "retail_db"),
                sslmode="require" if os.environ.get("DATABASE_URL", "").find("supabase.co") != -1 else "prefer"
            )
            return conn

def get_request_conn():
    if not hasattr(g, "db_conn"):
        g.db_conn = get_db_conn()
    return g.db_conn

@app.teardown_appcontext
def close_request_conn(exception=None):
    conn = g.pop("db_conn", None)
    try:
        if conn:
            conn.close()
    except Exception:
        pass

class PostgreSQLCompat:
    """Compatibility object so existing code using `mysql.connection.cursor()` keeps working."""
    @property
    def connection(self):
        return get_request_conn()
    
    def cursor(self, cursor_factory=None):
        """Return a cursor. Use RealDictCursor for dict-like results (like MySQLdb.cursors.DictCursor)"""
        conn = self.connection
        if cursor_factory == RealDictCursor:
            return conn.cursor(cursor_factory=RealDictCursor)
        return conn.cursor()

# instantiate compatibility object
mysql = PostgreSQLCompat()  # Keep the name 'mysql' for compatibility with existing code

# -------------------- File upload helper --------------------
UPLOAD_FOLDER = 'static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------- Simple health endpoint --------------------
@app.route("/_health")
def _health():
    return {"status": "ok"}, 200

# -------------------- ROUTES (auth / dashboards / products / cart / orders) --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            session['is_admin'] = 1 if session['role'] == 'admin' else 0
            return redirect(url_for('admin_dashboard') if session['role'] == 'admin' else url_for('user_dashboard'))
        flash("Incorrect email or password.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# Dashboards
@app.route('/user')
def user_dashboard():
    if session.get('loggedin') and session.get('role') == 'user':
        cur = mysql.connection.cursor(RealDictCursor)
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        cur.close()
        return render_template('user_dashboard.html', username=session['username'], products=products)
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor(RealDictCursor)
        cur.execute("SELECT COUNT(*) AS total_users FROM users WHERE role='user'")
        users = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS total_products FROM products")
        products = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS total_orders FROM orders")
        orders = cur.fetchone()
        cur.execute("SELECT * FROM products")
        all_products = cur.fetchall()
        cur.close()
        return render_template('admin_dashboard.html', users=users, products=products, orders=orders, all_products=all_products)
    return redirect(url_for('login'))

# Products
@app.route('/products')
def view_products():
    cur = mysql.connection.cursor(RealDictCursor)
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if session.get('loggedin') and session.get('role') == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            stock = request.form['stock']
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO products (name, description, price, stock, image) VALUES (%s, %s, %s, %s, %s)",
                            (name, description, price, stock, filename))
                mysql.connection.commit()
                cur.close()
                flash("Product added successfully.", "success")
                return redirect(url_for('admin_products'))
            flash("Invalid image file.", "danger")
        return render_template('add_product.html')
    return redirect(url_for('login'))

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor(RealDictCursor)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            stock = request.form['stock']
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cur.execute("UPDATE products SET name=%s, description=%s, price=%s, stock=%s, image=%s WHERE id=%s",
                            (name, description, price, stock, filename, product_id))
            else:
                cur.execute("UPDATE products SET name=%s, description=%s, price=%s, stock=%s WHERE id=%s",
                            (name, description, price, stock, product_id))
            mysql.connection.commit()
            cur.close()
            flash("Product updated successfully.", "success")
            return redirect(url_for('admin_products'))
        cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = cur.fetchone()
        cur.close()
        return render_template('edit_product.html', product=product)
    return redirect(url_for('login'))

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        mysql.connection.commit()
        cur.close()
        flash("Product deleted successfully.", "danger")
        return redirect(url_for('admin_products'))
    return redirect(url_for('login'))

@app.route('/admin_products')
def admin_products():
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor(RealDictCursor)
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        cur.close()
        return render_template('admin_products.html', products=products)
    return redirect(url_for('login'))

# Cart & orders
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash("Product added to cart.", "success")
    return redirect(url_for('view_products'))

@app.route('/ajax/add_to_cart', methods=['POST'])
def ajax_add_to_cart():
    if not session.get('loggedin') or session.get('role') != 'user':
        return jsonify({'status': 'error', 'message': 'Login required'})
    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart
    return jsonify({'status': 'success', 'message': 'Product added to cart'})

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    product_ids = [int(pid) for pid in cart.keys()]
    cur = mysql.connection.cursor(RealDictCursor)
    products = []
    if product_ids:
        placeholders = ','.join(['%s'] * len(product_ids))
        cur.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", product_ids)
        products = cur.fetchall()
    cur.close()
    return render_template('cart.html', cart=cart, products=products)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('loggedin') or session.get('role') != 'user':
        return redirect(url_for('login'))
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('view_cart'))
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        cur = mysql.connection.cursor()
        # PostgreSQL uses RETURNING clause to get the inserted id (no lastrowid)
        cur.execute("INSERT INTO orders (user_id, payment_method, payment_status) VALUES (%s, %s, %s) RETURNING id",
                    (session['id'], payment_method, 'Completed'))
        order_id = cur.fetchone()[0]
        for pid, qty in cart.items():
            cur.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (order_id, pid, qty))
            cur.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (qty, pid))
        mysql.connection.commit()
        cur.close()
        session.pop('cart', None)
        flash("Order placed successfully!", "success")
        return redirect(url_for('order_success', order_id=order_id))
    return render_template('checkout.html')

@app.route('/order_success/<int:order_id>')
def order_success(order_id):
    return render_template('order_success.html', order_id=order_id)

@app.route('/orders')
def user_orders():
    if session.get('loggedin') and session.get('role') == 'user':
        cur = mysql.connection.cursor(RealDictCursor)
        cur.execute("SELECT * FROM orders WHERE user_id = %s", (session['id'],))
        orders = cur.fetchall()
        cur.close()
        return render_template('orders.html', orders=orders)
    return redirect(url_for('login'))

@app.route('/admin/orders')
def admin_orders():
    if 'id' in session and session['role'] == 'admin':
        cur = mysql.connection.cursor(RealDictCursor)
        cur.execute("""
            SELECT 
                o.id AS order_id,
                u.email AS user_email,
                o.order_date,
                o.payment_method,
                o.payment_status,
                p.name AS product_name,
                oi.quantity,
                p.price,
                (p.price * oi.quantity) AS line_total
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            ORDER BY o.id DESC
        """)
        raw_orders = cur.fetchall()
        cur.close()

        orders = {}
        for row in raw_orders:
            oid = row['order_id']
            if oid not in orders:
                orders[oid] = {
                    'order_id': oid,
                    'user_email': row['user_email'],
                    'order_date': row['order_date'],
                    'payment_method': row['payment_method'],
                    'payment_status': row['payment_status'],
                    'products': [],
                    'grand_total': 0
                }
            orders[oid]['products'].append({
                'product_name': row['product_name'],
                'quantity': row['quantity'],
                'price': row['price'],
                'line_total': row['line_total']
            })
            orders[oid]['grand_total'] += row['line_total']

        return render_template('admin_orders.html', orders=orders.values())

    return redirect(url_for('login'))

@app.route('/invoice/<int:order_id>')
def invoice(order_id):
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(RealDictCursor)
    cur.execute("""
        SELECT o.*, u.username, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = %s
    """, (order_id,))
    order = cur.fetchone()

    invoice_number = f"INV-{order_id:04d}"

    cur.execute("""
        SELECT p.name, p.price, oi.quantity, (p.price * oi.quantity) AS line_total
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, (order_id,))
    items = cur.fetchall() or []
    cur.close()

    total = sum(item.get('line_total', 0) for item in items)

    return render_template('invoice.html', order=order, items=items, total=total, invoice_number=invoice_number)

# Admin user management
@app.route('/admin/users')
def admin_users():
    if session.get('loggedin') and session.get('is_admin') == 1:
        cur = mysql.connection.cursor(RealDictCursor)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        return render_template('admin_users.html', users=users)
    return redirect(url_for('login'))

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get('loggedin') and session.get('is_admin') == 1:
        cur = mysql.connection.cursor(RealDictCursor)
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            cur.execute("UPDATE users SET username=%s, email=%s WHERE id=%s", (username, email, user_id))
            mysql.connection.commit()
            cur.close()
            flash("User updated successfully.", "success")
            return redirect(url_for('admin_users'))
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return render_template('edit_user.html', user=user)
    return redirect(url_for('login'))

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('loggedin') and session.get('is_admin') == 1:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        mysql.connection.commit()
        cur.close()
        flash("User deleted successfully.", "danger")
        return redirect(url_for('admin_users'))
    return redirect(url_for('login'))

# -------------------- RUN --------------------
if __name__ == '__main__':
    # for local development
    app.run(debug=True, host='0.0.0.0')
