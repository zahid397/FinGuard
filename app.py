import streamlit as st
import pandas as pd
import datetime
import json
import os
from cryptography.fernet import Fernet
import plotly.express as px
import google.generativeai as genai

# ============================
# 🚀 PAGE CONFIGURATION
# ============================
st.set_page_config(
    page_title="🏆 FinGuard Ultra Pro — ICT Innovation Award Edition",
    page_icon="💰",
    layout="wide"
)

# ============================
# 🎨 WHITE + GOLD UI + LOGO
# ============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Poppins', sans-serif;
    background-color: #FFFFFF !important;
}

.stApp { background-color: #FFFFFF !important; }

[data-testid="stSidebar"] {
    background-color: #FAFAFA !important;
}

/* Glowing gold text animation */
@keyframes goldGlow {
  0% { text-shadow: 0 0 5px #FFD700, 0 0 10px #FFD700; }
  50% { text-shadow: 0 0 25px #FFD700, 0 0 50px #FFCC00; }
  100% { text-shadow: 0 0 5px #FFD700, 0 0 10px #FFD700; }
}

/* Title */
.title-container { text-align: center; margin-bottom: 25px; }
.title-text {
    display: inline-block;
    color: #B8860B;
    font-size: 2.8em;
    font-weight: 700;
    animation: goldGlow 2.5s infinite ease-in-out;
    margin-left: 10px;
    vertical-align: middle;
}

.logo-img {
    width: 85px;
    height: 85px;
    vertical-align: middle;
    animation: pulse 3s infinite ease-in-out;
}

@keyframes pulse {
  0% { transform: scale(1); filter: drop-shadow(0 0 6px gold); }
  50% { transform: scale(1.08); filter: drop-shadow(0 0 18px gold); }
  100% { transform: scale(1); filter: drop-shadow(0 0 6px gold); }
}

p.subtext {
    text-align: center;
    color: #333;
    margin-bottom: 25px;
    font-size: 1.05em;
}

/* Buttons */
.stButton>button {
    background-color: #FFFFFF !important;
    color: #111111 !important;
    border: 1px solid #E0E0E0 !important;
    border-radius: 10px !important;
    font-weight: 600;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #FFF8E1 !important;
    transform: scale(1.03);
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: #111 !important;
}
.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #FFD700 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================
# 🪙 LOGO + TITLE
# ============================
st.markdown("""
<div class="title-container">
    <img src="https://files.oaiusercontent.com/file-Np6QmLJ1m6uSgBPnqQnMY1B7?se=2025-12-31T00%3A00%3A00Z&sp=r&sv=2022-11-02&sr=b&rscd=inline%3Bfilename%3Dfinlogo.png" 
         class="logo-img" alt="FinGuard Logo"/>
    <span class="title-text">FinGuard Ultra Pro</span>
</div>
<p class="subtext">🏆 Official ICT Innovation Award 2025 Edition | Presidency University 💡</p>
""", unsafe_allow_html=True)

# ============================
# 🔐 ENCRYPTION SYSTEM
# ============================
KEY_FILE = "secret.key"
DATA_FILE = "expenses_encrypted.json"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)

def encrypt_data(data):
    return fernet.encrypt(json.dumps(data).encode()).decode()

def decrypt_data(data):
    try:
        return json.loads(fernet.decrypt(data.encode()).decode())
    except:
        return []

# ============================
# 📦 DATA MANAGEMENT
# ============================
CATEGORIES = [
    "🍕 Food", "🏠 Rent", "🚗 Transport", "💡 Utilities", 
    "🎓 Education", "💊 Health", "🛍️ Shopping", "🎬 Entertainment"
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
    with open(DATA_FILE, "r") as f:
        enc = f.read().strip()
    return pd.DataFrame(decrypt_data(enc)) if enc else pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

def save_data(df):
    df["Date"] = df["Date"].astype(str)
    with open(DATA_FILE, "w") as f:
        f.write(encrypt_data(df.to_dict("records")))

# ============================
# 🤖 AI SETUP
# ============================
@st.cache_resource
def setup_gemini():
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if not key:
            return None
        genai.configure(api_key=key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except:
        return None

def ai_reply(model, df, q):
    if df.empty:
        return "⚠️ Please add some expenses first!"
    total = df["Amount"].sum()
    cat_sum = df.groupby("Category")["Amount"].sum().to_dict()
    if model:
        try:
            prompt = f"You are FinGuard AI from Presidency University. Analyze {cat_sum} (Total ₹{total:,.2f}). Question: {q}. Reply in English+Bangla mix within 2 lines."
            return model.generate_content(prompt).text
        except:
            pass
    top_cat = max(cat_sum, key=cat_sum.get)
    return f"🤖 Offline Mode: Most spent on **{top_cat}**. Save a little next time — proud of your effort! 💪"

# ============================
# 🧠 SESSION STATE
# ============================
if "df" not in st.session_state:
    st.session_state.df = load_data()

model = setup_gemini()

# ============================
# 📊 APP TABS
# ============================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Expense", "🤖 AI Assistant", "🏅 About"])

# --- Dashboard ---
with tab1:
    df = st.session_state.df
    if df.empty:
        st.info("No data yet. Add your first expense to get started.")
    else:
        total = df["Amount"].sum()
        st.metric("💰 Total Spent", f"₹{total:,.2f}")
        fig = px.pie(df, names="Category", values="Amount", hole=0.3, title="Spending by Category")
        st.plotly_chart(fig, use_container_width=True)

# --- Add Expense ---
with tab2:
    with st.form("add_form", clear_on_submit=True):
        date = st.date_input("🗓️ Date", datetime.date.today())
        cat = st.selectbox("Category", CATEGORIES)
        desc = st.text_input("Description")
        amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        submit = st.form_submit_button("✅ Add Expense")
        if submit:
            new = pd.DataFrame([[date, cat, desc, amt]], columns=["Date", "Category", "Description", "Amount"])
            st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
            save_data(st.session_state.df)
            st.success("✅ Expense added successfully!")

# --- AI Assistant ---
with tab3:
    st.subheader("💬 Ask FinGuard AI")
    q = st.text_area("Ask your question (English/Bangla mix supported):")
    if st.button("🤖 Analyze"):
        st.write(ai_reply(model, st.session_state.df, q))

# --- ABOUT TAB ---
with tab4:
    st.markdown("---")
    st.markdown("""
    ## 🏆 FinGuard Ultra Pro — ICT Innovation Award 2025 Edition

    **FinGuard Ultra Pro** is an AI-driven financial management platform proudly developed in Bangladesh 🇧🇩,  
    combining security, intelligence, and simplicity for the modern digital economy.

    ### ✨ Highlights
    - 🔐 AES Encrypted Expense Data  
    - 🤖 Gemini AI + Offline Hybrid Mode  
    - 📊 Real-time Visualization  
    - 💡 Smart Budget Insights  
    - 🧠 Built for Digital Bangladesh Vision 2041  

    ### 🎖️ Recognition
    Developed for **ICT Innovation Award 2025** under the  
    National AI Startup Acceleration Program.

    **👨‍💻 Developer:** Zahid Hasan  
    **🏛️ Institution:** Presidency University, Bangladesh  
    **📅 Build Date:** October 2025  

    Made with ❤️ using **Python**, **Streamlit**, and **Google Gemini AI**
    """)
