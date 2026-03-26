import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.graph_objects as go
import joblib

# ---------- Page Config ----------
st.set_page_config(page_title="Blinkit Decision Platform", layout="wide")

# ---------- Session ----------
if "page" not in st.session_state:
    st.session_state.page = "Analytics Dashboard"

# ---------- Sidebar ----------
st.sidebar.markdown("## Navigation")

def nav_button(label):
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = label

nav_button("Analytics Dashboard")
nav_button("Delivery Risk Calculator")
nav_button("AI Business Assistant")

page = st.session_state.page

# =========================================================
# ANALYTICS DASHBOARD
# =========================================================
if page == "Analytics Dashboard":

    st.title("Blinkit Analytics Dashboard")

    @st.cache_data
    def load_analytics():

        marketing = pd.read_csv("data_set/blinkit_marketing_performance.csv")
        orders = pd.read_csv("data_set/blinkit_orders.csv")

        # Date convert
        marketing["date"] = pd.to_datetime(marketing["date"])
        orders["order_date"] = pd.to_datetime(orders["order_date"])

        # Aggregate
        daily_marketing = marketing.groupby(marketing["date"].dt.date).agg({
            "spend": "sum"
        }).reset_index().rename(columns={"date": "report_date", "spend": "marketing_spend"})

        daily_orders = orders.groupby(orders["order_date"].dt.date).agg({
            "order_total": "sum",
            "order_id": "count"
        }).reset_index().rename(columns={
            "order_date": "report_date",
            "order_total": "revenue",
            "order_id": "order_count"
        })

        df = pd.merge(daily_orders, daily_marketing, on="report_date", how="outer")
        df.fillna(0, inplace=True)

        # IMPORTANT FIX
        df["report_date"] = pd.to_datetime(df["report_date"])

        # Add missing metrics (fake/simple calc for demo)
        df["roas"] = df["revenue"] / df["marketing_spend"].replace(0, 1)
        df["avg_delay"] = 5  # dummy
        df["estimated_profit"] = df["revenue"] * 0.2
        df["customer_satisfaction"] = 4.0

        return df

    df = load_analytics()

    # ---------- Date Filter ----------
    st.subheader("Date Filter")

    filter_type = st.radio(
        "Select Range",
        ["Last 7 Days", "Last 30 Days", "Custom Range"],
        horizontal=True
    )

    max_date = df["report_date"].max().date()

    if filter_type == "Last 7 Days":
        start_date = max_date - timedelta(days=7)
        end_date = max_date
    elif filter_type == "Last 30 Days":
        start_date = max_date - timedelta(days=30)
        end_date = max_date
    else:
        start_date = st.date_input("Start Date", df["report_date"].min().date())
        end_date = st.date_input("End Date", max_date)

    filtered_df = df[
        (df["report_date"].dt.date >= start_date) &
        (df["report_date"].dt.date <= end_date)
    ]

    # ---------- KPIs ----------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue", f"₹{filtered_df['revenue'].sum():,.0f}")
    c2.metric("ROAS", f"{filtered_df['roas'].mean():.2f}x")
    c3.metric("Delay", f"{filtered_df['avg_delay'].mean():.1f} mins")
    c4.metric("Profit", f"₹{filtered_df['estimated_profit'].sum():,.0f}")

    # ---------- Chart ----------
    fig = go.Figure()
    fig.add_trace(go.Bar(x=filtered_df["report_date"], y=filtered_df["marketing_spend"], name="Spend"))
    fig.add_trace(go.Scatter(x=filtered_df["report_date"], y=filtered_df["revenue"], name="Revenue"))
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DELIVERY RISK (SAFE VERSION)
# =========================================================
elif page == "Delivery Risk Calculator":

    st.title("Delivery Risk Calculator")

    st.info("Demo version (no DB used)")

    hour = st.slider("Order Hour", 0, 23, 18)
    is_peak = int(hour in [18,19,20,21])

    if is_peak:
        st.warning("Medium Risk ⚠️")
    else:
        st.success("Low Risk ✅")

# =========================================================
# AI ASSISTANT (SAFE)
# =========================================================
elif page == "AI Business Assistant":

    st.title("AI Business Assistant")

    question = st.chat_input("Ask question")

    if question:
        st.write("🤖 This is demo response (AI disabled for now)")
