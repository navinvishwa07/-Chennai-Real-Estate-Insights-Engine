import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Chennai Real Estate Engine", layout="wide")

# 2. Load the Final Mapped Data
@st.cache_data
def load_data():
    # READ THE GEOCODED FILE
    df = pd.read_csv("chennai_housing_final.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ File not found. Make sure you ran 'geocoder.py' successfully!")
    st.stop()

# 3. Sidebar Filters
st.sidebar.header("🔍 Filter Options")

# -- Filter by Location --
all_locations = sorted(df['location'].unique())
selected_loc = st.sidebar.multiselect("Select Location", all_locations, default=all_locations[:3])

# -- Filter by Price Range --
min_price = int(df['price'].min())
max_price = int(df['price'].max())
price_range = st.sidebar.slider("Budget Range (₹)", min_price, max_price, (min_price, max_price))

# Apply Filters
filtered_df = df[
    (df['location'].isin(selected_loc)) & 
    (df['price'].between(price_range[0], price_range[1]))
]

# 4. Main Dashboard UI
st.title("🏙️ Chennai Real Estate Insights Engine")
st.markdown("### Real-time analysis of undervaluation listings")

# Top Level Metrics
if not filtered_df.empty:
    avg_ppsqft = filtered_df['price_per_sqft'].median()
    col1, col2, col3 = st.columns(3)
    col1.metric("Listings Found", f"{len(filtered_df)}")
    col2.metric("Median Price", f"₹ {filtered_df['price'].median() / 100000:.1f} L")
    col3.metric("Avg Price/Sqft", f"₹ {int(avg_ppsqft)}")
else:
    st.warning("No listings match your filters.")
    st.stop()

st.divider()

# --- THE MAP SECTION ---
st.subheader("🗺️ Neighborhood Price Heatmap")
st.caption("Brighter Colors = Higher Price Per Sqft")

fig_map = px.scatter_mapbox(
    filtered_df,
    lat="lat",
    lon="lon",
    color="price_per_sqft",
    size="sqft",
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=10,
    height=500,
    hover_name="title",
    hover_data={"lat": False, "lon": False, "location": True, "price": False, "price_per_sqft": True}
)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# --- THE CHARTS SECTION ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("💰 Price vs. Size Analysis")
    
    # Create Custom Tooltip Column (Cr/Lacs)
    # Use .copy() to prevent "SettingWithCopyWarning"
    chart_df = filtered_df.copy()
    chart_df['display_price'] = chart_df['price'].apply(
        lambda x: f"₹ {x/10000000:.2f} Cr" if x >= 10000000 else f"₹ {x/100000:.2f} L"
    )

    fig_scatter = px.scatter(
        chart_df,
        x="sqft",
        y="price",
        color="location",
        size="price_per_sqft",
        hover_data={'display_price': True, 'price': False, 'sqft': True, 'location': True},
        title="Bigger Bubble = More Expensive per Sqft"
    )

    # Custom Y-Axis Ticks (Indian Format)
    if not chart_df.empty:
        max_price_val = chart_df['price'].max()
        tick_vals = np.linspace(0, max_price_val, 6)
        tick_text = []
        for x in tick_vals:
            if x >= 10000000:
                tick_text.append(f"₹ {x/10000000:.1f} Cr")
            else:
                tick_text.append(f"₹ {x/100000:.0f} L")
        
        fig_scatter.update_yaxes(tickmode='array', tickvals=tick_vals, ticktext=tick_text)

    st.plotly_chart(fig_scatter, use_container_width=True)

with c2:
    st.subheader("📍 Price Distribution")
    fig_box = px.box(filtered_df, x="location", y="price_per_sqft", points="all")
    fig_box.update_yaxes(tickformat=",", tickprefix="₹ ")
    st.plotly_chart(fig_box, use_container_width=True)

# 6. The "Deal Rater" Algorithm 🤖
st.subheader("🔥 Top 5 Undervalued Picks")
st.caption("Listings priced significantly lower than the neighborhood average.")

if not filtered_df.empty:
    # Calculate neighborhood median
    filtered_df['market_median'] = filtered_df.groupby('location')['price_per_sqft'].transform('median')
    
    # Flag deals (10% cheaper)
    filtered_df['is_deal'] = filtered_df['price_per_sqft'] < (filtered_df['market_median'] * 0.9)
    
    deals = filtered_df[filtered_df['is_deal'] == True].sort_values(by='price_per_sqft')
    
    st.dataframe(
        deals[['location', 'title', 'sqft', 'price', 'price_per_sqft', 'market_median']],
        hide_index=True
    )