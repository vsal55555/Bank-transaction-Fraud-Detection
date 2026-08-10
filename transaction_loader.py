#!/usr/bin/env python3

import os
import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "OLTP_DB"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "thiswillpass")
}

N_TRANSACTIONS = 40

START_DATE = datetime(2025, 6, 26)
END_DATE = datetime(2025, 6, 28)

random.seed(42)


def random_datetime():
    diff = int(
        (END_DATE - START_DATE).total_seconds()
    )

    return START_DATE + timedelta(
        seconds=random.randint(0, diff)
    )


def get_ids(cur, table, column):

    cur.execute(
        f"SELECT {column} FROM {table}"
    )

    return [r[0] for r in cur.fetchall()]

def get_next_transaction_number(cur):

    cur.execute("""
        SELECT COALESCE(
            MAX(
                CAST(
                    REPLACE(transaction_id,'TX','')
                    AS INTEGER
                )
            ),
            0
        )
        FROM bank_transactions
    """)

    return cur.fetchone()[0] + 1

def generate_transactions(cur):

    account_ids = get_ids(
        cur,
        "accounts",
        "naccount_id"
    )

    merchant_ids = get_ids(
        cur,
        "merchants",
        "nmerchant_id"
    )

    location_ids = get_ids(
        cur,
        "locations",
        "location_id"
    )

    channel_ids = get_ids(
        cur,
        "channels",
        "channel_id"
    )

    occupation_ids = get_ids(
        cur,
        "occupations",
        "occupation_id"
    )

    rows = []
    start_txn = get_next_transaction_number(cur)
    
    for i in range(N_TRANSACTIONS):

        txn_time = random_datetime()
        
        rows.append(
            (
                f"TX{start_txn+i:07d}",

                random.choice(account_ids),

                round(
                    random.uniform(
                        10,
                        100000
                    ),
                    2
                ),

                txn_time,

                random.choice(
                    [
                        "DEBIT",
                        "CREDIT"
                    ]
                ),

                random.choice(
                    location_ids
                ),

                f"D{random.randint(1000,9999)}",

                f"10.{random.randint(0,255)}."
                f"{random.randint(0,255)}."
                f"{random.randint(0,255)}",

                random.choice(
                    merchant_ids
                ),

                random.choice(
                    channel_ids
                ),

                random.randint(
                    18,
                    75
                ),

                random.choice(
                    occupation_ids
                ),

                random.randint(
                    10,
                    600
                ),

                random.randint(
                    0,
                    5
                ),

                round(
                    random.uniform(
                        1000,
                        1000000
                    ),
                    2
                ),

                txn_time
                - timedelta(
                    minutes=random.randint(
                        10,
                        5000
                    )
                )
            )
        )

    sql = """
    INSERT INTO bank_transactions (

        transaction_id,
        naccount_id,
        transaction_amount,
        transaction_date,
        transaction_type,

        location_id,
        device_id,
        ip_address,

        nmerchant_id,
        channel_id,

        customer_age,
        occupation_id,

        transaction_duration,
        login_attempts,

        account_balance,

        previous_transaction_date

    )
    VALUES %s
    """

    execute_values(
        cur,
        sql,
        rows,
        page_size=1000
    )

    print(
        f"{len(rows):,} transactions loaded."
    )


def main():

    conn = psycopg2.connect(
        **DB_CONFIG
    )

    try:

        cur = conn.cursor()

        generate_transactions(cur)

        conn.commit()

        print(
            "Transaction load completed."
        )

    except Exception as e:

        conn.rollback()

        print(
            f"ERROR: {e}"
        )

        raise

    finally:

        conn.close()


if __name__ == "__main__":
    main()