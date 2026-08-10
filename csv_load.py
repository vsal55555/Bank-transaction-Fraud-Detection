import psycopg2
import os

# ── CONNECTION SETTINGS ───────────────────────────────────────────
# Update these if your PostgreSQL setup is different.
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "OLTP_DB"  # replace with your actual database name
DB_USER     = "postgres"  # replace with your actual database user
DB_PASSWORD = "thiswillpass"  # replace with your actual database password

# Path to the CSV file (same folder as this script by default)
CSV_PATH = os.path.join(os.path.dirname(__file__), "bank_transactions_data_2.csv")
# ─────────────────────────────────────────────────────────────────


# ── STEP 1: CREATE TABLE SQL ──────────────────────────────────────
# Defines the schema for the bank_transactions_data_2 table.
# Notice: each column has a specific type, and some have constraints.
# We talked about why each choice was made in class.

CREATE_TABLE_SQL = """
DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id            VARCHAR(50) PRIMARY KEY,
    account_id                VARCHAR(50)           NOT NULL,
    transaction_amount        NUMERIC(18,2)         NOT NULL,
    transaction_date          TIMESTAMP             NOT NULL,
    transaction_type          VARCHAR(50)           NOT NULL,

    location                  VARCHAR(100),
    device_id                 VARCHAR(50),
    ip_address                INET,

    merchant_id               VARCHAR(50),
    channel                   VARCHAR(50),

    customer_age              INTEGER,
    customer_occupation       VARCHAR(100),

    transaction_duration      INTEGER,
    login_attempts            INTEGER,

    account_balance           NUMERIC(18,2),

    previous_transaction_date TIMESTAMP

);
"""
# Note: completed_at, rating, and payment_method are nullable (no NOT NULL).
# Can you think of why? What does a NULL value mean for each of these?
# ─────────────────────────────────────────────────────────────────


def get_connection():
    """Open and return a database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def create_table(conn):
    """Drop and recreate the transactions table."""
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    print("Table created")


def load_csv(conn, csv_path):
    """
    Load the CSV into the transactions table using PostgreSQL's COPY command.

    COPY is much faster than inserting rows one by one -- it streams
    the file directly into the table at the database level.

    The 'with open(...)' block safely closes the file even if an
    error occurs mid-load.
    """
    with conn.cursor() as cur:
        with open(csv_path, "r", encoding="utf-8") as f:
            next(f)  # skip the header row -- COPY doesn't want it
            cur.copy_from(
                file=f,
                table="transactions",
                sep=",",
                null=""   # treat empty string as NULL
            )
        row_count = cur.rowcount
    conn.commit()
    return row_count


def verify(conn):
    """Run a quick sanity check -- print counts """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) AS total
            FROM transactions;
        """)
        rows = cur.fetchall()

    print("\ntransactions count:")
    for (count,) in rows:
        print(f" {count:>6}")


def main():
    print(f"Connecting to {DB_NAME} on {DB_HOST}:{DB_PORT}...")

    conn = get_connection()
    print("Connected")

    create_table(conn)

    print(f"Loading {CSV_PATH}...")
    loaded = load_csv(conn, CSV_PATH)
    print(f"Loaded {loaded:,} rows")

    verify(conn)

    conn.close()
    print("\nDone. Open DBeaver and run:  SELECT * FROM transactions LIMIT 10;")


if __name__ == "__main__":
    main()
