"""
Complete Neon PostgreSQL setup: Create tables and upload all data.
Much more stable than Railway!
"""
import psycopg2
import pandas as pd
import time
from datetime import datetime

# Neon PostgreSQL connection
NEON_URL = "postgresql://neondb_owner:npg_VogqX2pU1sNh@ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
BATCH_SIZE = 10000

print("="*80)
print("NEON POSTGRESQL SETUP AND DATA UPLOAD")
print("="*80)

try:
    # Step 1: Create tables
    print("\n[1/5] Connecting to Neon and creating tables...")
    conn = psycopg2.connect(NEON_URL)
    cursor = conn.cursor()

    # Create sales_transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_transactions (
            id SERIAL PRIMARY KEY,
            invoice_no VARCHAR(50) NOT NULL,
            stock_code VARCHAR(50) NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL,
            invoice_date TIMESTAMP NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            customer_id INTEGER,
            country VARCHAR(100),
            total_amount DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_date ON sales_transactions(invoice_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_id ON sales_transactions(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON sales_transactions(country);")

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            is_superuser BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            verification_token VARCHAR(255),
            verification_token_expires TIMESTAMP,
            reset_password_token VARCHAR(255),
            reset_password_token_expires TIMESTAMP
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

    conn.commit()
    print("Tables and indexes created successfully!")

    # Check existing data
    cursor.execute("SELECT COUNT(*) FROM sales_transactions")
    existing_count = cursor.fetchone()[0]
    print(f"Existing rows: {existing_count:,}")

    if existing_count > 0:
        cursor.execute("SELECT MAX(invoice_date) FROM sales_transactions")
        last_date = cursor.fetchone()[0]
        print(f"Last uploaded date: {last_date}")
    else:
        last_date = None

    conn.close()

    # Step 2: Load CSV
    print("\n[2/5] Loading CSV file...")
    print("This takes 2-3 minutes for 540K rows...")
    df = pd.read_csv('data/raw/data.csv', encoding='latin-1')
    print(f"Total rows in CSV: {len(df):,}")

    # Step 3: Clean data
    print("\n[3/5] Cleaning data...")
    df.columns = df.columns.str.lower()
    df['total_amount'] = df['quantity'] * df['unitprice']
    df['invoice_date'] = pd.to_datetime(df['invoicedate'])
    df['description'] = df['description'].fillna('Unknown')
    df['customerid'] = df['customerid'].fillna(0).astype(int)
    df = df[df['quantity'] > 0]
    df = df[df['unitprice'] >= 0]
    df = df.sort_values('invoice_date')
    print(f"Rows after cleaning: {len(df):,}")

    # Skip already uploaded
    if last_date:
        df = df[df['invoice_date'] > last_date].copy()
        print(f"Rows to upload: {len(df):,}")

    if len(df) == 0:
        print("\nDatabase is up to date!")
        exit(0)

    # Step 4: Upload in batches
    print(f"\n[4/5] Uploading {len(df):,} rows to Neon...")
    print("="*80)

    total_uploaded = 0
    start_time = datetime.now()
    num_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(num_batches):
        batch_start = batch_num * BATCH_SIZE
        batch_end = min(batch_start + BATCH_SIZE, len(df))
        batch = df.iloc[batch_start:batch_end]

        try:
            conn = psycopg2.connect(NEON_URL)
            cursor = conn.cursor()

            batch_uploaded = 0
            for _, row in batch.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO sales_transactions
                        (invoice_no, stock_code, description, quantity, invoice_date,
                         unit_price, customer_id, country, total_amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        str(row['invoiceno']),
                        str(row['stockcode']),
                        str(row['description'])[:500],
                        int(row['quantity']),
                        row['invoice_date'],
                        float(row['unitprice']),
                        int(row['customerid']),
                        str(row['country']),
                        float(row['total_amount'])
                    ))
                    batch_uploaded += 1

                    if batch_uploaded % 500 == 0:
                        conn.commit()

                except Exception as e:
                    continue

            conn.commit()
            conn.close()

            total_uploaded += batch_uploaded
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = total_uploaded / elapsed if elapsed > 0 else 0
            remaining = len(df) - total_uploaded
            eta = remaining / rate if rate > 0 else 0

            print(f"Batch {batch_num+1}/{num_batches}: +{batch_uploaded:,} rows | "
                  f"Total: {existing_count + total_uploaded:,} | "
                  f"{rate:.0f} rows/sec | ETA: {eta/60:.1f} min")

            # Small pause between batches
            if batch_num < num_batches - 1:
                time.sleep(1)

        except Exception as e:
            print(f"Batch {batch_num+1} error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            continue

    # Step 5: Verify
    print("\n[5/5] Verifying upload...")
    conn = psycopg2.connect(NEON_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_transactions")
    final_count = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(invoice_date), MIN(invoice_date) FROM sales_transactions")
    max_date, min_date = cursor.fetchone()
    conn.close()

    elapsed_total = (datetime.now() - start_time).total_seconds()

    print("\n" + "="*80)
    print("NEON SETUP COMPLETE!")
    print("="*80)
    print(f"Starting count:  {existing_count:,}")
    print(f"Rows uploaded:   {total_uploaded:,}")
    print(f"Final count:     {final_count:,}")
    print(f"Date range:      {min_date} to {max_date}")
    print(f"Total time:      {elapsed_total/60:.1f} minutes")
    print(f"Average rate:    {total_uploaded/elapsed_total:.0f} rows/second")
    print("="*80)
    print("\nNext steps:")
    print("1. Update Railway API environment variables")
    print("2. Update Streamlit Cloud secrets")
    print("="*80)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
