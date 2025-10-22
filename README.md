
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
| Database     | MySQL                      |
| Others       | Font Awesome, Flask-MySQLdb, Jinja2 Templates |

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

4. **Setup MySQL Database**
   - Create a database named `retail_store`
   - Import the SQL schema provided in `/database/retail_store.sql`

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Visit in Browser**
   - Navigate to `http://127.0.0.1:5000`


### ✅ `requirements.txt`

```txt
Flask==2.2.5
Flask-MySQLdb==1.0.1
mysqlclient==2.2.0
Werkzeug==2.2.3
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
