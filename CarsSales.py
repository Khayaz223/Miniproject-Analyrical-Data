import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv(r"CarSales.csv")
    df = df.drop_duplicates()
    df = df.drop(columns=['Vehicle Type'])
    df['Model'] = df['Model'].str.replace('05-Sep', '9-5').str.replace('03-Sep', '9-3')
    df = df.dropna(subset=['Year Resale Value', 'Price in Thousands', 'Curb Weight', 'Power Factor', 'Fuel Efficiency'])

    # Convert sales to actual units (multiply by 1000)
    df['Sales (Units)'] = (df['Sales in Thousands'] * 1000).astype(int)
    
    # Convert price and resale value to actual dollars (multiply by 1000)
    df['Price'] = df['Price in Thousands'] * 1000
    df['Year Resale Value'] = df['Year Resale Value'] * 1000

    # Derived metrics
    df['Wheelbase-to-Length Ratio'] = df['Wheelbase'] / df['Length']
    df['Area Proxy'] = df['Width'] * df['Length']

    # Convert data types
    df['Horsepower'] = df['Horsepower'].astype(int)
    df['Fuel Efficiency'] = df['Fuel Efficiency'].astype(int)
    df['Curb Weight'] = df['Curb Weight'].round(1)
    df['Power Factor'] = df['Power Factor'].round(1)
    df = df.reset_index(drop=True)

    if 'Latest Launch' in df.columns:
        df['Latest Launch'] = pd.to_datetime(df['Latest Launch'])

    return df

df = load_data()

