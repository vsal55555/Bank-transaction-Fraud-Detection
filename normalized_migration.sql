DROP TABLE IF EXISTS bank_transations;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS merchants;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS channels ;
DROP TABLE IF EXISTS occupations ;


-- Cities that appear as initiated locations
CREATE TABLE locations (
    location_id   SERIAL        PRIMARY KEY,
    name     VARCHAR(100)   NOT NULL UNIQUE
);


-- accounts names, deduped from the flat table)
CREATE TABLE accounts (
    naccount_id     SERIAL        PRIMARY KEY,
    id       		VARCHAR(50)   NOT NULL
);

-- merchants
CREATE TABLE merchants (
    nmerchant_id     SERIAL        PRIMARY KEY,
    name          VARCHAR(50)  NOT NULL
);

CREATE TABLE channels (
	channel_id SERIAL PRIMARY KEY,
	name 	   VARCHAR(50) NOT NULL  
);

CREATE TABLE occupations (
    occupation_id   SERIAL        PRIMARY KEY,
    name     VARCHAR(50)   NOT NULL UNIQUE
);
-- ─────────────────────────────────────────────────────────────────
-- STEP 2: Create the bank_transactions table with foreign keys
-- ─────────────────────────────────────────────────────────────────

CREATE TABLE bank_transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    naccount_id 	INTEGER 	NOT NULL	REFERENCES accounts(naccount_id),
    transaction_amount NUMERIC(18,2) NOT NULL	CHECK (transaction_amount >= 0),
    transaction_date TIMESTAMP NOT NULL,
    transaction_type VARCHAR(20) NOT NULL	CHECK (transaction_type IN ('DEBIT','CREDIT')),
    location_id 	INTEGER		NOT NULL	REFERENCES locations(location_id),
    device_id VARCHAR(20)	NOT NULL,
    ip_address INET			NOT NULL,
    
    nmerchant_id    INTEGER	NOT NULL 	REFERENCES merchants(nmerchant_id),
    channel_id INTEGER		NOT NULL 		REFERENCES channels(channel_id),
    customer_age INTEGER,
    occupation_id  	INTEGER REFERENCES occupations(occupation_id),
    transaction_duration      INTEGER,
    login_attempts            INTEGER,
    account_balance NUMERIC(18,2),  
	previous_transaction_date TIMESTAMP
);

---- migration 

INSERT INTO locations (name)
SELECT
	DISTINCT INITCAP(TRIM(REGEXP_REPLACE(t.location, '\s+', ' ', 'g')))
FROM
	transactions t;
    


INSERT INTO accounts (id)
SELECT
	DISTINCT TRIM(REGEXP_REPLACE(t.account_id, '\s+', ' ', 'g'))
FROM
	transactions t;

INSERT INTO merchants (name)
SELECT
	DISTINCT REGEXP_REPLACE(t.merchant_id, '\s+', ' ', 'g')
FROM
	transactions t;

INSERT INTO channels (name)
select DISTINCT channel FROM transactions
WHERE channel IS NOT NULL;


INSERT INTO occupations (name)
select DISTINCT customer_occupation FROM transactions
WHERE customer_occupation IS NOT NULL ;

INSERT INTO bank_transactions (
    transaction_id,
    naccount_id,
    transaction_amount,
    transaction_date,
    transaction_type,
    location_id,
    device_id ,
    ip_address,
    
    nmerchant_id,
    channel_id ,
    customer_age,
    occupation_id,
    transaction_duration,
    login_attempts,
    account_balance,  
	previous_transaction_date
)
SELECT 
transaction_id,
(SELECT  naccount_id 
	FROM accounts a 
	 WHERE a.id = TRIM(REGEXP_REPLACE(t.account_id, '\s+', ' ', 'g'))) naccount_id,
	 transaction_amount,
	 transaction_date,
	 UPPER(transaction_type),
	 (SELECT  location_id  
		FROM locations l
	 WHERE l.name = t.location ) location_id,
	 device_id,
	 ip_address,
(SELECT  nmerchant_id 
		FROM merchants m
	 WHERE m.name = REGEXP_REPLACE(t.merchant_id, '\s+', ' ', 'g')) nmerchant_id, 
(SELECT  channel_id  
		FROM channels c
		WHERE c.name = t.channel  ) channel_id,
customer_age,
(SELECT  occupation_id  
		FROM occupations o  
		WHERE o.name = t.customer_occupation) occupation_id,
transaction_duration,
login_attempts,
account_balance,
previous_transaction_date
FROM transactions t;


--SELECT * FROM transactions ORDER BY transaction_date desc;
SELECT * FROM bank_transactions ORDER BY transaction_date desc;
SELECT count(naccount_id) FROM bank_transactions;
SELECT count(*) FROM accounts;
SELECT * FROM locations;


SELECT
		t.transaction_id,
		t.naccount_id,
		transaction_amount,
		transaction_date,
		t.transaction_type,
		t.customer_age,
		t.transaction_duration,
		t.login_attempts,
		t.account_balance,
        t.location_id,
        t.channel_id,
        t.nmerchant_id,
        t.occupation_id
    FROM  bank_transactions t
    ORDER BY t.transaction_date
