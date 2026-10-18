import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Agriculture Equipment Analytics",
    page_icon="🌾",
    layout="wide"
)

# Green agriculture website design
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f1f8e9, #ffffff);
}
h1, h2, h3 {
    color: #1b5e20;
}
[data-testid="stMetric"] {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #c5e1a5;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("🌾 Agriculture Equipment Analytics")
st.subheader("Equipment Usage and Seasonal Demand Analysis")
st.markdown(
    "Explore agricultural equipment usage, seasonal trends, "
    "monthly demand and state-wise analysis."
)

# Sample data
np.random.seed(42)

states = [
    "Tamil Nadu", "Punjab", "Haryana", "Karnataka",
    "Maharashtra", "Uttar Pradesh", "Andhra Pradesh",
    "Telangana", "Gujarat", "Kerala"
]

equipment = [
    "Tractor", "Power Tiller", "Seed Drill",
    "Combine Harvester", "Pump Set", "Sprayer",
    "Thresher", "Rotavator", "Cultivator", "Plough"
]

month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

season_map = {
    1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Kharif", 7: "Kharif", 8: "Kharif",
    9: "Kharif", 10: "Rabi", 11: "Rabi", 12: "Rabi"
}

season_factor = {
    "Winter": 0.85,
    "Summer": 0.95,
    "Kharif": 1.40,
    "Rabi": 1.15
}

equipment_factor = {
    "Tractor": 1.40,
    "Power Tiller": 0.85,
    "Seed Drill": 1.00,
    "Combine Harvester": 1.10,
    "Pump Set": 1.20,
    "Sprayer": 1.15,
    "Thresher": 0.90,
    "Rotavator": 1.05,
    "Cultivator": 0.95,
    "Plough": 0.90
}

records = []

for state in states:
    for month in range(1, 13):
        season = season_map[month]

        for item in equipment:
            base = (
                100
                * season_factor[season]
                * equipment_factor[item]
            )

            usage = int(
                base
                * np.random.uniform(0.70, 1.30)
                * np.random.uniform(0.85, 1.15)
            )

            records.append({
                "State": state,
                "Month": month,
                "Month_Name": month_names[month - 1],
                "Season": season,
                "Equipment": item,
                "Usage_Count": max(1, usage)
            })

df = pd.DataFrame(records)

# Sidebar filters
st.sidebar.header("🌿 Dashboard Filters")

selected_states = st.sidebar.multiselect(
    "Select States",
    states,
    default=states
)

selected_seasons = st.sidebar.multiselect(
    "Select Seasons",
    ["Winter", "Summer", "Kharif", "Rabi"],
    default=["Winter", "Summer", "Kharif", "Rabi"]
)

selected_equipment = st.sidebar.multiselect(
    "Select Equipment",
    equipment,
    default=equipment
)

filtered = df[
    df["State"].isin(selected_states)
    & df["Season"].isin(selected_seasons)
    & df["Equipment"].isin(selected_equipment)
]

if filtered.empty:
    st.warning("Please select at least one state, season and equipment.")
    st.stop()

# Summary metrics
st.markdown("## 📊 Project Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Records", f"{len(filtered):,}")
c2.metric("Equipment Types", filtered["Equipment"].nunique())
c3.metric("States Selected", filtered["State"].nunique())
c4.metric("Total Usage", f"{filtered['Usage_Count'].sum():,}")

st.success("🌱 Explore the agricultural equipment analysis below!")

# Prepare chart data
equipment_usage = (
    filtered.groupby("Equipment", as_index=False)["Usage_Count"]
    .sum()
    .sort_values("Usage_Count", ascending=False)
)

season_order = ["Winter", "Summer", "Kharif", "Rabi"]

seasonal = (
    filtered.groupby("Season", as_index=False)["Usage_Count"]
    .sum()
)
seasonal["Season"] = pd.Categorical(
    seasonal["Season"],
    categories=season_order,
    ordered=True
)
seasonal = seasonal.sort_values("Season")

monthly = (
    filtered.groupby(["Month", "Month_Name"], as_index=False)["Usage_Count"]
    .sum()
    .sort_values("Month")
)

state_usage = (
    filtered.groupby("State", as_index=False)["Usage_Count"]
    .sum()
    .sort_values("Usage_Count", ascending=False)
)

# Graph 1
st.markdown("## 🚜 1. Equipment-wise Usage")
fig1 = px.bar(
    equipment_usage,
    x="Equipment",
    y="Usage_Count",
    color="Usage_Count",
    title="Agricultural Equipment Usage",
    color_continuous_scale="Greens"
)
st.plotly_chart(fig1, use_container_width=True)

# Graph 2
st.markdown("## 🌦️ 2. Seasonal Demand")
fig2 = px.bar(
    seasonal,
    x="Season",
    y="Usage_Count",
    color="Season",
    title="Demand Across Seasons",
    color_discrete_sequence=["#81c784", "#aed581", "#388e3c", "#689f38"]
)
st.plotly_chart(fig2, use_container_width=True)

# Graph 3
st.markdown("## 📅 3. Monthly Demand")
fig3 = px.line(
    monthly,
    x="Month_Name",
    y="Usage_Count",
    markers=True,
    title="Monthly Equipment Demand"
)
fig3.update_traces(line_color="#2e7d32")
st.plotly_chart(fig3, use_container_width=True)

# Graph 4
st.markdown("## 🗺️ 4. State-wise Usage")
fig4 = px.bar(
    state_usage,
    x="State",
    y="Usage_Count",
    color="Usage_Count",
    title="Equipment Usage by State",
    color_continuous_scale="YlGn"
)
st.plotly_chart(fig4, use_container_width=True)

# Graph 5
st.markdown("## 🔥 5. Equipment vs Season")
pivot = filtered.pivot_table(
    index="Equipment",
    columns="Season",
    values="Usage_Count",
    aggfunc="sum",
    fill_value=0,
    observed=False
)
pivot = pivot.reindex(columns=season_order, fill_value=0)

fig5 = px.imshow(
    pivot,
    labels={
        "x": "Season",
        "y": "Equipment",
        "color": "Usage Count"
    },
    title="Equipment Usage Heatmap",
    color_continuous_scale="Greens",
    aspect="auto"
)
st.plotly_chart(fig5, use_container_width=True)

# Graph 6
st.markdown("## 🥧 6. Equipment Usage Percentage")
fig6 = px.pie(
    equipment_usage,
    names="Equipment",
    values="Usage_Count",
    title="Equipment Usage Distribution",
    color_discrete_sequence=px.colors.sequential.Greens
)
st.plotly_chart(fig6, use_container_width=True)

# Graph 7
st.markdown("## 📈 7. Seasonal Equipment Comparison")
comparison = filtered.pivot_table(
    index="Season",
    columns="Equipment",
    values="Usage_Count",
    aggfunc="sum",
    fill_value=0,
    observed=False
).reindex(season_order).fillna(0)

fig7 = px.bar(
    comparison,
    barmode="group",
    title="Equipment Demand Comparison by Season",
    labels={"value": "Usage Count", "Season": "Season"}
)
st.plotly_chart(fig7, use_container_width=True)

# Graph 8
st.markdown("## 🌱 8. Monthly Demand by Season")
monthly_season = (
    filtered.groupby(
        ["Month", "Month_Name", "Season"],
        as_index=False
    )["Usage_Count"]
    .sum()
    .sort_values("Month")
)

fig8 = px.line(
    monthly_season,
    x="Month_Name",
    y="Usage_Count",
    color="Season",
    markers=True,
    title="Monthly Demand Trends by Season",
    category_orders={"Season": season_order}
)
st.plotly_chart(fig8, use_container_width=True)

# Analysis
st.markdown("## 🏆 Key Analysis Results")

top_equipment = equipment_usage.iloc[0]["Equipment"]
top_season = seasonal.sort_values(
    "Usage_Count", ascending=False
).iloc[0]["Season"]
top_month = monthly.loc[
    monthly["Usage_Count"].idxmax(), "Month_Name"
]

a, b, c = st.columns(3)
a.metric("Top Equipment", top_equipment)
b.metric("Highest Demand Season", str(top_season))
c.metric("Highest Demand Month", top_month)

# Dataset preview
with st.expander("🔎 View Dataset"):
    st.dataframe(filtered, use_container_width=True)

# Downloads
st.markdown("## 📥 Download Project Data")

st.download_button(
    "Download Full Dataset (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="agriculture_equipment_dataset.csv",
    mime="text/csv"
)

st.download_button(
    "Download Filtered Dataset (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_agriculture_data.csv",
    mime="text/csv"
)

st.caption(
    "Note: This dashboard uses demonstration data, not official government statistics."
)
