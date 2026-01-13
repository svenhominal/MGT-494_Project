import streamlit as st
 

def header_banner():
    """
    Affiche un bandeau de titre
    """
    st.markdown("""
    <style>
        @media (max-width: 768px) {
            .header-title { font-size: 1.4em !important; }
            .header-slogan { font-size: 0.75em !important; letter-spacing: 1px !important; }
        }
    </style>
    <div style="
        background-color: #DAA520;
        color: white;
        padding: 10px 20px;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        flex-wrap: wrap;
        gap: 8px;
    ">
        <div class="header-title" style="
            font-size: 1.8em;
            font-weight: bold;
            margin: 0;
        ">
            Price Predictor
        </div>
        <div class="header-slogan" style="
            font-size: 1em;
            font-weight: bold;
            letter-spacing: 2px;
            margin: 0;
        ">
            EPFL 
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_title(title_text):
    """
    Affiche un titre de section stylisé de manière cohérente
    
    Args:
        title_text (str): Le texte du titre de la section
    """
    st.markdown(f"""
    <div style="margin: 32px 0 17px 0;">
        <h3 style="text-align: center; color: #DAA520; padding-bottom: 8px; border-bottom: 2px solid #DAA520;">
            {title_text}
        </h3>
    </div>
    """, unsafe_allow_html=True)

def project_card_design(name, project_type, area, co2_absorbed, available_credits, unit_price, benefits, image_url):
    """
    Displays a beautifully designed project card using Streamlit components
    """
    # Use Streamlit container for better rendering
    with st.container():
        # Header section with project name
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
            padding: 20px;
            border-radius: 15px 15px 0 0;
            color: white;
            margin-bottom: 0;
        ">
            <h2 style="margin: 0; font-size: 1.8em; font-weight: bold;">🌿 {name}</h2>
            <p style="margin: 5px 0 0 0; font-size: 1.1em; opacity: 0.9;">{project_type}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main content section
        st.markdown(f"""
        <div style="
            border: 2px solid #1b5e20;
            border-top: none;
            border-radius: 0 0 15px 15px;
            padding: 20px;
            background: #f8f9fa;
        ">
        """, unsafe_allow_html=True)
        
        # Info grid using Streamlit columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: rgba(27, 94, 32, 0.1); border-radius: 8px;">
                <div style="font-weight: bold; color: #1b5e20;">🏞️ Area</div>
                <div style="font-size: 1.1em;">{area}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: rgba(27, 94, 32, 0.1); border-radius: 8px;">
                <div style="font-weight: bold; color: #1b5e20;">🍃 CO₂ Absorbed</div>
                <div style="font-size: 1.1em;">{co2_absorbed}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: rgba(27, 94, 32, 0.1); border-radius: 8px;">
                <div style="font-weight: bold; color: #1b5e20;">💰 Unit Price</div>
                <div style="font-size: 1.1em;">{unit_price} CHF</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: rgba(27, 94, 32, 0.1); border-radius: 8px;">
                <div style="font-weight: bold; color: #1b5e20;">🌿 Available Offsets</div>
                <div style="font-size: 1.1em;">{available_credits}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Benefits section
        benefits_text = " • ".join(benefits)
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        ">
            <div style="font-weight: bold; color: #1b5e20; margin-bottom: 8px;">🌱 Environmental Benefits:</div>
            <div style="color: #2e7d32;">• {benefits_text}</div>
        </div>
        """, unsafe_allow_html=True)
        

        
        # Close main content div
        st.markdown("</div>", unsafe_allow_html=True)