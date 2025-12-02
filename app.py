# ===== START: PyMySQL shim + SQLAlchemy + legacy mysql compatibility =====
import os
import pymysql
pymysql.install_as_MySQLdb()   # makes a MySQLdb module available (pure Python)

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, session, url_for

# create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_me_in_prod")

# Configure SQLAlchemy from DATABASE_URL environment variable (recommended)
# Example: mysql+pymysql://user:pass@host:port/dbname?ssl-mode=REQUIRED
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # fallback to individual vars if you use them (not recommended in production)
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASS = os.environ.get("DB_PASS", "")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "retail_db")
    database_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Legacy DB connection factory that returns a MySQLdb-compatible connection (PyMySQL provides MySQLdb)
def get_legacy_db_conn():
    import MySQLdb
    conn = MySQLdb.connect(
        host=os.environ.get("DB_HOST", DB_HOST if 'DB_HOST' in locals() else "127.0.0.1"),
        user=os.environ.get("DB_USER", DB_USER if 'DB_USER' in locals() else "root"),
        passwd=os.environ.get("DB_PASS", DB_PASS if 'DB_PASS' in locals() else ""),
        db=os.environ.get("DB_NAME", DB_NAME if 'DB_NAME' in locals() else database_url.rsplit("/", 1)[-1]),
        port=int(os.environ.get("DB_PORT", DB_PORT if 'DB_PORT' in locals() else 3306)),
        connect_timeout=5,
        charset="utf8mb4",
        use_unicode=True
    )
    return conn

# Request-scoped connection stored on flask.g (automatically closed)
def get_request_conn():
    if not hasattr(g, "db_conn"):
        g.db_conn = get_legacy_db_conn()
    return g.db_conn

from flask import has_request_context
from flask import request

@app.teardown_appcontext
def close_request_conn(exception=None):
    conn = g.pop("db_conn", None)
    try:
        if conn:
            conn.close()
    except Exception:
        pass

# Compatibility object exposing .connection so existing code works: mysql.connection.cursor()
class MySQLCompat:
    @property
    def connection(self):
        return get_request_conn()

# instantiate
mysql = MySQLCompat()

# helper for allowed files (you probably already have this lower in the file)
UPLOAD_FOLDER = 'static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# simple health route (keeps it here so it exists even before other imports)
@app.route("/_health")
def _health():
    return {"status": "ok"}, 200

# ===== END shim =====

# ------------------ AUTH ------------------

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
            session['role'] = user['role']
            session['is_admin'] = 1 if user['role'] == 'admin' else 0
            return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('user_dashboard'))
        flash("Incorrect email or password.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# ------------------ DASHBOARDS ------------------

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

# ------------------ PRODUCTS ------------------

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
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
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
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
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

# ------------------ CART & ORDERS ------------------

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

        # Group products by order ID
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

    # Add formatted invoice number
    invoice_number = f"INV-{order_id:04d}"

    cur.execute("""
        SELECT p.name, p.price, oi.quantity, (p.price * oi.quantity) AS line_total
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, (order_id,))
    items = cur.fetchall()

    total = sum(item['line_total'] for item in items)

    return render_template('invoice.html', order=order, items=items, total=total, invoice_number=invoice_number)


# ------------------ USER MANAGEMENT ------------------

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

# ------------------ MAIN ------------------

if __name__ == '__main__':
    app.run(debug=True)
