"""
Electricity Prices - Spanish Electricity Market
Based on Fabra & Reguant (2014) methodology

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import sys

# Add src folder to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.text import section_title, header_banner

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Price Prediction of the Electricity Market",
    page_icon="⚡",
    layout="wide"
)

# =============================================================================
# LOAD PREDICTIONS DATA
# =============================================================================
@st.cache_data
def load_predictions():
    """Load the 2007 price predictions from CSV"""
    # Try multiple possible paths
    possible_paths = [
        'predictions_2007.csv',
        os.path.join(os.path.dirname(__file__), 'predictions_2007.csv'),
        '/Users/svenhominal/Desktop/MA3 EPFL/ECONOMICS FOR CHALLENGING TIMES/project_0501/MGT-494_Project/predictions_2007.csv'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['date'] = pd.to_datetime(df['date']).dt.date
            return df
    
    return None

predictions_df = load_predictions()

# =============================================================================
# HEADER
# =============================================================================
header_banner()

# =============================================================================
# MAIN CONTENT - PRICE PREDICTIONS
# =============================================================================

if predictions_df is not None:
    #section_title("📊 2007 Electricity Price Predictions")
    
    # Centered date/time selection
    section_title("Select Date & Time")
    
    # Center the selection controls
    col_spacer1, col_center, col_spacer2 = st.columns([1, 2, 1])
    
    with col_center:
        
        # Get min and max dates from predictions
        min_date = predictions_df['date'].min()
        max_date = predictions_df['date'].max()
        
        # Date selector
        selected_date = st.date_input(
            "Select a date in 2007 (January to June)",
            value=date(2007, 1, 21),
            min_value=min_date,
            max_value=max_date,
            help="Choose any date in 2007 (January to June) to see price predictions"
        )
        
        # Hour selector
        selected_hour = st.slider(
            "Select hour of day",
            min_value=0,
            max_value=23,
            value=17,
            help="Hour in 24h format (0 = midnight, 12 = noon, 23 = 11 PM)"
        )
        
        # Format the hour nicely
        hour_str = f"{selected_hour:02d}:00"
        if selected_hour < 12:
            hour_display = f"{selected_hour}:00 AM" if selected_hour > 0 else "12:00 AM (Midnight)"
        elif selected_hour == 12:
            hour_display = "12:00 PM (Noon)"
        else:
            hour_display = f"{selected_hour - 12}:00 PM"
        
        st.info(f"📍 Selected: **{selected_date.strftime('%A, %B %d, %Y')}** at **{hour_display}**")
    
    # Price prediction results section
    section_title("💡 Price Prediction Results")
    
    # Get the prediction for selected date and hour
    mask = (predictions_df['date'] == selected_date) & (predictions_df['hour'] == selected_hour)
    selected_row = predictions_df[mask]
    
    if len(selected_row) > 0:
        pred_price = selected_row['predicted_price'].values[0]
        actual_price = selected_row['actual_price'].values[0] if 'actual_price' in selected_row.columns else None
        
        # Calculate error if actual price is available
        if actual_price is not None and not pd.isna(actual_price):
            error = actual_price - pred_price
            pct_error = (error / actual_price) * 100
            accuracy = 100 - abs(pct_error)
        else:
            error = None
            pct_error = None
            accuracy = None
        
        # Display styled boxes
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin: 10px 0;
            ">
                <div style="color: white; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">
                    Predicted Price
                </div>
                <div style="color: white; font-size: 2.2em; font-weight: bold;">
                    {pred_price:.2f}
                </div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.85em;">
                    €/MWh
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col2:
            if actual_price is not None and not pd.isna(actual_price):
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <div style="color: white; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">
                        Actual Price
                    </div>
                    <div style="color: white; font-size: 2.2em; font-weight: bold;">
                        {actual_price:.2f}
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.85em;">
                        €/MWh
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <div style="color: white; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">
                        Actual Price
                    </div>
                    <div style="color: white; font-size: 2.2em; font-weight: bold;">
                        N/A
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.85em;">
                        Not available
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with metric_col3:
            if error is not None:
                # Color based on error magnitude
                if abs(pct_error) <= 5:
                    gradient = "linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)"
                    status_icon = "✅"
                elif abs(pct_error) <= 15:
                    gradient = "linear-gradient(135deg, #f39c12 0%, #e67e22 100%)"
                    status_icon = "⚠️"
                else:
                    gradient = "linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)"
                    status_icon = "❌"
                
                st.markdown(f"""
                <div style="
                    background: {gradient};
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <div style="color: white; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">
                        {status_icon} Prediction Error
                    </div>
                    <div style="color: white; font-size: 2.2em; font-weight: bold;">
                        {error:+.2f}
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.85em;">
                        €/MWh ({pct_error:+.1f}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <div style="color: white; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">
                        📊 Prediction Error
                    </div>
                    <div style="color: white; font-size: 2.2em; font-weight: bold;">
                        N/A
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.85em;">
                        Not available
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Accuracy banner
        if accuracy is not None:
            if accuracy >= 80:
                banner_color = "#27ae60"
                banner_text = f"✅ Excellent prediction accuracy: {accuracy:.1f}%"
            elif accuracy >= 60:
                banner_color = "#f39c12"
                banner_text = f"ℹ️ Good prediction accuracy: {accuracy:.1f}%"
            else:
                banner_color = "#e74c3c"
                banner_text = f"⚠️ Moderate prediction accuracy: {accuracy:.1f}%"
            
            st.markdown(f"""
            <div style="
                background-color: {banner_color};
                color: white;
                padding: 12px 20px;
                border-radius: 10px;
                text-align: center;
                font-weight: 600;
                margin-top: 15px;
            ">
                {banner_text}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No prediction available for the selected date and time.")
    
    # =============================================================================
    # DAILY PROFILE CHART
    # =============================================================================
    section_title("📈 Daily Price Profile")
    
    # Get all hours for the selected date
    day_data = predictions_df[predictions_df['date'] == selected_date].copy()
    
    if len(day_data) > 0:
        # Create the chart
        fig = go.Figure()
        
        # Add predicted prices
        fig.add_trace(go.Scatter(
            x=day_data['hour'],
            y=day_data['predicted_price'],
            mode='lines+markers',
            name='Predicted Price',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8),
            hovertemplate='Hour %{x}:00<br>Predicted: %{y:.2f} €/MWh<extra></extra>'
        ))
        
        # Add actual prices if available
        if 'actual_price' in day_data.columns and day_data['actual_price'].notna().any():
            fig.add_trace(go.Scatter(
                x=day_data['hour'],
                y=day_data['actual_price'],
                mode='lines+markers',
                name='Actual Price',
                line=dict(color='#4ECDC4', width=3),
                marker=dict(size=8),
                hovertemplate='Hour %{x}:00<br>Actual: %{y:.2f} €/MWh<extra></extra>'
            ))
        
        # Mark the selected hour
        fig.add_vline(
            x=selected_hour,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Selected: {hour_str}"
        )
        
        fig.update_layout(
            title=f"Hourly Electricity Prices - {selected_date.strftime('%A, %B %d, %Y')}",
            xaxis_title="Hour of Day",
            yaxis_title="Price (€/MWh)",
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    
    # =============================================================================
    # MODEL INFO EXPANDER
    # =============================================================================
    with st.expander("About the Prediction Model"):
        st.markdown("""
        ### LightGBM Price Forecasting Model
        
        **Training Data:** 2005-2006 Spanish electricity market data (~17,000 observations)
        
        **Features Used:**
        - **Temporal:** Hour, day of week, month, season
        - **Fuel Costs:** Gas, coal, oil (Brent) prices
        - **Carbon:** Emissions price and rate
        - **Weather:** Temperature, wind conditions
        
        **Model Performance:**
        | Dataset | RMSE (€/MWh) | R² |
        |---------|-------------|-----|
        | Training (2005-Aug 2006) | ~4.5 | ~0.85 |
        | Validation (Sep-Dec 2006) | ~4.8 | ~0.82 |
        | Test (2007) | ~5.2 | ~0.78 |
        
        *Model trained to avoid data leakage with time-based validation split.*
        """)
    
    # =============================================================================
    # BUSINESS VALUE & PASS-THROUGH SECTION
    # =============================================================================
    section_title("💼 Why Price Prediction Matters for Electricity Generators")
    
    st.markdown("""
    <div style="
        background: #e9ecef;
        padding: 25px;
        border-radius: 15px;
        color: #333;
        margin: 20px 0;
    ">
        <h3 style="color: #DAA520; margin-bottom: 15px;">🎯 Strategic Value for Coal & CCGT Power Plants</h3>
        <p style="font-size: 1.05em; line-height: 1.6;">
        For electricity producers operating <strong>coal-fired</strong> and <strong>CCGT (Combined Cycle Gas Turbine)</strong> plants, 
        accurate price predictions are critical for optimizing bidding strategies and maximizing profitability in wholesale markets.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Three columns for use cases
    use_col1, use_col2, use_col3 = st.columns(3)
    
    with use_col1:
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #DAA520;
            height: 300px;
        ">
            <h4 style="color: #DAA520;">Optimal Bidding Strategy</h4>
            <p style="font-size: 0.95em;">
            <strong>Predict clearing prices</strong> to optimize hourly bids in the wholesale market.
            </p>
            <p style="font-size: 0.85em; color: #666;">
            <em>Example:</em> A CCGT plant operator can anticipate peak-hour prices and bid strategically 
            to maximize margins when gas costs are favorable.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with use_col2:
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #4ECDC4;
            height: 300px;
        ">
            <h4 style="color: #4ECDC4;">Merit Order Positioning</h4>
            <p style="font-size: 0.95em;">
            <strong>Understand where your plant sits</strong> in the supply curve based on fuel and carbon costs.
            </p>
            <p style="font-size: 0.85em; color: #666;">
            <em>Example:</em> Coal plants with higher emissions (~0.9 tCO₂/MWh) face different carbon costs 
            than CCGT (~0.4 tCO₂/MWh), affecting competitive position.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with use_col3:
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #27ae60;
            height: 300px;
        ">
            <h4 style="color: #27ae60;">Revenue Forecasting</h4>
            <p style="font-size: 0.95em;">
            <strong>Project revenues</strong> for financial planning and investment decisions.
            </p>
            <p style="font-size: 0.85em; color: #666;">
            <em>Example:</em> Plant managers can forecast daily revenues and schedule maintenance 
            during predicted low-price periods to minimize opportunity costs.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pass-through insight section
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    pt_col1, pt_col2 = st.columns(2)
    
    with pt_col1:
        st.markdown("""
        <div style="
            background: #fff3cd;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #DAA520;
        ">
            <h4 style="color: #856404;">🏭 Coal Plant Implications</h4>
            <ul style="font-size: 0.95em; color: #856404;">
                <li>Higher emission rate (~0.9 tCO₂/MWh) = larger carbon cost exposure</li>
                <li>When carbon prices rise, coal becomes <strong>less competitive</strong> vs CCGT</li>
                <li>Pass-through allows partial cost recovery but <strong>not full</strong> (83% < 100%)</li>
                <li>Strategic: Hedge carbon allowances in forward markets</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with pt_col2:
        st.markdown("""
        <div style="
            background: #d4edda;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #27ae60;
        ">
            <h4 style="color: #155724;">⚡ CCGT Plant Advantages</h4>
            <ul style="font-size: 0.95em; color: #155724;">
                <li>Lower emission rate (~0.4 tCO₂/MWh) = smaller carbon burden</li>
                <li>Rising carbon prices improve <strong>relative competitiveness</strong></li>
                <li>Faster ramping enables capturing <strong>peak price hours</strong></li>
                <li>Strategic: Monitor gas/carbon price ratio for optimal dispatch</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    

else:
    st.warning("""
    ⚠️ **Predictions data not found!**
    
    To enable price predictions:
    1. Run the LightGBM model training cells in `extension_code_sven.ipynb`
    2. Execute the cell that saves predictions to `predictions_2007.csv`
    3. Refresh this page
    """)
    
    st.info("Once the predictions file is generated, you'll be able to look up electricity prices for any date and hour in 2007!")


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>MGT-494 Economics for Challenging Times | EPFL | 2025</p>
    <p>Based on analysis of Spanish electricity market data (2005-2006)</p>
</div>
""", unsafe_allow_html=True)
