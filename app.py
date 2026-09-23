import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="South African Insurance Claims Dashboard",
    layout="wide")

# ---------- Color palette ----------
PRIMARY = "#00C2CB"      # bright teal
ACCENT = "#FF6B6B"       # coral
GOLD = "#FFD166"         # warm gold
PALETTE = ["#00C2CB", "#FF6B6B", "#FFD166", "#8AC926", "#B388FF", "#FF9F1C", "#4CC9F0"]
BG = "#1E2230"            # page background
PANEL = "#2A3040"         # card/panel background

# ---------- Custom CSS ----------
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BG};
    }}
    h1, h2, h3, h4 {{
        color: {PRIMARY};
    }}
    p, span, label, li, div, .stMarkdown, .stCaption,
    .stSelectbox label, .stDateInput label, .stCheckbox label {{
        color: #F0F0F0 !important;
    }}
    div[data-testid="stMetric"] {{
        background-color: {PANEL};
        border: 1px solid #3A4155;
        border-left: 5px solid {ACCENT};
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}
    div[data-testid="stMetricValue"] {{
        color: {PRIMARY} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: #C5C9D3 !important;
    }}
      .stSelectbox div[data-baseweb="select"] {{
        background-color: {PANEL};
    }}
    .stSelectbox div[data-baseweb="select"] * {{
        color: #FFFFFF !important;
        background-color: {PANEL} !important;
    }}
    .stDateInput input {{
        background-color: {PANEL};
        color: #FFFFFF;
    }}
    .stDataFrame {{
        background-color: {PANEL};
    }}
    .stButton>button, .stDownloadButton>button {{
        background-color: {ACCENT};
        color: {BG};
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }}
    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: {PRIMARY};
        color: {BG};
    }}
    </style>
