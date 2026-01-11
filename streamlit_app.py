"""
Carbon Pass-through Simulator - Spanish Electricity Market
Based on Fabra & Reguant (2014) methodology

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Price Prediction and Carbon Pass-through Simulator",
    page_icon="⚡",
    layout="wide"
)

# =============================================================================
# HEADER
# =============================================================================
st.title("Price Prediction and Carbon Cost Pass-through Simulator")
st.markdown("""
**Spanish Electricity Market Analysis (2005-2006)**

This interactive tool demonstrates how carbon costs are passed through to electricity prices,
based on our empirical analysis following [Fabra & Reguant (2014)](https://www.aeaweb.org/articles?id=10.1257/aer.104.9.2872).

---
""")


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
