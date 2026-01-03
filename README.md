
# 🛒 Online Retail Application Management System

A full-stack web-based application built for managing an online retail store.

## 📌 Project Overview

This application simulates a real-world e-commerce environment with features for both customers and administrators. It enables customers to browse products, manage their shopping carts, place orders, and view invoices. Administrators can manage users, products, inventory, and orders.

## 🎯 Objectives

- Implement real-world database engineering principles such as ER modeling and normalization.
- Design a secure and efficient relational database system.
- Develop a user-friendly and responsive interface.
- Enable role-based authentication and authorization.
- Provide complete e-commerce functionality including checkout and order history.

## 🛠️ Tech Stack

| Layer        | Technology Used           |
|--------------|----------------------------|
| Frontend     | HTML, CSS, Bootstrap, JavaScript |
| Backend      | Python (Flask Framework)   |
| Database     | PostgreSQL (Supabase)      |
| Others       | Font Awesome, Flask-SQLAlchemy, Jinja2 Templates |

## 🔐 Key Features

### 👤 User Features:
- Register/Login with role selection
- Browse products with images
- Add items to cart and checkout
- View order history and invoice

### 🔧 Admin Features:
- Admin dashboard
- Add/Edit/Delete Products
- Manage Users
- Track orders and generate invoices

## 🧱 Database Design

- Properly normalized tables (UNF → 3NF)
- Entities: `users`, `products`, `cart`, `orders`, `order_items`, `invoices`
- ER Diagram and relational schema included in documentation

## 📸 Screenshots

- Login / Register Page
- Admin Dashboard
- Product Listings
- Cart & Checkout Page
- Invoice Page

*(Screenshots available in `/screenshots` folder)*

## 📝 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/online-retail-app.git
   cd online-retail-app
   ```

2. **Create & Activate Virtual Environment**
   ```bash
   python -m venv venv 
On Windows:
     venv\Scripts\activate
On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL Database (Supabase)**
   - Create a Supabase project at https://supabase.com
   - Set the `DATABASE_URL` environment variable with your Supabase connection string
   - Run the migration script: `python run_migrations.py`
   - Or import the SQL schema from `db/schema.sql` in Supabase SQL Editor

5. **Set Environment Variables**
   ```bash
   # Create a .env file (optional, for local development)
   export DATABASE_URL="postgresql://postgres:password@db.project.supabase.co:5432/postgres"
   export SECRET_KEY="your-secret-key-here"
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```

7. **Visit in Browser**
   - Navigate to `http://127.0.0.1:5000`

## 🚀 Deployment

This application is configured for deployment on Vercel with Supabase. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### ✅ `requirements.txt`

```txt
Flask==2.2.5
Werkzeug==2.2.3
Flask-SQLAlchemy==3.0.5
SQLAlchemy==2.0.22
psycopg2-binary==2.9.9
gunicorn==21.2.0
```

---

### ✅ Installation Steps

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