""", unsafe_allow_html=True)

# ----------Supabase Connection----------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

response = supabase.table("insurance_claims").select("*").execute()

claims_df = pd.DataFrame(response.data)
claims_df["claim_date"] = pd.to_datetime(claims_df["claim_date"])

st.title("South African Insurance Claims Dashboard")

st.markdown(
    """
    This dashboard provides real-time analysis of South African insurance claims data stored in a cloud database.

    Features include:
    - Claims monitoring
    - Province-level analysis
    - Claim type analysis
    - Status tracking
    - Trend analysis
    - Data export functionality
    """)
filtered_df = claims_df.copy()

col1, col2, col3, col4 = st.columns(4)

total_claims = len(filtered_df)
total_claim_amount = filtered_df["claim_amount"].sum()
average_claim_amount = filtered_df["claim_amount"].mean()
highest_claim = filtered_df["claim_amount"].max()

col1.metric("Total Claims",f"{total_claims:,}")

col2.metric("Total Claim Amount",f"R {total_claim_amount:,.2f}")

col3.metric("Average Claim Amount",f"R {average_claim_amount:,.2f}")

col4.metric("Highest Claim",f"R {highest_claim:,.2f}")

approval_rate = (
    len(filtered_df[filtered_df["claim_status"] 
        == "Approved"])
    / len(filtered_df)
    * 100 if len(filtered_df) > 0
    else 0)

col5 = st.columns(3)[0]

col5.metric(
    "Approval Rate",
    f"{approval_rate:.1f}%")

st.divider()

st.subheader("Filters")

selected_province = st.selectbox("Select Province", ["All"] + sorted(claims_df["province"].unique().tolist()))
selected_type = st.selectbox("Select Claim Type", ["All"] + sorted(claims_df["claim_types"].unique().tolist()))
selected_status = st.selectbox("Select Claim Status", ["All"] + sorted(claims_df["claim_status"].unique().tolist()))

start_date = st.date_input(
    "Start Date",
    claims_df["claim_date"].min())
end_date = st.date_input(
    "End Date",
    claims_df["claim_date"].max())

filtered_df = claims_df.copy()

if selected_province != "All":
    filtered_df = filtered_df[
    filtered_df["province"] ==
    selected_province]

if selected_type != "All":
    filtered_df = filtered_df[
    filtered_df["claim_types"] == 
    selected_type]

if selected_status != "All":
    filtered_df =filtered_df[
    filtered_df["claim_status"] ==
    selected_status]

filtered_df = filtered_df[(
    filtered_df["claim_date"] >=
    pd.to_datetime(start_date))
    &(filtered_df["claim_date"] <=
      pd.to_datetime(end_date))]

st.write(f"Filtered Records:{len(filtered_df)}")
    
if st.checkbox("Show Claims Data"):
    st.dataframe(filtered_df)

csv = filtered_df.to_csv(index=False)

st.header("Dashboard Visualisations")

st.subheader("Claims Analysis")

st.subheader("Claims by Province")

province_chart = (
    filtered_df.groupby("province")
    .size()
    .reset_index(name="claims")
)

province_fig = px.bar(
    province_chart,
    x="province",
    y="claims",
    color="province",
    color_discrete_sequence=PALETTE
)
province_fig.update_layout(showlegend=False, plot_bgcolor=BG, paper_bgcolor=BG, font_color="#F0F0F0")
st.plotly_chart(province_fig, use_container_width=True)

type_chart = (
    filtered_df.groupby("claim_types")
    .size()
    .reset_index(name="claims")
)

st.subheader("Claims by Type")

type_fig = px.bar(
    type_chart,
    x="claim_types",
    y="claims",
    color="claim_types",
    color_discrete_sequence=PALETTE
)
type_fig.update_layout(showlegend=False, plot_bgcolor=BG, paper_bgcolor=BG, font_color="#F0F0F0")
st.plotly_chart(type_fig, use_container_width=True)

status_chart = (
    filtered_df.groupby("claim_status")
    .size()
    .reset_index(name="claims")
)

st.subheader("Claims by Status")

status_fig = px.bar(
    status_chart,
    x="claim_status",
    y="claims",
    color="claim_status",
    color_discrete_sequence=PALETTE
)
status_fig.update_layout(showlegend=False, plot_bgcolor=BG, paper_bgcolor=BG, font_color="#F0F0F0")
st.plotly_chart(status_fig, use_container_width=True)

filtered_df["claim_date"] = pd.to_datetime(filtered_df["claim_date"])

monthly_chart = (
    filtered_df.groupby(
        filtered_df["claim_date"]
        .dt.to_period("M"))
        .size()
        .reset_index(name="claims"))

monthly_chart["claim_date"] = monthly_chart["claim_date"].astype(str)

st.subheader("Monthly Claims Trend")

monthly_fig = px.line(
    monthly_chart,
    x="claim_date",
    y="claims",
    markers=True,
    color_discrete_sequence=[ACCENT]
)
monthly_fig.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, font_color="#F0F0F0")
st.plotly_chart(monthly_fig, use_container_width=True)

st.subheader("Claim Status Distribution")
status_pie = (
    filtered_df.groupby("claim_status")
    .size()
    .reset_index(name="claims"))

fig = px.pie(
    status_pie,
    names="claim_status",
    values="claims",
    title="Claim Status Distribution",
    color_discrete_sequence=PALETTE,
    hole=0.4)

fig.update_traces(textposition="inside", textinfo="percent+label")
fig.update_layout(paper_bgcolor=BG, font_color="#F0F0F0")

st.plotly_chart(fig,
                use_container_width=True)

amount_chart = (
    filtered_df.groupby("province")
    ["claim_amount"]
    .sum()
    .reset_index())

st.subheader("Total Claim Amount by Province")

amount_fig = px.bar(
    amount_chart,
    x="province",
    y="claim_amount",
    color="province",
    color_discrete_sequence=PALETTE
)
amount_fig.update_layout(showlegend=False, plot_bgcolor=BG, paper_bgcolor=BG, font_color="#F0F0F0")
st.plotly_chart(amount_fig, use_container_width=True)

st.subheader("Summary Statistics")

st.subheader("Top 10 Highest Claims")

top_claims = (
    filtered_df
    .sort_values("claim_amount",
    ascending=False)
    .head(10))

st.dataframe(top_claims[
    ["claim_id",
     "claim_date",
     "province",
     "claim_types",
     "claim_amount",
     "claim_status"]])

st.dataframe(
    filtered_df[["claim_amount"]].describe())

st.download_button(
    label="Download Claims Data",
    data=csv,
    file_name="insurance_claims.csv",
    mime="text/csv"
)