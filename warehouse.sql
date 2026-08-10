CREATE DATABASE OLAP_DB;

-- =================================================================
-- NORMALIZED RIDE-SHARING SCHEMA
-- Normal Forms: 1NF, 2NF, 3NF compliant
-- =================================================================
CREATE TABLE dim_date (
    date_key        INTEGER      PRIMARY KEY,      -- e.g. 20240315
    full_date       DATE         NOT NULL UNIQUE,
    year            SMALLINT     NOT NULL,
    quarter         SMALLINT     NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month           SMALLINT     NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name      VARCHAR(10)  NOT NULL,          -- 'January' … 'December'
    week_of_year    SMALLINT     NOT NULL,          -- ISO week 1-53
    day_of_week     SMALLINT     NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sun
    day_name        VARCHAR(10)  NOT NULL,          -- 'Sunday' … 'Saturday'
    is_weekend      BOOLEAN      NOT NULL
);

-- ─────────────────────────────────────────────────────────────────────────────
-- dim_time
-- Pre-populated with every 15-minute bucket (96 rows).
-- time_key format: HHMM integer rounded down to nearest 15 min.
-- Example: a trip requested at 14:37 gets time_key = 1430.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE dim_time (
    time_key        INTEGER      PRIMARY KEY,   -- HHMM, e.g. 1430 = 2:30 PM
    hour            SMALLINT     NOT NULL CHECK (hour BETWEEN 0 AND 23),
    minute_bucket   SMALLINT     NOT NULL CHECK (minute_bucket IN (0, 15, 30, 45)),
    time_label      VARCHAR(8)   NOT NULL,      -- '14:30'
    time_of_day     VARCHAR(12)  NOT NULL,      -- 'Morning' / 'Afternoon' / 'Evening' / 'Night'
    is_rush_hour    BOOLEAN      NOT NULL       -- TRUE for 7-9am and 5-8pm weekday proxy
);

CREATE TABLE dim_occupation (
    occupation_key SERIAL PRIMARY KEY,
    occupation_id INTEGER UNIQUE,
    occupation_name VARCHAR(100)
);

CREATE TABLE dim_account (
    account_key SERIAL PRIMARY KEY,
    naccount_id INTEGER NOT NULL UNIQUE,
    account_name VARCHAR(100),
    status VARCHAR(20),
    created_at       TIMESTAMP,
    tenure_bucket   VARCHAR(20)                 -- '0-6 months' / '6-12 months' / '1-2 years' / '2+ years'
);

CREATE TABLE dim_channel (
    channel_key SERIAL PRIMARY KEY,
    channel_id INTEGER UNIQUE NOT NULL,
    channel_name VARCHAR(50)
);

CREATE TABLE dim_merchant (
    merchant_key SERIAL PRIMARY KEY,
    nmerchant_id INTEGER UNIQUE NOT NULL,
    merchant_name VARCHAR(100),
    address VARCHAR(100)
);

CREATE TABLE dim_location (
    location_key SERIAL PRIMARY KEY,
    location_id INTEGER UNIQUE,
    city_name       VARCHAR(100),
    state_province  VARCHAR(100),
    country         VARCHAR(100),
    region          VARCHAR(30),   -- derived: 'Northeast' / 'West' / 'South' / 'Midwest' / 'International'
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6)
);




--------------------------


--Populate dim_date
-- Generates one row per calendar day from 2023-01-01 to 2026-12-31.
-- Covers the full range of the sample dataset with room for future trips.
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO dim_date (
    date_key, full_date, year, quarter, month,
    month_name, week_of_year, day_of_week, day_name, is_weekend
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER                  AS date_key,
    d::DATE                                          AS full_date,
    EXTRACT(YEAR    FROM d)::SMALLINT                AS year,
    EXTRACT(QUARTER FROM d)::SMALLINT                AS quarter,
    EXTRACT(MONTH   FROM d)::SMALLINT                AS month,
    TRIM(TO_CHAR(d, 'Month'))                        AS month_name,   -- trim trailing spaces!
    EXTRACT(WEEK    FROM d)::SMALLINT                AS week_of_year,
    EXTRACT(DOW     FROM d)::SMALLINT                AS day_of_week,  -- 0=Sun, 6=Sat
    TRIM(TO_CHAR(d, 'Day'))                          AS day_name,     -- trim trailing spaces!
    EXTRACT(DOW FROM d) IN (0, 6)                    AS is_weekend
FROM generate_series(
    '2023-01-01'::TIMESTAMP,
    '2026-12-31'::TIMESTAMP,
    '1 day'::INTERVAL
) AS d;


-- ─────────────────────────────────────────────────────────────────────────────
-- Populate dim_time
-- 96 rows — one per 15-minute bucket across 24 hours.
-- ETL maps each trip's requested_at minute to the nearest 15-min bucket.
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO dim_time (time_key, hour, minute_bucket, time_label, time_of_day, is_rush_hour)
SELECT
    (h * 100 + m)::INTEGER                               AS time_key,   -- e.g. 1430
    h::SMALLINT                                          AS hour,
    m::SMALLINT                                          AS minute_bucket,
    LPAD(h::TEXT, 2, '0') || ':' || LPAD(m::TEXT, 2, '0') AS time_label, -- '14:30'
    CASE
        WHEN h BETWEEN  6 AND 11 THEN 'Morning'
        WHEN h BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN h BETWEEN 17 AND 20 THEN 'Evening'
        ELSE                          'Night'
    END                                                  AS time_of_day,
    (h BETWEEN 7 AND 8) OR (h BETWEEN 17 AND 19)        AS is_rush_hour  -- 7–9am, 5–8pm
FROM
    generate_series(0, 23) AS h,
    generate_series(0, 45, 15) AS m
ORDER BY h, m;


CREATE TABLE fact_transactions (

    transaction_key 			  BIGSERIAL 	PRIMARY KEY,
    source_transaction_id 		  VARCHAR(20) 	NOT NULL UNIQUE,

    date_key 					  INTEGER		NOT NULL REFERENCES dim_date(date_key),
    account_key 				  INTEGER		NOT NULL REFERENCES dim_account(account_key),
    merchant_key 				  INTEGER 		NOT NULL REFERENCES dim_merchant(merchant_key),
    location_key 				  INTEGER 				 REFERENCES dim_location(location_key),
    channel_key 				  INTEGER 				 REFERENCES dim_channel(channel_key),
    device_id 					  VARCHAR(20)	NOT NULL,
    ip_address 					  INET			NOT NULL,
	
    transaction_type 			  VARCHAR(20) 	NOT NULL	CHECK (transaction_type IN ('DEBIT','CREDIT')),
    
    transaction_amount NUMERIC(18,2) NOT NULL,
    account_balance NUMERIC(18,2),
	
    transaction_duration INTEGER,
    login_attempts INTEGER,
    
    fraud_score NUMERIC(5,2),
    fraud_flag BOOLEAN,
    fraud_reason VARCHAR(100),

    transaction_date           TIMESTAMP       NOT NULL,   -- kept for incremental watermark queries
    previous_transaction_date TIMESTAMP
);

