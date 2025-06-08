-- Create schemas for separation of concerns
CREATE SCHEMA IF NOT EXISTS products;
CREATE SCHEMA IF NOT EXISTS inventory; 
CREATE SCHEMA IF NOT EXISTS orders;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Products table
CREATE TABLE IF NOT EXISTS products.products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory.inventory (
    product_id UUID PRIMARY KEY REFERENCES products.products(product_id),
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    warehouse_location VARCHAR(100),
    last_restocked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders.orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Order items table
CREATE TABLE IF NOT EXISTS orders.order_items (
    id SERIAL PRIMARY KEY,
    order_id UUID REFERENCES orders.orders(order_id),
    product_id UUID REFERENCES products.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL
);

-- Insert sample data for testing
INSERT INTO products.products (sku, name, description, price, category) 
VALUES 
    ('WIDGET-001', 'Test Widget', 'A test widget for integration tests', 29.99, 'Widgets'),
    ('GADGET-001', 'Test Gadget', 'A test gadget for integration tests', 49.99, 'Gadgets')
ON CONFLICT (sku) DO NOTHING;

-- Insert inventory data
INSERT INTO inventory.inventory (product_id, stock_quantity, reserved_quantity) 
SELECT product_id, 100, 0 FROM products.products 
WHERE sku IN ('WIDGET-001', 'GADGET-001')
ON CONFLICT (product_id) DO UPDATE SET 
    stock_quantity = 100, 
    reserved_quantity = 0;