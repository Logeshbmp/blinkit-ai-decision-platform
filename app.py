import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import timedelta
import plotly.graph_objects as go
import joblib
from rag_engine import ask_business_question


# ---------- Page Config ----------
st.set_page_config(
    page_title="Blinkit Decision Platform",
    layout="wide"
)

load_dotenv()

# ---------- DB Connection ----------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ---------- Session State ----------
if "page" not in st.session_state:
    st.session_state.page = "Analytics Dashboard"


# ---------- Sidebar Navigation ----------
st.sidebar.markdown("## Navigation")

def nav_button(label):
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = label

nav_button("Analytics Dashboard")
nav_button("Delivery Risk Calculator")
nav_button("AI Business Assistant")

page = st.session_state.page


# =========================================================
#  Analytics Dashboard
# =========================================================
if page == "Analytics Dashboard":

    st.title("Blinkit Analytics Dashboard")

    @st.cache_data
    def load_analytics():
        df = pd.read_sql("SELECT * FROM master_analytics_view", engine)
        df["report_date"] = pd.to_datetime(df["report_date"])
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


    # ---------- KPI Metrics ----------
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Revenue", f"₹{filtered_df['revenue'].sum():,.0f}")

    with c2:
        st.metric("Avg ROAS", f"{filtered_df['roas'].mean():.2f}x")

    with c3:
        st.metric("Avg Delay", f"{filtered_df['avg_delay'].mean():.1f} mins")

    with c4:
        st.metric("Total Profit", f"₹{filtered_df['estimated_profit'].sum():,.0f}")


    # ---------- Revenue vs Marketing ----------
    st.subheader("Revenue vs Marketing Spend")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=filtered_df["report_date"],
        y=filtered_df["marketing_spend"],
        name="Marketing Spend"
    ))

    fig.add_trace(go.Scatter(
        x=filtered_df["report_date"],
        y=filtered_df["revenue"],
        mode="lines+markers",
        name="Revenue"
    ))

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)


    # ---------- Revenue Trend ----------
    st.subheader("Daily Revenue Trend")

    rev_fig = go.Figure()

    rev_fig.add_trace(go.Scatter(
        x=filtered_df["report_date"],
        y=filtered_df["revenue"],
        mode="lines+markers",
        name="Revenue"
    ))

    rev_fig.update_layout(height=400)

    st.plotly_chart(rev_fig, use_container_width=True)


    # ---------- Customer Satisfaction ----------
    st.subheader("Customer Satisfaction Trend")

    rating_fig = go.Figure()

    rating_fig.add_trace(go.Scatter(
        x=filtered_df["report_date"],
        y=filtered_df["customer_satisfaction"],
        mode="lines+markers",
        name="Rating"
    ))

    rating_fig.update_layout(height=400)

    st.plotly_chart(rating_fig, use_container_width=True)


    # ---------- Orders vs Revenue ----------
    st.subheader("Orders vs Revenue")

    order_fig = go.Figure()

    order_fig.add_trace(go.Bar(
        x=filtered_df["report_date"],
        y=filtered_df["order_count"],
        name="Orders"
    ))

    order_fig.add_trace(go.Scatter(
        x=filtered_df["report_date"],
        y=filtered_df["revenue"],
        mode="lines+markers",
        name="Revenue"
    ))

    order_fig.update_layout(height=450)

    st.plotly_chart(order_fig, use_container_width=True)



# =========================================================
# Delivery Risk Calculator (ML)
# =========================================================
elif page == "Delivery Risk Calculator":

    st.title("Delivery Risk Calculator")

    @st.cache_resource
    def load_delay_model():
        return joblib.load("data/delivery_delay_model.pkl")

    model = load_delay_model()

    @st.cache_data
    def load_orders():
        df = pd.read_sql("SELECT * FROM orders_with_customer", engine)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["order_hour"] = df["order_date"].dt.hour
        df["is_late"] = (df["delivery_status"] != "On Time").astype(int)
        return df

    ml_df = load_orders()

    area = st.selectbox("Area", sorted(ml_df["area"].unique()))
    hour = st.slider("Order Hour", 0, 23, 18)
    day = st.selectbox(
        "Day",
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    )

    day_num = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(day)

    is_weekend = int(day_num >= 5)
    is_peak = int(hour in [18,19,20,21])

    area_rate = ml_df.groupby("area")["is_late"].mean().get(area, 0)
    hour_rate = ml_df.groupby("order_hour")["is_late"].mean().get(hour, 0)
    area_hour_rate = ml_df.groupby(["area","order_hour"])["is_late"].mean().get((area, hour), 0)

    X = pd.DataFrame([{
        "order_hour": hour,
        "day_of_week": day_num,
        "is_weekend": is_weekend,
        "is_peak_hour": is_peak,
        "area_delay_rate": area_rate,
        "area_hour_delay_rate": area_hour_rate,
        "hour_delay_rate": hour_rate
    }])

    prob = model.predict_proba(X)[0][1]

    if prob >= 0.7:
        st.error(f"High Delay Risk ({prob:.0%})")
    elif prob >= 0.4:
        st.warning(f"Medium Delay Risk ({prob:.0%})")
    else:
        st.success(f"Low Delay Risk ({prob:.0%})")



# =========================================================
# AI Business Assistant
# =========================================================
elif page == "AI Business Assistant":

    st.title("AI Business Assistant")

    st.write("Ask business questions based on customer feedback")

    question = st.chat_input("Ask a business question")

    if question:

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):

            with st.spinner("Analyzing feedback..."):

                answer = ask_business_question(question)

                st.write(answer)
