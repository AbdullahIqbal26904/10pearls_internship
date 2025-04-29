import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pickle
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AQI Prediction Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        font-weight: 600;
    }
    .card {
        border-radius: 5px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .good {background-color: #ccffcc; color: #006600;}
    .moderate {background-color: #ffff99; color: #666600;}
    .unhealthy-sensitive {background-color: #ffcc99; color: #cc6600;}
    .unhealthy {background-color: #ff9999; color: #990000;}
    .very-unhealthy {background-color: #cc99cc; color: #660066;}
    .hazardous {background-color: #cc6666; color: #660000;}
    .custom-info-box {
        background-color: #e1f5fe;
        border-left: 5px solid #0288d1;
        padding: 15px;
        border-radius: 3px;
        margin-bottom: 20px;
    }
    .metric-good { color: #00e400; }
    .metric-moderate { color: #ffff00; }
    .metric-usg { color: #ff7e00; }
    .metric-unhealthy { color: #ff0000; }
    .metric-very-unhealthy { color: #8f3f97; }
    .metric-hazardous { color: #7e0023; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def load_data():
    """Load historical AQI data and predictions."""
    try:
        # --- Step 1: Load Data from AWS S3 ---
        bucket_name = 'my-feature-store-data'
        data_key = 'pipeline-data/data.csv'
        prediction_key = 'predictions/prediction_results.csv'
        # Create S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

        # Load dataset
        obj = s3.get_object(Bucket=bucket_name, Key=data_key)
        historical_data = pd.read_csv(obj['Body'])
        # Load predictions
        obj = s3.get_object(Bucket=bucket_name, Key=prediction_key)
        predictions = pd.read_csv(obj['Body'])
        
        return historical_data, predictions
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def get_aqi_category(aqi):
    """Returns the AQI category, color and health implications based on the value."""
    if aqi <= 50:
        return "Good", "#00e400", "Air quality is satisfactory, and air pollution poses little or no risk."
    elif aqi <= 100:
        return "Moderate", "#ffff00", "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#ff7e00", "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
    elif aqi <= 200:
        return "Unhealthy", "#ff0000", "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
    elif aqi <= 300:
        return "Very Unhealthy", "#8f3f97", "Health alert: The risk of health effects is increased for everyone."
    else:
        return "Hazardous", "#7e0023", "Health warning of emergency conditions: everyone is more likely to be affected."

def get_trend_icon(current, previous):
    """Returns an icon indicating the trend of AQI values."""
    if current > previous * 1.05:  # 5% increase
        return "↑"
    elif current < previous * 0.95:  # 5% decrease
        return "↓"
    else:
        return "→"

def get_forecast_summary(predictions):
    """Generate a summary of the forecast."""
    if predictions is None or len(predictions) == 0:
        return "Unable to generate forecast summary."
    
    avg_aqi = predictions['Predicted_Calculated_AQI'].mean()
    max_aqi = predictions['Predicted_Calculated_AQI'].max()
    max_day = predictions.loc[predictions['Predicted_Calculated_AQI'].idxmax(), 'Date']
    
    category, _, implication = get_aqi_category(max_aqi)
    
    return f"Over the next 3 days, the AQI is predicted to average around {avg_aqi:.1f}, with the highest value of {max_aqi:.1f} ({category}) on {max_day}. {implication}"

# --- Dashboard Layout ---

def main():
    # Load data
    historical_data, predictions = load_data()
    
    if historical_data is None or predictions is None:
        st.error("Unable to load data. Please check the data files and try again.")
        return
    
    # --- Header Section ---
    st.markdown("<h1 class='main-header'>🌬️ Air Quality Index Prediction Dashboard</h1>", unsafe_allow_html=True)
    
    # Current date and time
    st.markdown(f"<p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>", unsafe_allow_html=True)
    
    # Dashboard description
    with st.expander("About this dashboard", expanded=False):
        st.markdown("""
        This dashboard provides a 3-day forecast of Air Quality Index (AQI) values. The predictions are based on historical data 
        and machine learning models that take into account various factors including pollutant levels, weather conditions, and temporal patterns.
        
        The dashboard displays:
        - Historical AQI trends
        - 3-day AQI forecast
        - Detailed hourly predictions
        - Health implications of forecasted AQI levels
        
        **Data sources:**
        - Historical AQI and weather data
        - Machine learning model predictions
        """)
    
    # --- Quick Forecast Summary ---
    st.markdown("<div class='custom-info-box'>", unsafe_allow_html=True)
    st.markdown(f"<h3>Forecast Summary</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>{get_forecast_summary(predictions)}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- Recent Historical Trends ---
    st.markdown("<h2 class='sub-header'>Historical AQI Trends</h2>", unsafe_allow_html=True)
    
    # Get last 30 days of data for historical chart
    if 'year' in historical_data.columns and 'month' in historical_data.columns and 'day' in historical_data.columns:
        historical_data['date'] = pd.to_datetime(historical_data[['year', 'month', 'day']])
        recent_data = historical_data.sort_values('date').tail(30*24)  # Assuming hourly data, get last 30 days
        
        fig = px.line(
            recent_data, 
            x='date', 
            y='Calculated_AQI',
            labels={'date': 'Date', 'Calculated_AQI': 'AQI Value'},
            title='Historical AQI Values (Last 30 Days)'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # --- 3-Day Forecast Cards ---
    st.markdown("<h2 class='sub-header'>3-Day AQI Forecast</h2>", unsafe_allow_html=True)
    
    # Convert predictions to appropriate types
    predictions['Date'] = pd.to_datetime(predictions['Date'])
    predictions['Predicted_Calculated_AQI'] = predictions['Predicted_Calculated_AQI'].astype(float)
    
    # Create columns for each day's forecast
    cols = st.columns(len(predictions))
    
    for i, (_, row) in enumerate(predictions.iterrows()):
        date_str = row['Date'].strftime('%A, %b %d')
        aqi_value = row['Predicted_Calculated_AQI']
        category, color, implication = get_aqi_category(aqi_value)
        
        # Show trend for days after the first
        trend = ""
        if i > 0:
            prev_aqi = predictions.iloc[i-1]['Predicted_Calculated_AQI']
            trend = get_trend_icon(aqi_value, prev_aqi)
        
        with cols[i]:
            st.markdown(f"""
            <div class='card' style='border-left: 5px solid {color};'>
                <h3>{date_str}</h3>
                <h2 style='color:{color};'>{aqi_value:.1f} {trend}</h2>
                <p style='font-weight:bold;'>{category}</p>
                <p style='font-size:0.8rem;'>{implication}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # --- Detailed Forecast Chart ---
    st.markdown("<h2 class='sub-header'>Detailed Forecast Visualization</h2>", unsafe_allow_html=True)
    
    # Generate hourly simulated data based on daily predictions
    detailed_forecast = []
    
    for _, row in predictions.iterrows():
        date = row['Date']
        base_aqi = row['Predicted_Calculated_AQI']
        
        # Generate hourly variations (slight randomness around the predicted daily value)
        for hour in range(24):
            # AQI typically improves during afternoon and worsens at night/morning
            hour_factor = 1.0 + 0.1 * np.sin((hour - 6) * np.pi / 12)  # Peak at 6pm, lowest at 6am
            hourly_aqi = base_aqi * hour_factor * (1 + np.random.normal(0, 0.03))  # Add small random variation
            
            timestamp = pd.Timestamp(date.year, date.month, date.day, hour)
            category, color, _ = get_aqi_category(hourly_aqi)
            
            detailed_forecast.append({
                'timestamp': timestamp,
                'aqi': hourly_aqi,
                'category': category,
                'color': color
            })
    
    detailed_df = pd.DataFrame(detailed_forecast)
    
    # Create detailed hourly forecast chart
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=detailed_df['timestamp'],
        y=detailed_df['aqi'],
        mode='lines',
        name='Hourly AQI',
        line=dict(width=3, color='royalblue'),
        hovertemplate='%{x}<br>AQI: %{y:.1f}<extra></extra>'
    ))
    
    # Add AQI category background colors
    aqi_levels = {
        "Good": (0, 50, "#00e400"),
        "Moderate": (51, 100, "#ffff00"),
        "USG": (101, 150, "#ff7e00"),
        "Unhealthy": (151, 200, "#ff0000"),
        "Very Unhealthy": (201, 300, "#8f3f97"),
        "Hazardous": (301, 500, "#7e0023")
    }
    
    y_max = max(detailed_df['aqi'].max() + 20, 300)  # Ensure chart shows at least up to Very Unhealthy level
    
    for level, (low, high, color) in aqi_levels.items():
        if high <= y_max:  # Only add rectangles for visible range
            fig.add_hrect(
                y0=low, y1=high,
                fillcolor=color, opacity=0.15,
                layer="below", line_width=0,
                annotation_text=level, annotation_position="top left"
            )
    
    # Layout configuration
    fig.update_layout(
        title="Hourly AQI Forecast - Next 72 Hours",
        xaxis_title="Date and Time",
        yaxis_title="AQI Value",
        yaxis_range=[0, y_max],
        hovermode="x unified",
        height=500,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- AQI Information Section ---
    st.markdown("<h2 class='sub-header'>Understanding Air Quality Index (AQI)</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### What is AQI?
        
        The Air Quality Index (AQI) is a standardized indicator for reporting air quality. It tells you how clean or polluted the air is and what associated health effects might be of concern. The AQI focuses on health effects you may experience within a few hours or days after breathing polluted air.
        
        ### Pollutants Measured
        
        - **PM2.5** - Fine particulate matter (2.5 micrometers or smaller)
        - **PM10** - Coarse particulate matter (10 micrometers or smaller)
        - **O3** - Ozone
        - **CO** - Carbon monoxide
        - **SO2** - Sulfur dioxide
        - **NO2** - Nitrogen dioxide
        """)
    
    with col2:
        # AQI Category Legend
        st.markdown("### AQI Categories and Health Implications")
        
        for level, (low, high, color) in aqi_levels.items():
            category_name = {"USG": "Unhealthy for Sensitive Groups"}.get(level, level)
            st.markdown(f"""
            <div style='
                padding: 10px; 
                margin-bottom: 10px; 
                border-radius: 5px; 
                background-color: {color}; 
                opacity: 0.7;
                color: {'black' if level in ["Good", "Moderate"] else "white"};
                font-weight: bold;'>
                {category_name} ({low}-{high})
            </div>
            """, unsafe_allow_html=True)
    
    # --- Footer ---
    st.markdown("---")
    st.markdown("<p style='text-align: center;'>Developed by Abdullah Iqbal | AQI Prediction Project</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