# Set page config
st.set_page_config(page_title="Car Sales Analytics", layout="wide", page_icon="🚗")
st.snow() # Show snow on dashboard load
st.markdown("""
<style>
 /* Adjust sidebar styling */
[data-testid="stSidebar"] {
    padding: 1rem;
}

/* Make sidebar scrollable */
.css-1d391kg {overflow-y: auto;
}
            
/* Sprinkle fade-in animation */
@keyframes sprinkle {
  0% { opacity: 0; transform: translateY(-10px); }
  100% { opacity: 1; transform: translateY(0); }
}
h1, h2, .stMetric, .stPlotlyChart {
  animation: sprinkle 1s ease-out;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao, .st-ap, .st-aq, .st-ar, .st-as {
        background-color: #8B4000;
        color: #ffffff;
        border: 1px solid #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .stMetric {
        background-color: #8B4000;
        color: #ffffff;
        border: 1px solid #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        border-radius: 10px;
        padding: 10px;
    }
    .css-1aumxhk {
        background-color: #8B4000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("### 🔍 Filter Cars")
    
    with st.expander("🔧 Select Manufacturer(s)", expanded=False):
        selected_manufacturers = st.multiselect(
            "Choose from available options",
            options=df['Manufacturer'].unique(),
            default=df['Manufacturer'].unique()
        )

    # Add date range selector to sidebar if 'Latest Launch' exists in dataframe
    if 'Latest Launch' in df.columns:
        st.markdown("---")
        st.markdown("### 📅 Date Range Selector")
        min_date = df['Latest Launch'].min()
        max_date = df['Latest Launch'].max()
        
        start_date = st.date_input("Start date", min_date)
        end_date = st.date_input("End date", max_date)

    st.image("KYZ.png", use_container_width=True)  # Insert your image

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-size: 13px; color: gray;'>"
        "© 2025, <b>Khayaz</b>"
        "</div>",
        unsafe_allow_html=True
    )

# --- Filtered Data ---
filtered_df = df[df['Manufacturer'].isin(selected_manufacturers)]

# Apply date filter if 'Latest Launch' exists
if 'Latest Launch' in filtered_df.columns:
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = filtered_df[(filtered_df['Latest Launch'] >= start_date) & 
                             (filtered_df['Latest Launch'] <= end_date)]

# --- KPI Section ---
from datetime import datetime

# --- Title and Image ---
col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.image('cars.jpg', width=170)

with col_title:
    st.markdown(
        "<center><h1 style='text-align: left; margin-bottom: 0;'>Car Sales Analytics Dashboard 🚗</h1></center>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size:16px; color:gray; margin-top:0;'>"
        f"Last update: <b>{datetime.now().strftime('%Y-%m-%d')}</b> &nbsp;|&nbsp; Created by <b>Khairul Azhad bin Khairul Nizam 2410735</b>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("## Year-to-Date (YTD) Performance Overview")

ytd_total_sales = filtered_df['Sales (Units)'].sum()
ytd_avg_price = filtered_df['Price'].mean()
ytd_avg_resale = filtered_df['Year Resale Value'].mean()
resale_ratio = (ytd_avg_resale / ytd_avg_price * 100).round(1)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("YTD Total Sales", f"{ytd_total_sales:,.0f} Units", "12.5% YoY")
with col2:
    st.metric("Average Price", f"${ytd_avg_price:,.0f}", "5.3% YoY")
with col3:
    st.metric("Avg Resale Ratio", f"{resale_ratio}%", "Resale/Price Ratio")

# --- 1. YTD Cars Sold by Manufacturer ---
st.header("1. YTD Cars Sold by Manufacturer")
sales_by_manu = filtered_df.groupby('Manufacturer')['Sales (Units)'].sum().sort_values(ascending=False).reset_index()
fig1 = px.bar(sales_by_manu, x='Manufacturer', y='Sales (Units)', 
              title='Sales by Manufacturer', 
              labels={'Sales (Units)': 'Sales (Units)'},
              text=[f"{x:,.0f}" for x in sales_by_manu['Sales (Units)']])
fig1.update_traces(textposition='outside')
st.plotly_chart(fig1, use_container_width=True)

# --- Downloadable Data ---
st.download_button(
    label="📥 Download Sales by Manufacturer CSV",
    data=sales_by_manu.to_csv(index=False).encode('utf-8'),
    file_name='sales_by_manufacturer.csv',
    mime='text/csv'
)

# --- 2. Side-by-Side: Curb Weight & Vehicle Specs ---
st.header("2. YTD Total Sales by Curb Weight & Vehicle Specifications")
col1, col2 = st.columns(2)

with col1:
    curb_bins = pd.cut(filtered_df['Curb Weight'], bins=5)
    df_curb = filtered_df.copy()
    df_curb['Curb Weight Bin'] = curb_bins.astype(str)
    curb_group = df_curb.groupby('Curb Weight Bin')['Sales (Units)'].sum().reset_index()
    fig2 = px.pie(curb_group, values='Sales (Units)', names='Curb Weight Bin',
                  title='Sales by Curb Weight',
                  hover_data={'Sales (Units)': ':,.0f'})
    st.plotly_chart(fig2, use_container_width=True)

# --- Downloadable Data ---
    st.download_button(
    label="📥 Download Curb Weight Sales CSV",
    data=curb_group.to_csv(index=False).encode('utf-8'),
    file_name='sales_by_curb_weight.csv',
    mime='text/csv'
)
    
with col2:
    spec_cols = ['Horsepower', 'Engine Size', 'Fuel Capacity', 'Fuel Efficiency', 'Power Factor']
    selected_spec = st.selectbox("Choose Vehicle Specification", spec_cols)
    spec_bins = pd.cut(filtered_df[selected_spec], bins=5)
    df_spec = filtered_df.copy()
    df_spec['Spec Bin'] = spec_bins.astype(str)
    spec_group = df_spec.groupby('Spec Bin')['Sales (Units)'].sum().reset_index()
    fig3 = px.pie(spec_group, values='Sales (Units)', names='Spec Bin',
                  title=f'Sales by {selected_spec}', hole=0.4,
                  hover_data={'Sales (Units)': ':,.0f'})
    st.plotly_chart(fig3, use_container_width=True)

# --- Downloadable Data ---
    st.download_button(
    label=f"📥 Download Sales by {selected_spec} CSV",
    data=spec_group.to_csv(index=False).encode('utf-8'),
    file_name=f'sales_by_{selected_spec.lower().replace(" ", "_")}.csv',
    mime='text/csv'
)

# --- 3. YTD Sales Weekly Trend ---
st.header("3. YTD Sales Weekly Trend")
if 'Latest Launch' in df.columns:
    if not filtered_df.empty:
        weekly_df = filtered_df.copy()
        weekly_df['Launch Week'] = weekly_df['Latest Launch'].dt.to_period('W').astype(str)
        weekly_sales = weekly_df.groupby('Launch Week')['Sales (Units)'].sum().reset_index()
        
        fig4 = px.line(weekly_sales, x='Launch Week', y='Sales (Units)', 
                      title=f'Weekly Sales Trend ({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})', 
                      markers=True,
                      labels={'Sales (Units)': 'Sales (Units)'})
        fig4.update_traces(text=[f"{x:,.0f}" for x in weekly_sales['Sales (Units)']])
        st.plotly_chart(fig4, use_container_width=True)

        # Downloadable Data
        st.download_button(
            label="📥 Download Weekly Sales Trend CSV",
            data=weekly_sales.to_csv(index=False).encode('utf-8'),
            file_name='weekly_sales_trend.csv',
            mime='text/csv'
        )
    else:
        st.warning("No data available for the selected date range.")
else:
    st.warning("Weekly trend requires 'Latest Launch' date data.")

# --- 4. YTD Sales by Vehicle Dimensions ---
st.header("4. YTD Total Sales by Vehicle Dimensions")
dimension_metric = st.radio("Choose Metric", ['Wheelbase-to-Length Ratio', 'Area Proxy'])

if dimension_metric:
    dim_bins = pd.cut(filtered_df[dimension_metric], bins=5)
    df_dim = filtered_df.copy()
    df_dim['Dimension Bin'] = dim_bins.astype(str)
    dim_group = df_dim.groupby('Dimension Bin').agg({
        dimension_metric: 'mean',
        'Sales (Units)': 'sum'
    }).reset_index()

    fig5 = px.bar(
        dim_group,
        x=dimension_metric,
        y='Sales (Units)',
        title=f'Sales by {dimension_metric}',
        text=[f"{x:,.0f}" for x in dim_group['Sales (Units)']],
        labels={'Sales (Units)': 'Sales (Units)', dimension_metric: dimension_metric}
    )
    fig5.update_traces(textposition='outside')
    st.plotly_chart(fig5, use_container_width=True)

    # --- Downloadable Data ---
    st.download_button(
        label=f"📥 Download Sales by {dimension_metric} CSV",
        data=dim_group.to_csv(index=False).encode('utf-8'),
        file_name=f'sales_by_{dimension_metric.lower().replace(" ", "_").replace("-", "_")}.csv',
        mime='text/csv'
    )

# --- 5. Company-Wise Sales Trend (Treemap with Visible Values) ---
st.header("5. Company-Wise Sales Trend")

# Use unscaled values for visualization (as per your request)
filtered_df['Sales Display'] = filtered_df['Sales (Units)']
filtered_df['Price Display'] = filtered_df['Price']
filtered_df['Resale Display'] = filtered_df['Year Resale Value']

treemap_df = filtered_df.groupby(['Manufacturer', 'Model']).agg({
    'Sales Display': 'sum',
    'Price Display': 'mean',
    'Resale Display': 'mean'
}).reset_index()

fig6 = px.treemap(
    treemap_df,
    path=['Manufacturer', 'Model'],
    values='Sales Display',
    color='Price Display',
    color_continuous_scale=px.colors.sequential.Rainbow,
    hover_data={
        'Sales Display': ':.0f',
        'Price Display': ':.0f',
        'Resale Display': ':.0f'
    },
    title="Sales Treemap by Manufacturer and Model (Sized by Sales in Thousands, Colored by Price in Thousands)"
)

fig6.update_traces(
    hovertemplate='<b>%{label}</b><br>Sales: %{customdata[0]:,.0f}<br>Price: $%{customdata[1]:,.0f}<br>Resale: $%{customdata[2]:,.0f}<extra></extra>',
    texttemplate='%{label}<br>%{value:,.0f} Units',
    textfont=dict(size=14),
    textposition="middle center"
)

st.plotly_chart(fig6, use_container_width=True)

# Downloadable Data
st.download_button(
    label="📥 Download Treemap Sales Data CSV",
    data=treemap_df.to_csv(index=False).encode('utf-8'),
    file_name='sales_treemap_data.csv',
    mime='text/csv'
)

# --- 6. Prepared Dataset Table ---
st.header("6. Prepared Dataset")
if st.checkbox("Show Prepared Data Table"):
    st.dataframe(
        filtered_df.style.format({
            'Sales in Thousands': '{:,.3f}',
            'Sales Display': '{:,.0f}',
            'Engine Size': '{:,.1f}',
            'Fuel Capacity': '{:,.1f}',
            'Fuel Efficiency': '{:,.0f}',
            'Wheelbase': '{:,.1f}',
            'Length': '{:,.1f}',
            'Width': '{:,.1f}',
            'Latest Launch': lambda x: x.strftime('%Y-%m-%d') if isinstance(x, pd.Timestamp) else x,
            'Price in Thousands': '${:,.1f}',
            'Horsepower': '{:,.0f}',
            'Sales (Units)': '{:,.0f}',
            'Price': '${:,.0f}',
            'Year Resale Value': '${:,.0f}',
            'Price Display': '${:,.0f}',
            'Resale Display': '${:,.0f}',
            'Curb Weight': '{:.1f}',
            'Power Factor': '{:.1f}',
            'Wheelbase-to-Length Ratio': '{:.3f}',
            'Area Proxy': '{:.1f}'
        }),
        use_container_width=True
    )

# Downloadable Prepared Data
st.download_button(
    label="📥 Download Prepared Data CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='prepared_car_sales_data.csv',
    mime='text/csv'
)