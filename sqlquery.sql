DROP TABLE IF EXISTS blinkit_orders;

CREATE TABLE blinkit_orders (
order_id TEXT,
customer_id TEXT,
order_date TIMESTAMP,
promised_delivery_time TIMESTAMP,
actual_delivery_time TIMESTAMP,
delivery_status TEXT,
order_total FLOAT,
payment_method TEXT,
delivery_partner_id TEXT,
store_id TEXT
);

SELECT * FROM blinkit_orders LIMIT 10;

DROP TABLE IF EXISTS blinkit_customer_feedback;


CREATE TABLE blinkit_customer_feedback (
feedback_id TEXT,
order_id TEXT,
customer_id TEXT,
rating FLOAT,
feedback_text TEXT,
feedback_category TEXT,
sentiment TEXT,
feedback_date TIMESTAMP
);


SELECT * FROM blinkit_customer_feedback LIMIT 10;

DROP TABLE IF EXISTS blinkit_customers;

CREATE TABLE blinkit_customers (
customer_id TEXT,
customer_name TEXT,
email TEXT,
phone TEXT,
address TEXT,
area TEXT,
pincode TEXT,
registration_date TIMESTAMP,
customer_segment TEXT,
total_orders FLOAT,
avg_order_value FLOAT
);

SELECT * FROM blinkit_customers LIMIT 10;

DROP TABLE IF EXISTS blinkit_products;

CREATE TABLE blinkit_products (
product_id TEXT,
product_name TEXT,
category TEXT,
brand TEXT,
price FLOAT,
mrp FLOAT,
margin_percentage FLOAT,
shelf_life_days INT,
min_stock_level INT,
max_stock_level INT
);


SELECT * FROM blinkit_products LIMIT 10;


DROP TABLE IF EXISTS blinkit_order_items;

CREATE TABLE blinkit_order_items (
order_id TEXT,
product_id TEXT,
quantity INT,
unit_price FLOAT
);

SELECT * FROM blinkit_order_items LIMIT 10;

DROP TABLE IF EXISTS blinkit_marketing_performance;


CREATE TABLE blinkit_marketing_performance (
campaign_id TEXT,
campaign_name TEXT,
date DATE,
target_audience TEXT,
channel TEXT,
impressions INT,
clicks INT,
conversions INT,
spend FLOAT,
revenue_generated FLOAT,
roas FLOAT
);

SELECT * FROM blinkit_marketing_performance LIMIT 10;

DROP VIEW IF EXISTS orders_with_customer;

CREATE VIEW orders_with_customer AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.promised_delivery_time,
    o.actual_delivery_time,
    o.delivery_status,
    o.order_total,
    c.area,
    c.customer_segment
FROM blinkit_orders o
LEFT JOIN blinkit_customers c
ON o.customer_id = c.customer_id;



SELECT COUNT(*) FROM blinkit_orders;

SELECT COUNT(*) FROM blinkit_customers;


SELECT * FROM orders_with_customer LIMIT 10;