from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def extract(conn,sql, params=None):
    try:
        with conn.cursor(cursor_factory =RealDictCursor ) as curr:
            curr.execute(sql,params)
            rows = curr.fetchall()
            logger.info(f"Extracted {len(rows)} from the table")
        return rows
    except Exception as e:
        logger.error(str(e))
        raise 
    
def extract_location(conn):
     extract_location_sql = """
    SELECT
        location_id ,
        name
    FROM
        locations l ;
    """
     return extract(conn,extract_location_sql)

    


def extract_channel(conn):
    extract_channel_sql = """
     SELECT
        channel_id,
        name
    FROM
        channels;
    """
    return extract(conn, extract_channel_sql)



def extract_merchant(conn):
    extract_merchant_sql = """
    SELECT
        nmerchant_id,
        name
    FROM
        merchants p;
    """
    return extract(conn, extract_merchant_sql)


def extract_occupation(conn):
    extract_occupation_sql = """
    SELECT
        occupation_id,
        name
    FROM
        occupations o;
    """
    return extract(conn, extract_occupation_sql)



def extract_accounts(conn):
    extract_accounts_sql = """
    SELECT
        naccount_id,
        id
    FROM
        accounts ac;
    """
    return extract(conn, extract_accounts_sql)



def extract_transactions_full(conn):
    extract_alltransactions_sql = """
      SELECT
        t.transaction_id,
		t.naccount_id,
		t.transaction_amount,
		t.transaction_date,
		t.transaction_type,
		t.customer_age,
		t.transaction_duration,
		t.login_attempts,
		t.account_balance,
        t.location_id,
        t.channel_id,
        t.nmerchant_id,
        t.occupation_id,
        t.ip_address,
        t.previous_transaction_date,
        t.device_id
    FROM  bank_transactions t
    ORDER BY t.transaction_date
        """
    return extract(conn,extract_alltransactions_sql)

def extract_transactions_incremental(conn, watermark):
    extract_newtransactions_sql = """
      SELECT
        t.transaction_id,
		t.naccount_id,
		t.transaction_amount,
		t.transaction_date,
		t.transaction_type,
		t.customer_age,
		t.transaction_duration,
		t.login_attempts,
		t.account_balance,
        t.location_id,
        t.channel_id,
        t.nmerchant_id,
        t.occupation_id,
        t.ip_address,
        t.previous_transaction_date,
        t.device_id
    FROM  bank_transactions t
    where t.transaction_date > %(watermark)s
    ORDER BY t.transaction_date
        """
    return extract(conn,extract_newtransactions_sql,watermark)

def extract_lookup_dim(conn):
    logger.info("Loading lookup table into memmory")
    lookup = {}
    with conn.cursor() as curr:
        
        curr.execute("SELECT location_id, location_key FROM dim_location")
        lookup["location"] = {r[0]:r[1] for r in curr.fetchall()}

        curr.execute("SELECT channel_id, channel_key FROM dim_channel")
        lookup["channel"] = {r[0]:r[1] for r in curr.fetchall()}
        
        curr.execute("SELECT nmerchant_id, merchant_key FROM dim_merchant")
        lookup["merchant"] = {r[0]:r[1] for r in curr.fetchall()}
        
        curr.execute("SELECT naccount_id, account_key FROM dim_account")
        lookup["account"] = {r[0]:r[1] for r in curr.fetchall()}

        curr.execute("SELECT occupation_id, occupation_key FROM dim_occupation")
        lookup["occupation"] = {r[0]:r[1] for r in curr.fetchall()}

        # curr.execute("SELECT occupation_key,age_key,customer_key FROM dim_customer")
        # lookup["customer"] = {(row[0],row[0]):row[1]
        #                             for row in curr.fetchall()}

        curr.execute("SELECT date_key FROM dim_date")
        lookup["date"] = {r[0]: True for r in curr.fetchall()}

        curr.execute("SELECT time_key FROM dim_time")
        lookup["time"] = {r[0]: True for r in curr.fetchall()}
    return lookup

def get_watermark(conn) -> datetime:
    """
    Return the most recent requested_at already loaded in the warehouse.
    Falls back to 2000-01-01 on an empty fact table so the first run
    behaves as a full load without special-casing.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(
                MAX(transaction_date),
                '2000-01-01'::TIMESTAMP
            )
            FROM fact_transactions
        """)
        watermark = cur.fetchone()[0]
    logger.info(f"Watermark: {watermark}")
    return watermark