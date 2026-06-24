import os
import requests
import streamlit as st
from dotenv import load_dotenv

st.set_page_config(
    page_title="IPO Profitability Predictor",
    page_icon="👾",
    layout="centered"
)

st.title("IPO Listing Gain Prediction System")
st.markdown("""
This system routes subscription data directly to a containerized Random Forest 
inference engine to evaluate day-one market profitability.
""")
st.write("---")

# Organize inputs into two columns
col1, col2 = st.columns(2)

with col1:
    issue_size = st.number_input("Issue Size (crores)", min_value=1.0, value=450.0, step=10.0)
    qib = st.number_input("QIB (Institutional Subscription Multiple)", min_value=0.0, value=55.4, step=0.5)
    hni = st.number_input("HNI (High Net-Worth Subscription Multiple)", min_value=0.0, value=12.1, step=0.5)

with col2:
    offer_price = st.number_input("Offer Price (INR)", min_value=1.0, value=250.0, step=5.0)
    rii = st.number_input("RII (Retail Subscription Multiple)", min_value=0.0, value=4.5, step=0.5)
    total = st.number_input("Total Overall Subscription Multiple", min_value=0.0, value=24.3, step=0.5)

st.write("---")

if st.button("Analyze Market Profitability", use_container_width=True):

    payload = {
        "Issue_Size(crores)": issue_size,
        "QIB": qib,
        "HNI": hni,
        "RII": rii,
        "Total": total,
        "Offer Price": offer_price
    }

    load_dotenv()
    API_KEY_SECRET = st.secrets.get("API_KEY_SECRET") or os.getenv("API_KEY_SECRET")
    if not API_KEY_SECRET:
    st.error("Missing API Security Key configuration. Please check your .env file or Streamlit Secrets panel.")
    st.stop()
    
    headers = {
        "X-API-KEY": API_KEY_SECRET
    }
    
    # local Docker container URL gateway
    container_url = "http://44.222.149.171:8000/predict"
    
    try:
        with st.spinner("Executing the model"):
            response = requests.post(container_url, json=payload, headers=headers, timeout=5)
            
        if response.status_code == 200:
            result = response.json()
            probability = result["profit_probability"]
            signal = result["profitable_class_signal"]
            
            if signal == "SUCCESS":
                st.success(f"### Signal: {signal}")
                st.metric(label="Model Confidence Level", value=f"{probability}%")
                st.info("The subscription demand profile indicates a strong institutional backstop. Safe market configuration.")
            else:
                st.warning(f"### Signal: HIGH RISK / WARNING")
                st.metric(label="Model Confidence Level", value=f"{probability}%")
                st.error("The current data distributions point toward an unbacked retail-trap or overvalued supply constraint.")
        elif response.status_code == 403:
            st.error("Access Denied (403): Your Streamlit app failed to authenticate with the secure backend.")
        else:
            st.error(f"Container Error: Returned HTTP Status Code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("Connection Refused! Make sure your Docker container is running on port 8000.")
