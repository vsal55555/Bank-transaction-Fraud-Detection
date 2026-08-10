
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
import time
import argparse
from datetime import datetime
from etl import extract_promo_code
from quality import DataQualityError, run_quality_checks
from transform import transform
from logger_config import setup_logger

from load import (
    load_dim_account_data,
    load_dim_channel,
    load_dim_location,
    load_dim_merchant,
    load_dim_occupation,
    load_fact_transactions
)

from extract import (
    extract_channel,
    extract_accounts,
    extract_location,
    extract_lookup_dim, 
    extract_merchant, 
    extract_occupation,
    extract_transactions_full,
    extract_transactions_incremental,
    get_watermark
)

from config import (SOURCE_DB_CONFIG, DEST_DB_CONFIG)


def parse_args():
    parser = argparse.ArgumentParser(description="Rides ETL pipeline")
    parser.add_argument(
        "--full-reload",
        action="store_true",
        help="Truncate warehouse and reload all data (default: incremental)"
    )
    args, _ = parser.parse_known_args()
    return args

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
)
logger = logging.getLogger(__name__)

# logger.info(f"SRC_DB_HOST={SOURCE_DB_CONFIG['host']}")
# logger.info(f"SRC_DB_NAME={SOURCE_DB_CONFIG['dbname']}")

# logger.info(f"SRC_DB_USER={SOURCE_DB_CONFIG['user']}")
# logger.info(f"Password Length={len(SOURCE_DB_CONFIG['password'])}")
def validate_data(fact_rows, logger):
    start = time.time()
    run_quality_checks(fact_rows)
    logger.info(f"Quality Check completed on {time.time() - start:.2f}s")

def main():

    src_conn = None
    dst_conn = None
    try:
        logger = setup_logger()
        logger.info("Pipeline Started")
        pipeline_start = time.time()
        args = parse_args()
        mode = 'FULL' if args.full_reload else 'INCREMENTAL'
        """
        Extract all dimension data from the source DB and load them into the target DB.
        """

        src_conn = psycopg2.connect(**SOURCE_DB_CONFIG)
        dst_conn = psycopg2.connect(**DEST_DB_CONFIG)

    
        time0 = time.time()
        location_data = extract_location(src_conn)
        load_dim_location(dst_conn, location_data)

        channel_data = extract_channel(src_conn)
        load_dim_channel(dst_conn, channel_data)

        merchant_data = extract_merchant(src_conn)
        load_dim_merchant(dst_conn, merchant_data)

        occupation_data = extract_occupation(src_conn)
        load_dim_occupation(dst_conn, occupation_data)

        accounts_data = extract_accounts(src_conn)
        load_dim_account_data(dst_conn, accounts_data)

        #promo_code_data = extract_promo_code(src_conn)
        #load_dim_promo_code(dst_conn, promo_code_data)
        logger.info(f"Dimention table load completed on {time.time() - time0:.2f}s")
        
        time0 = time.time()
        lookups = extract_lookup_dim(dst_conn)
        logger.info(f"Lookup table extraction completed on {time.time() - time0:.2f}s")
        
        #create a function to Read   Watermark
        #When watermark = None,i.e Null watermark. ETL should interpret None as Initial load and load ALL trips.
        time0 = time.time()
        if mode == 'INCREMENTAL':
            watermark = get_watermark(dst_conn)
            rows = extract_transactions_incremental(src_conn,{"watermark":watermark})
        else:
            rows = extract_transactions_full(src_conn)
        logger.info(f"Transactions extraction  from OLTP completed on {time.time() - time0:.2f}s")

        time0 = time.time()
        fact_rows = transform(rows, lookups)
        logger.info(f"Transformation completed on {time.time() - time0:.2f}s")

        validate_data(fact_rows, logger)


        time0 = time.time()
        load_fact_transactions(dst_conn, fact_rows)
        logger.info(f"Fact Transactions load completed on {time.time() - time0:.2f}s")
        logger.info(f"Pipeline complete in "f"{time.time() - pipeline_start:.2f}s")

    except DataQualityError as e:
        logger.error(f"QUALITY CHECK FAILED: {str(e)}")
        logger.error(f"Pipeline Aborted")
        return
    
    except psycopg2.OperationalError as e:
       raise ConnectionError("Source database authentication failed. "
                             "Please verify SRC_DB_USER and SRC_DB_PASSWORD.") from e

    except Exception as e:
        logger.exception(f"Pipeline Failed: {e}")
        


    finally:
        if src_conn:
            src_conn.close()

        if dst_conn:
            dst_conn.close()

        
if __name__ == "__main__":
        main()

