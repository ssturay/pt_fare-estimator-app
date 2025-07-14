import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from fare_model import calculate_fare

# --- Mobile-Friendly Layout ---
st.markdown("""
    <style>
    @media (max-width: 600px) {
        .stApp .block-container {
            padding: 0.5rem !important;
        }
        label, .stSelectbox label {
            font-size: 0.9rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- Language Support ---
lang = st.sidebar.selectbox("🌐 Choose Language", ["English", "Krio"])

L = {
    "English": {
        "title": "🚖 Freetown Public Transport Fare Estimator - FEsApp",
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
        "map_header": "🗺️ Click on the Map to Measure Route Distance",
        "your_location": "📍 Your current location"
    },
    "Krio": {
        "title": "🚖 Fritɔn Transpɔt Fɛr Estimator - FEsApp",
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
        "map_header": "🗺️ Klik Map fɔ Mɛshɔ Dɔns",
        "your_location": "📍 Yuh Lokeshɔn"
    }
}[lang]

st.title(L["title"])

# --- Detect User Location ---

location = streamlit_geolocation()

if location and location["latitude"] is not None and location["longitude"] is not None:
    user_lat = location["latitude"]
    user_lon = location["longitude"]
    st.success(f"📍 Your current location: ({user_lat:.4f}, {user_lon:.4f})")
else:
    st.warning("📍 Waiting for location permission or unable to fetch coordinates.")
    user_lat, user_lon = 8.48, -13.23  # Default to Freetown




# --- Map Interaction for Distance Measurement ---
with st.expander(L["map_header"]):
    if "clicks" not in st.session_state:
        st.session_state["clicks"] = []

    m = folium.Map(location=[user_lat, user_lon], zoom_start=12)

    for pt in st.session_state["clicks"]:
        folium.Marker([pt["lat"], pt["lng"]]).add_to(m)

    map_data = st_folium(m, height=400, key="map")

    if map_data and map_data.get("last_clicked"):
        if len(st.session_state["clicks"]) < 2:
            st.session_state["clicks"].append(map_data["last_clicked"])

    if len(st.session_state["clicks"]) == 2:
        pt1, pt2 = st.session_state["clicks"]
        distance_km = geodesic((pt1["lat"], pt1["lng"]), (pt2["lat"], pt2["lng"])).km
        st.success(f"📏 Measured Distance: {distance_km:.2f} km")
    else:
        distance_km = st.number_input(L["distance"], min_value=0.0, step=0.1)

# --- Form Inputs ---
vehicle_type = st.selectbox(L["vehicle_type"], ["minibus", "keke", "taxi", "motorbike", "paratransit bus", "formal bus"])
fuel_price = st.number_input(L["fuel_price"], min_value=0, value=30000)
traffic_level = st.selectbox(L["traffic"], ["low", "moderate", "heavy"])
weather_condition = st.selectbox(L["weather"], ["clear", "cloudy", "rainy", "stormy"])
traffic_period = st.selectbox(L["period"], ["morning peak", "afternoon peak", "evening peak", "off-peak"])
day_type = st.radio(L["day"], ["weekday", "weekend"])

# --- Fare Calculation ---
if st.button(L["calculate"]):
    fare, breakdown = calculate_fare(vehicle_type, distance_km, fuel_price, traffic_level,
                                     weather_condition, traffic_period, day_type)
    st.success(f"{L['fare_estimate']}: **{int(fare):,} SLL**")
    with st.expander(L["fare_breakdown"]):
        df = pd.DataFrame.from_dict({k: [v] for k, v in breakdown.items() if k != "Weekend Multiplier"})
        st.dataframe(df.T.rename(columns={0: "SLL"}), use_container_width=True)

# --- Fare Trend Simulation ---
st.subheader(L["fare_trend"])
with st.expander(L["simulate_trend"]):
    trend_days = st.slider(L["trend_days"], 1, 30, 7)
    start_date = st.date_input(L["start_date"], datetime.date.today())
    if st.button(L["generate_trend"]):
        trend = []
        for i in range(trend_days):
            date = start_date + datetime.timedelta(days=i)
            fuel_sim = fuel_price + i * 200
            daytype = "weekday" if date.weekday() < 5 else "weekend"
            fare, _ = calculate_fare(vehicle_type, distance_km, fuel_sim, traffic_level,
                                     weather_condition, traffic_period, daytype)
            trend.append({"Date": date, L["estimated"]: fare})
        df_trend = pd.DataFrame(trend).set_index("Date")
        st.line_chart(df_trend)

# --- Route Comparison ---
st.subheader(L["comparison"])
with st.expander(L["compare_label"]):
    rows = st.slider("Routes", 1, 5, 2)
    comp = []
    for i in range(rows):
        col1, col2, col3 = st.columns(3)
        with col1:
            v = st.selectbox(f"{L['vehicle']} {i+1}", ["minibus", "keke", "taxi", "motorbike", "paratransit bus", "formal bus"], key=f"v_{i}")
        with col2:
            d = st.number_input(f"{L['distance_km']} {i+1}", 0.0, 100.0, key=f"d_{i}")
        with col3:
            f = st.number_input(f"{L['fuel_price']} {i+1}", 0, value=30000, key=f"f_{i}")
        fare, _ = calculate_fare(v, d, f, traffic_level, weather_condition, traffic_period, day_type)
        comp.append({L["scenario"]: f"#{i+1}", L["vehicle"]: v, L["distance_km"]: d, "Fuel Price": f, L["estimated"]: fare})
    df = pd.DataFrame(comp)
    st.dataframe(df, use_container_width=True)
    st.altair_chart(alt.Chart(df).mark_bar().encode(
        x=L["scenario"], y=L["estimated"], color=L["vehicle"],
        tooltip=[L["vehicle"], L["distance_km"], "Fuel Price", L["estimated"]]
    ).properties(height=400), use_container_width=True)
