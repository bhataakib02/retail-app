-- PostgreSQL schema for Supabase
-- Note: Database and schema are managed by Supabase

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    image VARCHAR(255),
    stock INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'Pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price_at_time DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Insert admin user (only if not exists)
INSERT INTO users (username, email, password, role)
SELECT 'admin', 'admin@admin.com', 'admin123', 'admin'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@admin.com');

-- Insert products (only if table is empty)
INSERT INTO products (name, description, price, image, stock)
SELECT * FROM (VALUES
    ('1984', 'A dystopian novel by George Orwell.', 299.00, '1984.jpg', 20),
    ('ab_wheel', 'Abdominal exercise wheel for core workouts.', 899.00, 'ab_wheel.jpg', 15),
    ('airdopes441', 'Wireless earbuds with Bluetooth connectivity.', 1499.00, 'airdopes441.jpg', 30),
    ('airfryer', 'Healthy air fryer for oil-free cooking.', 4999.00, 'airfryer.jpg', 10),
    ('anarkali', 'Traditional Indian Anarkali dress.', 1999.00, 'anarkali.jpg', 8),
    ('basketball', 'Official size basketball.', 599.00, 'basketball.jpg', 25),
    ('beats_studio', 'Noise cancelling Beats Studio headphones.', 18999.00, 'beats_studio.jpg', 12),
    ('blazer', 'Formal blue blazer.', 2499.00, 'blazer.jpg', 10),
    ('canon_g7x', 'Canon G7X digital camera.', 42999.00, 'canon_g7x.jpg', 5),
    ('cant_hurt_me', 'Motivational book by David Goggins.', 349.00, 'cant_hurt_me.jpg', 20),
    ('chinos', 'Comfortable green chinos pants.', 1199.00, 'chinos.jpg', 18),
    ('cricket_bat', 'Wooden cricket bat for practice and matches.', 999.00, 'cricket_bat.jpg', 22),
    ('cricket_gloves', 'Pair of professional cricket gloves.', 799.00, 'cricket_gloves.jpg', 15),
    ('denim_skirt', 'Blue denim skirt for casual wear.', 899.00, 'denim_skirt.jpg', 12),
    ('dinner_set', 'Ceramic 16-piece dinner set.', 1999.00, 'dinner_set.jpg', 10),
    ('download', 'Zero to One by Peter Thiel - Book.', 299.00, 'download.jpg', 20),
    ('fabindia_kurta', 'Traditional green kurta from Fabindia.', 1099.00, 'fabindia_kurta.jpg', 10),
    ('four_agreements', 'Spiritual guide to personal freedom.', 349.00, 'four_agreements.jpg', 25),
    ('hand_gripper', 'Grip strength training tool.', 299.00, 'hand_gripper.jpg', 30),
    ('heater', 'Electric room heater for winters.', 1499.00, 'heater.jpg', 8),
    ('hrx_shorts', 'Men''s sports shorts by HRX.', 699.00, 'hrx_shorts.jpg', 20),
    ('inspiron14', 'Dell Inspiron 14 Laptop.', 47999.00, 'inspiron14.jpg', 4),
    ('ipad_air', 'Apple iPad Air 10.9 inch.', 56999.00, 'ipad_air.jpg', 6),
    ('lg_oled', 'LG 55 inch OLED TV.', 109999.00, 'lg_oled.jpg', 2),
    ('lunchbox', 'Microwave safe tiffin lunchbox.', 499.00, 'lunchbox.jpg', 30),
    ('mi13pro', 'Xiaomi 13 Pro smartphone.', 59999.00, 'mi13pro.jpg', 7),
    ('otg', 'Multi-port USB OTG adapter.', 249.00, 'otg.jpg', 40),
    ('pixel8', 'Google Pixel 8 smartphone.', 67999.00, 'pixel8.jpg', 5),
    ('power_of_now', 'Spiritual book by Eckhart Tolle.', 299.00, 'power_of_now.jpg', 25),
    ('reebok_trainers', 'Running shoes by Reebok.', 2599.00, 'reebok_trainers.jpg', 18),
    ('rice_cooker', 'Electric rice cooker.', 1299.00, 'rice_cooker.jpg', 12),
    ('rogphone7', 'Asus ROG Phone 7 for gaming.', 71999.00, 'rogphone7.jpg', 3),
    ('sewing_machine', 'Compact electric sewing machine.', 3999.00, 'sewing_machine.jpg', 6),
    ('shin_guards', 'Pair of shin guards for sports.', 499.00, 'shin_guards.jpg', 20),
    ('show_your_work', 'Book by Austin Kleon.', 299.00, 'show_your_work.jpg', 15),
    ('silent_patient', 'Thriller novel by Alex Michaelides.', 349.00, 'silent_patient.jpg', 20),
    ('skipping_rope', 'Adjustable skipping rope.', 199.00, 'skipping_rope.jpg', 30),
    ('start_with_why', 'Book by Simon Sinek.', 349.00, 'start_with_why.jpg', 25),
    ('stool', 'Wooden sitting stool.', 799.00, 'stool.jpg', 10),
    ('subtle_art', 'The Subtle Art of Not Giving a F*ck book.', 349.00, 'subtle_art.jpg', 30),
    ('tawa', 'Non-stick flat tawa for cooking.', 499.00, 'tawa.jpg', 12),
    ('tennis_racket', 'Set of tennis rackets.', 1499.00, 'tennis_racket.jpg', 8),
    ('timex_watch', 'Timex men''s digital wristwatch.', 1999.00, 'timex_watch.jpg', 10),
    ('tommy_polo', 'Tommy Hilfiger polo t-shirt.', 1299.00, 'tommy_polo.jpg', 18),
    ('washing_machine', 'Semi-automatic washing machine.', 8499.00, 'washing_machine.jpg', 4),
    ('water_bottle', 'Steel insulated water bottle.', 299.00, 'water_bottle.jpg', 25),
    ('yoga_mat', 'Comfortable yoga mat with strap.', 599.00, 'yoga_mat.jpg', 20),
    ('you_can_win', 'Book by Shiv Khera.', 299.00, 'you_can_win.jpg', 25),
    ('zara_jeans', 'Blue Zara denim jeans.', 1499.00, 'zara_jeans.jpg', 15),
    ('zenbook_duo', 'ASUS Zenbook Duo dual screen laptop.', 139999.00, 'zenbook_duo.jpg', 2)
) AS v(name, description, price, image, stock)
WHERE NOT EXISTS (SELECT 1 FROM products LIMIT 1);
