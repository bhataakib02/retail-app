# app.py - corrected and ready for Aiven MySQL (PyMySQL shim + SQLAlchemy TLS)
import os
import pymysql
pymysql.install_as_MySQLdb()  # make PyMySQL present as MySQLdb for legacy code

from flask import (
    Flask, g, render_template, request, redirect, session, url_for,
    flash, jsonify
)
from werkzeug.utils import secure_filename

# MySQLdb will be available because we installed the shim above
import MySQLdb
import MySQLdb.cursors

# SQLAlchemy + helper to safely modify URL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import make_url

# create app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_me_in_prod")

# -------------------- DATABASE / SQLALCHEMY TLS CONFIG --------------------
# Priority: use DATABASE_URL (recommended). If not present, fallback to individual env vars.
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASS = os.environ.get("DB_PASS", "")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "retail_db")
    database_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Remove "ssl-mode" query param (some drivers try to pass it as a keyword and cause errors).
# Then enable TLS for PyMySQL via connect_args.
try:
    url_obj = make_url(database_url)
    qdict = dict(url_obj.query)  # copy to mutable dict
    qdict.pop("ssl-mode", None)  # remove if present
    # Rebuild URL with cleaned query
    url_obj = url_obj._replace(query=qdict)
    database_url = str(url_obj)
except Exception:
    # If parsing fails for any reason, fall back to raw database_url and still set connect_args.
    pass

# Configure Flask-SQLAlchemy to use TLS (empty dict triggers TLS handshake) and timeout.
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"ssl": {}, "connect_timeout": 10}
}

# init SQLAlchemy
db = SQLAlchemy(app)

# -------------------- Legacy MySQLdb compatibility shim --------------------
def get_legacy_db_conn():
    """
    Return a MySQLdb connection (PyMySQL provides MySQLdb after install_as_MySQLdb()).
    Reads DB connection info from environment when available.
    """
    # derive fallback values
    fallback_db = (os.environ.get("DB_NAME") or
                   (database_url.rsplit("/", 1)[-1] if "/" in database_url else "retail_db"))
    conn = MySQLdb.connect(
        host=os.environ.get("DB_HOST", os.environ.get("DB_HOST", "127.0.0.1")),
        user=os.environ.get("DB_USER", os.environ.get("DB_USER", "root")),
        passwd=os.environ.get("DB_PASS", os.environ.get("DB_PASS", "")),
        db=os.environ.get("DB_NAME", fallback_db),
        port=int(os.environ.get("DB_PORT", os.environ.get("DB_PORT", 3306))),
        connect_timeout=10,
        charset="utf8mb4",
        use_unicode=True
    )
    return conn

def get_request_conn():
    if not hasattr(g, "db_conn"):
        g.db_conn = get_legacy_db_conn()
    return g.db_conn

@app.teardown_appcontext
def close_request_conn(exception=None):
    conn = g.pop("db_conn", None)
    try:
        if conn:
            conn.close()
    except Exception:
        pass

class MySQLCompat:
    """Compatibility object so existing code using `mysql.connection.cursor()` keeps working."""
    @property
    def connection(self):
        return get_request_conn()

# instantiate compatibility object
mysql = MySQLCompat()

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
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
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
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        return render_template('user_dashboard.html', username=session['username'], products=products)
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT COUNT(*) AS total_users FROM users WHERE role='user'")
        users = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS total_products FROM products")
        products = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS total_orders FROM orders")
        orders = cur.fetchone()
        cur.execute("SELECT * FROM products")
        all_products = cur.fetchall()
        return render_template('admin_dashboard.html', users=users, products=products, orders=orders, all_products=all_products)
    return redirect(url_for('login'))

# Products
@app.route('/products')
def view_products():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
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
                flash("Product added successfully.", "success")
                return redirect(url_for('admin_products'))
            flash("Invalid image file.", "danger")
        return render_template('add_product.html')
    return redirect(url_for('login'))

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
            flash("Product updated successfully.", "success")
            return redirect(url_for('admin_products'))
        cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = cur.fetchone()
        return render_template('edit_product.html', product=product)
    return redirect(url_for('login'))

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        mysql.connection.commit()
        flash("Product deleted successfully.", "danger")
        return redirect(url_for('admin_products'))
    return redirect(url_for('login'))

@app.route('/admin_products')
def admin_products():
    if session.get('loggedin') and session.get('role') == 'admin':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
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
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    products = []
    if product_ids:
        placeholders = ','.join(['%s'] * len(product_ids))
        cur.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", product_ids)
        products = cur.fetchall()
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
        cur.execute("INSERT INTO orders (user_id, payment_method, payment_status) VALUES (%s, %s, %s)",
                    (session['id'], payment_method, 'Completed'))
        order_id = cur.lastrowid
        for pid, qty in cart.items():
            cur.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (order_id, pid, qty))
            cur.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (qty, pid))
        mysql.connection.commit()
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
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM orders WHERE user_id = %s", (session['id'],))
        orders = cur.fetchall()
        return render_template('orders.html', orders=orders)
    return redirect(url_for('login'))

@app.route('/admin/orders')
def admin_orders():
    if 'id' in session and session['role'] == 'admin':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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

    total = sum(item.get('line_total', 0) for item in items)

    return render_template('invoice.html', order=order, items=items, total=total, invoice_number=invoice_number)

# Admin user management
@app.route('/admin/users')
def admin_users():
    if session.get('loggedin') and session.get('is_admin') == 1:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        return render_template('admin_users.html', users=users)
    return redirect(url_for('login'))

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get('loggedin') and session.get('is_admin') == 1:
        cur = mysql.connection.cursor()
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            cur.execute("UPDATE users SET username=%s, email=%s WHERE id=%s", (username, email, user_id))
            mysql.connection.commit()
            flash("User updated successfully.", "success")
            return redirect(url_for('admin_users'))
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        return render_template('edit_user.html', user=user)
    return redirect(url_for('login'))

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('loggedin') and session.get('is_admin') == 1:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        mysql.connection.commit()
        flash("User deleted successfully.", "danger")
        return redirect(url_for('admin_users'))
    return redirect(url_for('login'))

# -------------------- RUN --------------------
if __name__ == '__main__':
    # for local development
    app.run(debug=True, host='0.0.0.0')
