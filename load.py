import logging

logger = logging.getLogger(__name__)

def load_dim_location(conn,location_data):
    insert_dim_location_sql = """
 INSERT INTO dim_location
    (location_id, city_name)
    VALUES ( %(location_id)s ,
             %(name)s
            )
    ON CONFLICT (location_id) DO NOTHING
"""
    try:
        with conn.cursor() as curr:
            curr.executemany(insert_dim_location_sql, location_data)
            logger.info(f"{curr.rowcount} inserted to dim_location")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(str(e))
        raise

def load_dim_channel(conn, channel_data):
    insert_dim_channel_sql = """
 INSERT INTO dim_channel
    (channel_id, channel_name)
    VALUES ( %(channel_id)s,
             %(name)s
            )
    ON CONFLICT (channel_id) DO NOTHING
"""
    try:
        with conn.cursor() as curr:
            curr.executemany(insert_dim_channel_sql, channel_data)
            logger.info(f"{curr.rowcount} inserted to dim_channel")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(str(e))
        raise

def load_dim_merchant(conn, merchant_data):
    insert_dim_merchant_sql = """
 INSERT INTO dim_merchant
    (nmerchant_id, merchant_name)
    VALUES ( %(nmerchant_id)s,
             %(name)s
            )
    ON CONFLICT (nmerchant_id) DO NOTHING
"""
    try:
        with conn.cursor() as curr:
            curr.executemany(insert_dim_merchant_sql, merchant_data)
            logger.info(f"{curr.rowcount} inserted to dim_merchant")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(str(e))
        raise


def load_dim_occupation(conn, occupation_data):
    insert_dim_occupation_sql = """
 INSERT INTO dim_occupation
    (occupation_id, occupation_name)
    VALUES ( %(occupation_id)s,
             %(name)s
            )
    ON CONFLICT (occupation_id) DO NOTHING
"""
    try:
        with conn.cursor() as curr:
            curr.executemany(insert_dim_occupation_sql, occupation_data)
            logger.info(f"{curr.rowcount} inserted to dim_occupation")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(str(e))
        raise


def load_dim_account_data(conn, accounts_data):
    insert_dim_account_sql = """
 INSERT INTO dim_account
    (naccount_id, account_name)
    VALUES ( %(naccount_id)s,
             %(id)s
            )
    ON CONFLICT (naccount_id) DO NOTHING
"""
    try:
        with conn.cursor() as curr:
            curr.executemany(insert_dim_account_sql, accounts_data)
            logger.info(f"{curr.rowcount} inserted to dim_account")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(str(e))
        raise


def load_dim_promo_code(conn, promo_code_data):
    insert_dim_promo_code_sql = """
 INSERT INTO dim_promo_code
    (promo_code_id, code, discount_type, discount_value, is_active)
    VALUES ( %(promo_code_id)s,
             %(code)s,
             %(discount_type)s,
             %(discount_value)s,
             %(is_active)s
            )
    ON CONFLICT (promo_code_id) DO NOTHING
"""
    try:
        with conn.cursor() as curr:
            curr.executemany(insert_dim_promo_code_sql, promo_code_data)
            logger.info(f"{curr.rowcount} inserted to dim_promo_code")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(str(e))
        raise


def load_fact_transactions(conn, fact_data):
    insert_fact_transactions_sql = """
 INSERT INTO fact_transactions
    (source_transaction_id,account_key,location_key,channel_key,merchant_key,
    date_key,transaction_date,transaction_amount,device_id,ip_address,transaction_type,account_balance,previous_transaction_date,login_attempts,
    transaction_duration,fraud_score,fraud_flag,fraud_reason)
    VALUES ( %(source_transaction_id)s,
             %(account_key)s,
             %(location_key)s,
             %(channel_key)s,
             %(merchant_key)s,
             %(date_key)s,
             %(transaction_date)s,
             %(transaction_amount)s,
             %(device_id)s,
             %(ip_address)s,
            %(transaction_type)s,
            %(account_balance)s,
            %(previous_transaction_date)s,
            %(login_attempts)s,
            %(transaction_duration)s,
            %(fraud_score)s,
            %(fraud_flag)s,
            %(fraud_reason)s
            )
    ON CONFLICT DO NOTHING
"""
    if not fact_data:
        logger.info("No fact rows to load — skipping")
        return
    try:
        with conn.cursor() as curr:
            curr.executemany(insert_fact_transactions_sql, fact_data)
            logger.info(f"{curr.rowcount} inserted to fact_transactions")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(str(e))
        raise
