"""Check Neon upload progress anytime"""
import psycopg2

NEON_URL = "postgresql://neondb_owner:npg_VogqX2pU1sNh@ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    conn = psycopg2.connect(NEON_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sales_transactions")
    count = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(invoice_date), MIN(invoice_date) FROM sales_transactions")
    max_date, min_date = cursor.fetchone()

    expected_total = 540000
    progress_pct = (count / expected_total) * 100

    print(f"\n{'='*70}")
    print(f"  NEON POSTGRESQL UPLOAD PROGRESS")
    print(f"{'='*70}")
    print(f"  Current rows:    {count:,} / ~{expected_total:,}")
    print(f"  Progress:        {progress_pct:.1f}%")
    print(f"  Date range:      {min_date} to {max_date}")
    print(f"  Remaining:       ~{expected_total - count:,} rows")
    print(f"{'='*70}\n")

    conn.close()
except Exception as e:
    print(f"\nError: {e}\n")
