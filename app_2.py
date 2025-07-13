import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt
import pydeck as pdk
from fare_model import calculate_fare

# --- Responsive CSS for mobile layout ---
st.markdown(
    '''
    <style>
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# --- Language Selector ---
lang = st.sidebar.selectbox("🌐 Choose Language", ["English", "Krio"])

# --- Localization dictionary ---
L = {
    "English": {
        "title": "🚖 Dynamic Public Transport Fare Estimator – Freetown",
        "vehicle_type": "Select vehicle type",
        "distance": "Enter distance (km)",
        "fuel_price": "Enter current fuel price (SLL)",
        "traffic": "Traffic level",
        "weather": "Weather condition",
        "period": "Traffic period",
        "day": "Day type",
        "calculate": "Calculate Fare",
        "fare_breakdown": "🔍 View Fare Breakdown",
        "fare_components": "### Fare Components",
        "fare_estimate": "Estimated Fare",
        "fare_trend": "📈 Fare Trend Simulation Over Time",
        "simulate_trend": "Simulate Fare Trend Over Time",
        "trend_days": "Number of days to simulate",
        "start_date": "Start date",
        "generate_trend": "Generate Fare Trend",
        "comparison": "🛣️ Multiple Route / Vehicle Type Fare Comparison",
        "compare_label": "Compare Multiple Routes or Vehicles",
        "scenario": "Scenario",
        "vehicle": "Vehicle",
        "distance_km": "Distance (km)",
        "estimated": "Estimated Fare (SLL)",
        "visual_compare": "### 🔍 Visual Comparison",
        "map_section": "🗺️ Map Visualization",
        "show_map": "Show Map"
    },
    "Krio": {
        "title": "🚖 Transpɔt Fɛr Estimeita – Fritɔn",
        "vehicle_type": "Chuz di kaind transpɔt",
        "distance": "Wos dɔns (km)",
        "fuel_price": "Put di fɔyəl pris (SLL)",
        "traffic": "Trafik lɛvul",
        "weather": "Wɛda kondishɔn",
        "period": "Trafik taim",
        "day": "Dei kaind",
        "calculate": "Mak Fɛr",
        "fare_breakdown": "🔍 Luk Fɛr Brɛkdaun",
        "fare_components": "### Fɛr Pɔt dem",
        "fare_estimate": "Di Fɛr Na",
        "fare_trend": "📈 Fɛr Chɛnj Ova Taim",
        "simulate_trend": "Simuleyt Fɛr Ova Taim",
        "trend_days": "Numba ɔf dey fɔ simuleyt",
        "start_date": "Stat dey",
        "generate_trend": "Mak Fɛr Chaat",
        "comparison": "🛣️ Chɛk Plenti Ruut ɔr Transpɔt",
        "compare_label": "Chɛk Plenti Ruut ɔ Transpɔt Kaind",
        "scenario": "Scenario",
        "vehicle": "Transpɔt",
        "distance_km": "Dɔns (km)",
        "estimated": "Fɛr (SLL)",
        "visual_compare": "### 🔍 Fɛr Chaat",
        "map_section": "🗺️ Mɔp",
        "show_map": "Shɔ Mɔp"
    }
}[lang]

st.title(L["title"])

# --- Input Form ---
vehicle_type = st.selectbox(L["vehicle_type"], ["minibus", "keke", "taxi", "motorbike", "paratransit bus", "formal bus"])
distance_km = st.number_input(L["distance"], min_value=0.0, step=0.1)
fuel_price = st.number_input(L["fuel_price"], min_value=0, value=30000)
traffic_level = st.selectbox(L["traffic"], ["low", "moderate", "heavy"])
weather_condition = st.selectbox(L["weather"], ["clear", "cloudy", "rainy", "stormy"])
traffic_period = st.selectbox(L["period"], ["morning peak", "afternoon peak", "evening peak", "off-peak"])
day_type = st.radio(L["day"], ["weekday", "weekend"])

if st.button(L["calculate"]):
    fare, breakdown = calculate_fare(vehicle_type, distance_km, fuel_price, traffic_level,
                                     weather_condition, traffic_period, day_type)
    st.success(f"{L['fare_estimate']}: **{int(fare):,} SLL**")

    with st.expander(L["fare_breakdown"]):
        st.write(L["fare_components"])

        breakdown_chart_data = {
            k: v for k, v in breakdown.items()
            if k not in ["Weekend Multiplier", "Total Fare"]
        }

        df_breakdown = pd.DataFrame(list(breakdown_chart_data.items()), columns=["Component", "Amount (SLL)"])
        st.dataframe(df_breakdown, use_container_width=True)
        st.bar_chart(df_breakdown.set_index("Component"))

# --- Map Section ---
with st.expander(L["map_section"]):
    lat, lon = 8.4844, -13.2344
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

# --- Trend Simulation ---
st.subheader(L["fare_trend"])

with st.expander(L["simulate_trend"]):
    trend_days = st.slider(L["trend_days"], min_value=1, max_value=30, value=7)
    base_date = st.date_input(L["start_date"], datetime.date.today())

    if st.button(L["generate_trend"]):
        dates = [base_date + datetime.timedelta(days=i) for i in range(trend_days)]
        fuel_prices = np.linspace(fuel_price, fuel_price + 5000, trend_days)
        day_types = ["weekday" if d.weekday() < 5 else "weekend" for d in dates]

        trend_data = []
        for i in range(trend_days):
            fare, _ = calculate_fare(vehicle_type, distance_km, fuel_prices[i], traffic_level,
                                     weather_condition, traffic_period, day_types[i])
            trend_data.append({"Date": dates[i], L["estimated"]: fare})

        df_trend = pd.DataFrame(trend_data)
        st.line_chart(df_trend.set_index("Date"))

# --- Comparison ---
st.subheader(L["comparison"])

with st.expander(L["compare_label"]):
    num_routes = st.slider("Number of comparisons", 1, 5, 2)
    comparison_data = []

    for i in range(num_routes):
        st.markdown(f"#### {L['scenario']} {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            v = st.selectbox(f"{L['vehicle']} {i+1}", ["minibus", "keke", "taxi", "motorbike", "paratransit bus", "formal bus"], key=f"v_{i}")
        with col2:
            d = st.number_input(f"{L['distance_km']} {i+1}", min_value=0.0, step=0.1, key=f"d_{i}")
        with col3:
            f = st.number_input(f"{L['fuel_price']} {i+1}", min_value=0, value=fuel_price, key=f"f_{i}")

        fare, _ = calculate_fare(v, d, f, traffic_level, weather_condition, traffic_period, day_type)
        comparison_data.append({L["scenario"]: f"#{i+1}", L["vehicle"]: v, L["distance_km"]: d, "Fuel Price": f, L["estimated"]: fare})

    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison)
        st.write(L["visual_compare"])
        bar_chart = alt.Chart(df_comparison).mark_bar().encode(
            x=L["scenario"], y=L["estimated"], color=L["vehicle"],
            tooltip=[L["vehicle"], L["distance_km"], "Fuel Price", L["estimated"]]
        ).properties(height=400)
        st.altair_chart(bar_chart, use_container_width=True)