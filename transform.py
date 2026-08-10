import logging

logger = logging.getLogger(__name__)

def transform(oltp_row, lookups):
    fact_rows = []
    skipped = 0
    for row in oltp_row:
        transaction_id = row["transaction_id"]  

        date_key = int(row["transaction_date"].strftime("%Y%m%d")) # Output: '20260709' 
        if date_key not in lookups["date"]:
            logger.warning(f"transaction {transaction_id}: date_key {date_key} outside of dim_date range — skipped")
            skipped += 1
            continue

        transaction_date = row["transaction_date"]
        time_key = (transaction_date.hour * 100) + (transaction_date.minute // 15) * 15
        if time_key not in lookups["time"]:
            logger.warning(f"transaction {transaction_id}: time_key {time_key} outside of dim_time range — skipped")
            skipped += 1
            continue

        account_key = lookups["account"].get(row["naccount_id"]) 
        if account_key is None: 
            logger.warning(f"transaction {transaction_id}: account_id {row['account_id']} not in dim_account — skipped")
            skipped += 1
            continue

        location_key = lookups["location"].get(row["location_id"]) 
        if location_key is None:
            logger.warning(f"transaction {transaction_id}: vehicle_id {row['location_id']} not in dim_location— skipped")
            skipped += 1
            continue
        

        channel_key = lookups["channel"].get(row["channel_id"])
        if channel_key is None:
            logger.warning(f"transaction {transaction_id}: channel_id {row['channel_id']} not in dim_channel — skipped")
            skipped += 1
            continue

        merchant_key = lookups["merchant"].get(row["nmerchant_id"])
        if merchant_key is None:
            logger.warning(f"transaction {transaction_id}: pickup_location_id {row['nmerchant_id']} not in dim_merchant — skipped")
            skipped += 1
            continue

        # customer_key = lookups["customer"].get((row["customer_age"],row["occupation_id"]))
        # if customer_key is None:
        #     logger.warning(f"transaction {transaction_id}: occupation_id {row['customer_age']} not in dim_customer — skipped")
        #     skipped += 1
        #     continue

        # computed column
        transaction_amount = row['transaction_amount'] or 0
        device_id = row["device_id"] or ""
        ip_address = row["ip_address"] or ""
        transaction_type = row["transaction_type"] or ""
        account_balance  = row["account_balance"] or 0.00
        previous_transaction_date = row["previous_transaction_date"] 
        transaction_duration = row["transaction_duration"] or 0
        login_attempts = row["login_attempts"] or 0

        transaction_duration = row["transaction_duration"] or 0
        login_attempts = row["login_attempts"] or 0

        # Fraud Indicators
        fraud_score = 0
        fraud_reasons = []

        # Rule 1: High Amount

        if transaction_amount >= 100000:
            fraud_score += 10
            fraud_reasons.append("HIGH_AMOUNT")

        # Rule 2: Multiple Login Attempts
        if login_attempts >= 3:
            fraud_score += 10
            fraud_reasons.append("MULTIPLE_LOGIN_ATTEMPTS")

        # Rule 3: Long Transaction Duration
        if transaction_duration > 300:
            fraud_score += 15
            fraud_reasons.append("LONG_TRANSACTION_DURATION")

        fraud_flag = fraud_score > 0
        fraud_reason = ("|".join(fraud_reasons)
            if fraud_reasons
                else None)

        
        # duration_minutes = None
        # if row["status"] == "completed" and row["completed_at"]:
        #     delta = row["completed_at"] - row["requested_at"]
        #     duration_minutes = round(delta.total_seconds() / 60, 1)
        fact_rows.append({
            "source_transaction_id":transaction_id,
            "account_key":          account_key,
            "location_key":         location_key,
            "channel_key":          channel_key,
            "merchant_key":         merchant_key,
            "date_key":             date_key,
            "time_key":             time_key,
            "transaction_date":     row["transaction_date"],
            "transaction_amount":   transaction_amount,
            "device_id":            device_id,
            "ip_address":           ip_address,
            "transaction_type":     transaction_type,
            "account_balance":      account_balance,
            "previous_transaction_date": previous_transaction_date,
            "login_attempts":       login_attempts,
            "transaction_duration": transaction_duration,

            # Fraud fields
            "fraud_score": fraud_score,
            "fraud_flag": fraud_flag,
            "fraud_reason": fraud_reason
        })

        # fact_rows.append({
        #     "source_trip_id":       trip_id,
        #     "date_key":             date_key,
        #     "time_key":             time_key,
        #     "driver_key":           driver_key,
        #     "vehicle_key":          vehicle_key,
        #     "passenger_key":        passenger_key,
        #     "pickup_location_key":  pickup_location_key,
        #     "dropoff_location_key": dropoff_location_key,
        #     "payment_method_key":   payment_method_key,
        #     "promo_code_key":       promo_code_key,
        #     "base_fare":            base_fare,
        #     "tip_amount":           tip_amount,
        #     "discount_amount":      discount_amount,
        #     "fare_amount":          fare_amount,
        #     "status":               row["status"],
        #     "distance_km":          row["distance_km"],
        #     "duration_minutes":     duration_minutes,
        #     "driver_rating":        row["driver_rating"],
        #     "passenger_rating":     row["passenger_rating"],
        #     "surge_multiplier":     surge_multiplier,
        #     "requested_at":         row["requested_at"],
        # })

    logger.info(f"Transformed {len(fact_rows)} rows, skipped {skipped}")
    return fact_rows
