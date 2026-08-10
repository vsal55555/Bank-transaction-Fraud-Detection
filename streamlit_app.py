import streamlit as st

from dashboards import (
    fraud_trends,
    fraud_locations,
    fraud_accounts,
    fraud_merchants,
    fraud_reasons,
    fraud_heatmap,
    high_risk_transactions,
    executive_dashboard
)

st.set_page_config(
    page_title="Bank Fraud Dashboard",
    page_icon="🏦",
    layout="wide"
)

st.sidebar.title(
    "Bank Fraud Dashboard"
)
#Add menu items:
page = st.sidebar.radio(
    "Select Report",

    [
        "Executive Dashboard",
        "Fraud Trends",
        "Fraud Locations",
        "Fraud Accounts",
        "Fraud Merchants",
        "Fraud Reasons",
        "High Risk Transactions",
        "Fraud Heatmap"
    ]
)
#Add routing:

if page == "Fraud Trends":

    fraud_trends.render()

elif page == "Fraud Locations":

    fraud_locations.render()

elif page == "Fraud Accounts":

    fraud_accounts.render()

elif page == "Fraud Merchants":

    fraud_merchants.render()

elif page == "High Risk Transactions":

    high_risk_transactions.render()

elif page == "Executive Dashboard":

    executive_dashboard.render()

elif page == "Fraud Heatmap":

    fraud_heatmap.render()

elif page == "Fraud Reasons":

    fraud_reasons.render()