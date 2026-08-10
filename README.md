# 🏦 Bank Transaction Fraud Detection

## Overview

Bank Transaction Fraud Detection is an end-to-end Data Engineering project that ingests banking transaction data from an OLTP database, applies fraud detection rules during transformation, loads curated data into a PostgreSQL Data Warehouse, orchestrates ETL workflows using Apache Airflow, sends automated fraud alerts via email, and visualizes fraud insights through Streamlit dashboards.

---

## 🎯 Project Objectives

- Build a scalable ETL pipeline using Python
- Implement incremental data loading using watermarking
- Design a Star Schema data warehouse
- Detect suspicious transactions using rule-based fraud scoring
- Orchestrate workflows with Apache Airflow
- Send automated fraud alert notifications
- Visualize fraud trends and KPIs using Streamlit

---
## 📂 Project Structure

```text
Bank-transaction-Fraud-Detection/

├── dags/
│   └── bank_fraud_etl_dag.py
│
├── dashboards/
│   ├── db.py
│   ├── executive_dashboard.py
│   ├── fraud_summary.py
│   ├── fraud_trends.py
│   ├── fraud_locations.py
│   ├── fraud_accounts.py
│   ├── fraud_merchants.py
│   ├── fraud_reasons.py
│   ├── fraud_heatmap.py
│   └── high_risk_transactions.py
│
├── extract.py
├── transform.py
├── quality.py
├── load.py
├── pipeline.py
│
├── streamlit_app.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture

```text
┌──────────────────────────────┐
│      PostgreSQL (OLTP)       │
│                              │
│  Raw Banking Transactions    │
└───────────────┬──────────────┘
                │
                │ Extract
                ▼

┌──────────────────────────────┐
│      Python ETL Pipeline     │
└───────────────┬──────────────┘
                │
                ▼

┌──────────────────────────────┐
│       Transformation Layer   │
│                              │
│ ✓ Data Validation            │
│ ✓ Data Quality Checks        │
│ ✓ Star Schema Mapping        │
│ ✓ Fraud Rule Evaluation      │
│ ✓ Fraud Score Calculation    │
│ ✓ Fraud Flag Creation        │
└───────────────┬──────────────┘
                │
                │ Load
                ▼

┌──────────────────────────────┐
│     PostgreSQL Warehouse     │
│           (OLAP)             │
│                              │
│ Fact Transactions            │
│ Dim Account                  │
│ Dim Location                 │
│ Dim Merchant                 │
│ Dim Channel                  │
└───────┬───────────────┬──────┘
        │               │
        ▼               ▼

┌───────────────┐   ┌─────────────┐
│   Airflow     │   │  Streamlit  │
│ Scheduler     │   │ Dashboard   │
└──────┬────────┘   └──────┬──────┘
       │                   │
       ▼                   ▼

┌───────────────┐   ┌─────────────┐
│ Fraud Alerts  │   │ KPIs        │
│ Email Reports │   │ Trends      │
└───────────────┘   │ Insights    │
                    └─────────────┘
```

---

## 🛠️ Technology Stack

### Database
- PostgreSQL

### Programming Language
- Python

### ETL
- Pandas
- Psycopg2

### Workflow Orchestration
- Apache Airflow

### Data Visualization
- Streamlit
- Plotly

### Containerization
- Docker

---

## 📊 Data Warehouse Design

### Fact Table

#### fact_transactions

Stores transaction-level information and fraud indicators.

```text
source_transaction_id
account_key
merchant_key
location_key
channel_key
date_key

transaction_amount

fraud_score
fraud_flag
fraud_reason
```

### Dimension Tables

```text
dim_account
dim_merchant
dim_location
dim_channel
dim_occupation
dim_date
```

---

## 🚨 Fraud Detection Rules

| Rule | Condition | Score |
|--------|------------|--------|
| HIGH_AMOUNT | transaction_amount >= 100000 | +10 |
| MULTIPLE_LOGIN_ATTEMPTS | login_attempts >= 3 | +10 |
| LONG_TRANSACTION_DURATION | transaction_duration > 300 | +15 |
| HIGH_VELOCITY | More than 5 transactions within 10 minutes | +30 |
| LOCATION_ANOMALY | Different location within a short period | +30 |

### Fraud Score Logic

```text
Fraud Score =
Sum of all applicable fraud rules
```

### Fraud Flag

```text
fraud_flag = TRUE
```

when one or more fraud rules are triggered.

---

## ✅ Data Quality Checks

Implemented data quality validations include:

- Row Count Validation
- Positive Transaction Amount Validation
- Null Key Validation
- Fraud Score Validation
- Fraud Flag Consistency Validation
- Transaction Type Validation

---

## 🔄 ETL Workflow

### Full Load

```bash
python pipeline.py --full-reload
```

### Incremental Load

Uses watermark-based extraction.

```sql
transaction_date > watermark
```

Benefits:

- Faster processing
- Reduced database load
- Production-friendly approach

---

## 🌬️ Airflow DAG

### Workflow

```text
run_pipeline
      ↓
check_fraud_transactions
      ↓
send_fraud_email
```

### Features

- Scheduled execution
- Incremental processing
- Fraud monitoring
- Email notifications

---

## 📧 Fraud Alert Emails

When fraud transactions are detected:

```text
Fraud Transactions
      ↓
Airflow
      ↓
Email Alert
      ↓
Analyst Notification
```

Email includes:

- Transaction ID
- Fraud Score
- Fraud Reason
- Transaction Amount

---

## 📈 Streamlit Dashboard

### Executive Dashboard
- Total Transactions
- Fraud Transactions
- Fraud Percentage
- Average Fraud Score

### Fraud Summary Dashboard
Overall fraud monitoring KPIs.
Track fraud activity over time.
Fraud distribution by city.
Accounts with highest fraud activity.
Merchants associated with the highest fraud cases.
Breakdown of fraud triggers.
Transactions with elevated fraud scores.
Geographic fraud visualization.



---


## ▶️ Run Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

Open:

```text
http://localhost:8501
```

---

## ▶️ Run Airflow

Initialize:

```bash
docker compose up airflow-init
```

Start Airflow:

```bash
docker compose up -d
```

Open:

```text
http://localhost:8080
```

---

## 🚀 Future Enhancements

- Machine Learning Fraud Prediction
- Kafka-Based Streaming Pipeline
- Real-Time Fraud Detection
- Power BI Integration
- SMS Fraud Alerts
- Risk Categorization Engine
- Fraud Anomaly Detection Models

---

## 👨‍💻 Author

**Bishal Shrestha**

Data Engineering Capstone Project

---
## 🎥 Project Demo

Watch the complete project demo here:

🔗 [click me!](https://drive.google.com/file/d/1OcVUw0rqakYn-jBi1MRUONSXBK8srKGy/view)
