import streamlit as st
import pandas as pd
import datetime
import json
import os
from cryptography.fernet import Fernet
import plotly.express as px
import google.generativeai as genai

# =============================
# ⚙️ PAGE CONFIG
# =============================
st.set_page_config(page_title="💰 FinGuard Ultra Pro", page_icon="🪙", layout="wide")

# =============================
# 🎨 WHITE + GOLD UI
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
html, body, [class*="st-"] {font-family:'Poppins',sans-serif;background-color:#fff!important;color:#111;}
.stApp{background-color:#fff!important;}
[data-testid="stSidebar"]{background-color:#FAFAFA!important;}
.title{color:#B8860B;font-weight:700;text-align:center;font-size:2.6em;margin-bottom:0;}
.subtext{text-align:center;color:#555;margin-bottom:25px;}
.stButton>button{background-color:#fff;color:#111;border:1px solid #E0E0E0;border-radius:10px;font-weight:600;transition:0.3s;}
.stButton>button:hover{background-color:#FFF8E1;transform:scale(1.03);}
.stTabs [data-baseweb="tab"]{font-weight:600;color:#111!important;}
.stTabs [aria-selected="true"]{border-bottom:3px solid #FFD700!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>💰 FinGuard Ultra Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Presidency University Edition | Your Smart AI Financial Guardian 💡</p>", unsafe_allow_html=True)

# =============================
# 🔐 ENCRYPTION SETUP
# =============================
KEY_FILE = "secret.key"
DATA_FILE = "expenses.json"
BANK_FILE = "bank.json"
BUDGET_FILE = "budget.json"

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

def decrypt_data(token):
    try:
        return json.loads(fernet.decrypt(token.encode()).decode())
    except Exception:
        return []

def load_data(file, cols):
    if not os.path.exists(file):
        return pd.DataFrame(columns=cols)
    with open(file, "r") as f:
        enc = f.read().strip()
    if not enc:
        return pd.DataFrame(columns=cols)
    data = decrypt_data(enc)
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame(columns=cols)

def save_data(file, df):
    df2 = df.copy()
    df2["Date"] = df2["Date"].astype(str)
    recs = df2.to_dict("records")
    token = encrypt_data(recs)
    with open(file, "w") as f:
        f.write(token)

# =============================
# 🤖 GEMINI AI (v2.5 FLASH)
# =============================
@st.cache_resource
def setup_gemini():
    key = st.secrets.get("GEMINI_API_KEY")
    if not key:
        st.warning("⚠️ Gemini API Key missing — running in offline mode.")
        return None
    genai.configure(api_key=key)
    try:
        return genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        st.error(f"Gemini init failed: {e}")
        return None

model = setup_gemini()

def ai_reply(df, q):
    if df.empty:
        return "⚠️ Please add some expense data first!"
    df2 = df.copy()
    df2["Amount"] = pd.to_numeric(df2["Amount"], errors="coerce").fillna(0)
    total = df2["Amount"].sum()
    cat_sum = df2.groupby("Category")["Amount"].sum().to_dict()

    if model:
        try:
            prompt = f"""
            You are FinGuard AI 2.5 — a financial assistant.
            Analyze: {cat_sum}, Total ₹{total}.
            Question: {q}
            Reply briefly (English + Bengali mix, 2 lines max).
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.warning(f"AI Error (fallback mode): {e}")

    # Offline fallback
    if cat_sum:
        top = max(cat_sum, key=cat_sum.get)
        return f"🤖 Offline Mode: Highest spending on **{top}**. Try saving more next month 💡"
    return "No data available."

# =============================
# 💰 FRAUD DETECTION
# =============================
def detect_fraud(desc, amt):
    risky = ["lottery", "reward", "gift", "otp", "offer", "refund", "crypto", "bonus"]
    return any(k in desc.lower() for k in risky) or amt > 100000

# =============================
# 🧠 SESSION DATA
# =============================
if "expenses" not in st.session_state:
    st.session_state.expenses = load_data(DATA_FILE, ["Date","Category","Description","Amount"])
if "bank" not in st.session_state:
    st.session_state.bank = load_data(BANK_FILE, ["Date","Type","Amount","Balance"])
if "budget" not in st.session_state:
    st.session_state.budget = load_data(BUDGET_FILE, ["Date","Daily","Monthly"])

# =============================
# 📊 MAIN LAYOUT
# =============================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Dashboard", "💵 Add Expense", "🏦 Bank", "📅 Budget", "🤖 AI Assistant", "ℹ️ About"
])

# --- DASHBOARD ---
with tab1:
    st.subheader("📊 Financial Overview")
    df = st.session_state.expenses
    if df.empty:
        st.info("No expense data yet. Add something to begin tracking.")
    else:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        total = df["Amount"].sum()
        st.metric("💰 Total Spent", f"₹{total:,.2f}")

        fig_pie = px.pie(df, names="Category", values="Amount",
                         title="Spending by Category", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

        daily = df.groupby(df["Date"].dt.date)["Amount"].sum().reset_index()
        fig_bar = px.bar(daily, x="Date", y="Amount",
                         title="Daily Spending Trend", color="Amount",
                         color_continuous_scale="YlOrBr")
        st.plotly_chart(fig_bar, use_container_width=True)

# --- ADD EXPENSE ---
with tab2:
    st.subheader("💵 Add Expense")
    with st.form("expense_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.date.today())
        cat = st.selectbox("Category", [
            "🍕 Food", "🏠 Rent", "🚗 Transport", "💡 Utilities", 
            "🎓 Education", "💊 Health", "🎬 Entertainment", "🛍️ Shopping"
        ])
        desc = st.text_input("Description")
        amt = st.number_input("Amount ₹", min_value=0.0, format="%f")
        submitted = st.form_submit_button("✅ Add Expense")

        if submitted:
            if amt <= 0:
                st.error("Amount must be greater than 0.")
            else:
                if detect_fraud(desc, amt):
                    st.warning("🚨 Suspicious transaction detected!")
                new = pd.DataFrame([[date, cat, desc, amt]],
                                   columns=["Date","Category","Description","Amount"])
                st.session_state.expenses = pd.concat([st.session_state.expenses, new], ignore_index=True)
                save_data(DATA_FILE, st.session_state.expenses)
                st.success("Expense added successfully ✅")

# --- BANK ---
with tab3:
    st.subheader("🏦 Bank Management")
    bank = st.session_state.bank
    balance = bank["Balance"].iloc[-1] if not bank.empty else 0.0
    st.metric("Current Balance", f"₹{balance:,.2f}")

    col1, col2 = st.columns(2)
    with col1:
        amt = st.number_input("Deposit / Withdraw ₹", min_value=0.0, format="%f")
    with col2:
        action = st.radio("Select Action", ["Deposit", "Withdraw"])

    if st.button("💰 Confirm Transaction"):
        if action == "Withdraw" and amt > balance:
            st.error("❌ Insufficient balance.")
        else:
            new_balance = balance + amt if action == "Deposit" else balance - amt
            new = pd.DataFrame([[datetime.date.today(), action, amt, new_balance]],
                               columns=["Date","Type","Amount","Balance"])
            st.session_state.bank = pd.concat([bank, new], ignore_index=True)
            save_data(BANK_FILE, st.session_state.bank)
            st.success(f"{action} successful ✅ New Balance: ₹{new_balance:,.2f}")

    if not bank.empty:
        st.markdown("### 📜 Transaction History")
        st.dataframe(bank.sort_values("Date", ascending=False), use_container_width=True)

# --- BUDGET ---
with tab4:
    st.subheader("📅 Daily & Monthly Budget")
    daily = st.number_input("Set Daily Limit ₹", min_value=0.0, format="%f")
    monthly = st.number_input("Set Monthly Limit ₹", min_value=0.0, format="%f")
    if st.button("💾 Save Budget"):
        new = pd.DataFrame([[datetime.date.today(), daily, monthly]],
                           columns=["Date","Daily","Monthly"])
        st.session_state.budget = new
        save_data(BUDGET_FILE, new)
        st.success("Budget updated ✅")

    if not st.session_state.expenses.empty:
        df = st.session_state.expenses.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        today = datetime.date.today()
        month_start = today.replace(day=1)
        spent_today = df[df["Date"].dt.date == today]["Amount"].sum()
        spent_month = df[df["Date"].dt.date >= month_start]["Amount"].sum()
        st.info(f"🕒 Today: ₹{spent_today:,.2f} / ₹{daily:,.2f} | Month: ₹{spent_month:,.2f} / ₹{monthly:,.2f}")

# --- AI ASSISTANT ---
with tab5:
    st.subheader("🤖 FinGuard AI Assistant (Gemini 2.5 Flash)")
    q = st.text_area("Ask your question:")
    if st.button("🚀 Ask AI"):
        st.write(ai_reply(st.session_state.expenses, q))

# --- ABOUT ---
with tab6:
    st.markdown("""
    ---
    ### ℹ️ About FinGuard Ultra Pro
    🪙 **FinGuard Ultra Pro — Presidency University Edition (v3.2)**  
    Smart, Secure, AI-powered Finance Tracker with Banking System.

    **✨ Features**
    - 🔐 AES-secured encrypted data  
    - 💰 Track expenses, bank & budget  
    - 💡 Gemini 2.5 Flash AI + fraud detection  
    - 📊 Pie & Bar chart visualization  
    - 🏫 Presidency University Integration  

    **👨‍💻 Developer:** Zahid Hasan  
    **🎓 Institute:** Presidency University  
    **🏆 ICT Innovation Award 2025 Submission**  
    Built with ❤️ using Python, Streamlit & Google Gemini 2.5.
    ---
    """)
