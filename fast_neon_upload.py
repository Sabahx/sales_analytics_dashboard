"""
SUPER FAST Neon upload using PostgreSQL COPY command.
This can upload 50,000+ rows per second!
"""
import psycopg2
import pandas as pd
from io import StringIO
from datetime import datetime

NEON_URL = "postgresql://neondb_owner:npg_VogqX2pU1sNh@ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("="*80)
print("SUPER FAST NEON UPLOAD - Using PostgreSQL COPY")
print("="*80)

try:
    # Check existing data
    print("\n[1/4] Checking existing data...")
    conn = psycopg2.connect(NEON_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sales_transactions")
    existing_count = cursor.fetchone()[0]
    print(f"Existing rows: {existing_count:,}")

    if existing_count > 0:
        cursor.execute("SELECT MAX(invoice_date) FROM sales_transactions")
        last_date = cursor.fetchone()[0]
        print(f"Last date: {last_date}")
    else:
        last_date = None

    conn.close()

    # Load and process CSV in chunks
    print("\n[2/4] Processing CSV in chunks (FAST!)...")
    chunk_size = 50000
    total_uploaded = 0
    start_time = datetime.now()

    for chunk_num, chunk in enumerate(pd.read_csv('data/raw/data.csv',
                                                    encoding='latin-1',
                                                    chunksize=chunk_size)):
        # Clean data
        chunk.columns = chunk.columns.str.lower()
        chunk['total_amount'] = chunk['quantity'] * chunk['unitprice']
        chunk['invoice_date'] = pd.to_datetime(chunk['invoicedate'])
        chunk['description'] = chunk['description'].fillna('Unknown')
        chunk['customerid'] = chunk['customerid'].fillna(0).astype(int)
        chunk = chunk[chunk['quantity'] > 0]
        chunk = chunk[chunk['unitprice'] >= 0]

        # Skip already uploaded
        if last_date:
            chunk = chunk[chunk['invoice_date'] > last_date]

        if len(chunk) == 0:
            continue

        # Prepare data for COPY
        chunk_data = chunk[['invoiceno', 'stockcode', 'description', 'quantity',
                            'invoice_date', 'unitprice', 'customerid', 'country',
                            'total_amount']].copy()

        # Convert to CSV format in memory
        output = StringIO()
        chunk_data.to_csv(output, sep='\t', header=False, index=False, na_rep='\\N')
        output.seek(0)

        # Use COPY for super fast bulk insert
        try:
            conn = psycopg2.connect(NEON_URL)
            cursor = conn.cursor()

            cursor.copy_from(
                output,
                'sales_transactions',
                columns=('invoice_no', 'stock_code', 'description', 'quantity',
                        'invoice_date', 'unit_price', 'customer_id', 'country',
                        'total_amount'),
                sep='\t',
                null='\\N'
            )

            conn.commit()
            conn.close()

            total_uploaded += len(chunk)
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = total_uploaded / elapsed if elapsed > 0 else 0

            print(f"Chunk {chunk_num+1}: +{len(chunk):,} rows | "
                  f"Total: {existing_count + total_uploaded:,} | "
                  f"Rate: {rate:.0f} rows/sec")

        except Exception as e:
            print(f"Error in chunk {chunk_num+1}: {e}")
            # Try row-by-row for this chunk if COPY fails
            print(f"Retrying chunk {chunk_num+1} with slower method...")
            try:
                conn = psycopg2.connect(NEON_URL)
                cursor = conn.cursor()
                batch_count = 0
                for _, row in chunk_data.iterrows():
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
                        batch_count += 1
                        if batch_count % 1000 == 0:
                            conn.commit()
                    except:
                        continue
                conn.commit()
                conn.close()
                total_uploaded += batch_count
                print(f"  Recovered {batch_count:,} rows")
            except Exception as e2:
                print(f"  Recovery failed: {e2}")
                continue

    # Verify
    print("\n[3/4] Verifying upload...")
    conn = psycopg2.connect(NEON_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_transactions")
    final_count = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(invoice_date), MIN(invoice_date) FROM sales_transactions")
    max_date, min_date = cursor.fetchone()
    conn.close()

    elapsed_total = (datetime.now() - start_time).total_seconds()

    print("\n" + "="*80)
    print("FAST UPLOAD COMPLETE!")
    print("="*80)
    print(f"Starting count:  {existing_count:,}")
    print(f"Rows uploaded:   {total_uploaded:,}")
    print(f"Final count:     {final_count:,}")
    print(f"Date range:      {min_date} to {max_date}")
    print(f"Total time:      {elapsed_total/60:.1f} minutes")
    if total_uploaded > 0:
        print(f"Average rate:    {total_uploaded/elapsed_total:.0f} rows/second")
    print("="*80)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
