-- Sales Analytics Database Initialization Script

-- Create sales_transactions table
CREATE TABLE IF NOT EXISTS sales_transactions (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(20) NOT NULL,
    stock_code VARCHAR(50) NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    invoice_date TIMESTAMP NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    customer_id INTEGER,
    country VARCHAR(100) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_invoice_no ON sales_transactions(invoice_no);
CREATE INDEX IF NOT EXISTS idx_invoice_date ON sales_transactions(invoice_date);
CREATE INDEX IF NOT EXISTS idx_customer_id ON sales_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_country ON sales_transactions(country);
CREATE INDEX IF NOT EXISTS idx_stock_code ON sales_transactions(stock_code);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_date_country ON sales_transactions(invoice_date, country);
CREATE INDEX IF NOT EXISTS idx_customer_date ON sales_transactions(customer_id, invoice_date);

-- Create a view for quick KPI access
CREATE OR REPLACE VIEW v_sales_kpis AS
SELECT
    COUNT(DISTINCT invoice_no) as total_orders,
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(DISTINCT stock_code) as total_products,
    COUNT(DISTINCT country) as total_countries,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value,
    MIN(invoice_date) as first_transaction,
    MAX(invoice_date) as last_transaction
FROM sales_transactions;

-- Create a materialized view for monthly aggregates (optional, for performance)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_sales AS
SELECT
    DATE_TRUNC('month', invoice_date) as month,
    COUNT(DISTINCT invoice_no) as orders,
    COUNT(DISTINCT customer_id) as customers,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order_value
FROM sales_transactions
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY month;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_mv_monthly_month ON mv_monthly_sales(month);

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_sales;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO postgres;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Sales Analytics Database initialized successfully';
    RAISE NOTICE 'Tables created: sales_transactions';
    RAISE NOTICE 'Views created: v_sales_kpis, mv_monthly_sales';
    RAISE NOTICE 'Indexes created for optimal query performance';
END $$;
