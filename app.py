import streamlit as st
import pandas as pd
import datetime
import json
import os
from cryptography.fernet import Fernet, InvalidToken
import google.generativeai as genai

# ============================
# 🚀 CONFIGURATION
# ============================
st.set_page_config(
    page_title="FinGuard — AI Smart Expense & Budget Companion",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ✅ Force Light Theme
st.markdown("""
    <style>
        :root {
            color-scheme: light;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)
# ✅ Fix for faded tab text & icons
st.markdown("""
    <style>
        /* Tabs text & icon color */
        .stTabs [data-baseweb="tab"] p {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        /* Selected tab underline */
        .stTabs [aria-selected="true"] {
            border-bottom: 3px solid #e50914 !important;
        }
    </style>
""", unsafe_allow_html=True)
# 🎨 Premium Polish
st.markdown("""
    <style>
        /* Card look for inputs and buttons */
        div[data-testid="stNumberInput"], div[data-testid="stTextInput"], div[data-testid="stSelectbox"], textarea {
            border-radius: 10px !important;
            border: 1px solid #ddd !important;
            background-color: #f9f9f9 !important;
            color: #000 !important;
        }
        button[kind="secondary"], button[kind="primary"] {
            background-color: #0d47a1 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 8px 20px !important;
        }
        button[kind="primary"]:hover {
            background-color: #1565c0 !important;
        }
        /* Metric card polish */
        div[data-testid="stMetricValue"] {
            color: #0d47a1 !important;
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)
# 🌈 FinGuard Premium Glow Theme
st.markdown("""
<style>
    /* Gradient header + title glow */
    h1, h2, h3 {
        background: linear-gradient(90deg, #004aad, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: 0.5px;
    }

    /* App header section */
    .stAppHeader {
        background: linear-gradient(90deg, #004aad, #00b4d8);
        color: white !important;
        font-weight: bold;
        text-shadow: 0px 0px 8px rgba(255,255,255,0.5);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    /* Tabs hover glow */
    .stTabs [data-baseweb="tab"]:hover p {
        color: #004aad !important;
        text-shadow: 0px 0px 6px rgba(0, 74, 173, 0.4);
    }

    /* Button glow effect */
    button[kind="primary"] {
        box-shadow: 0px 0px 10px rgba(0, 74, 173, 0.4);
        transition: 0.3s ease;
    }
    button[kind="primary"]:hover {
        transform: scale(1.03);
        box-shadow: 0px 0px 14px rgba(0, 74, 173, 0.7);
    }

    /* Card soft shadow */
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"], div[data-testid="stSelectbox"], textarea {
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ============================
# 🔐 AES ENCRYPTION SETUP
# ============================
KEY_FILE = "secret.key"
DATA_FILE = "expenses.json"
BUDGET_FILE = "budget.json"
USER_FILE = "user.json"

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
    except InvalidToken:
        return []

# ============================
# 👤 USER AUTHENTICATION
# ============================
def register_user(username, password):
    user_data = {"username": username, "password": password}
    with open(USER_FILE, "w") as f:
        json.dump(user_data, f)

def verify_user(username, password):
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            user = json.load(f)
        return user["username"] == username and user["password"] == password
    return False

# ============================
# 📦 DATA MANAGEMENT
# ============================
CATEGORY_OPTIONS = [
    "Food", "Transport", "Rent", "Utilities", "Entertainment",
    "Shopping", "Education", "Health", "Others"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            encrypted = f.read().strip()
            if encrypted:
                data = decrypt_data(encrypted)
                return pd.DataFrame(data)
    return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

def save_data(df):
    df["Date"] = df["Date"].astype(str)
    encrypted = encrypt_data(df.to_dict("records"))
    with open(DATA_FILE, "w") as f:
        f.write(encrypted)

def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            return json.load(f).get("monthly_budget", 0.0)
    return 0.0

def save_budget(budget):
    with open(BUDGET_FILE, "w") as f:
        json.dump({"monthly_budget": budget}, f, indent=4)

# ============================
# 🚨 FRAUD DETECTION SYSTEM
# ============================
def detect_fraud(description):
    suspicious_words = ["lottery", "reward", "gift", "refund", "offer", "otp", "prize"]
    desc_lower = description.lower()
    return any(word in desc_lower for word in suspicious_words)

# ============================
# 🤖 GEMINI AI SETUP
# ============================
@st.cache_resource
def setup_gemini():
    if "GEMINI_API_KEY" not in st.secrets:
        st.warning("⚠️ Gemini API Key missing! Add it in .streamlit/secrets.toml")
        return None
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        st.error(f"Gemini setup failed: {e}")
        return None

def ask_ai(model, question, df):
    if model is None or df.empty:
        return "⚠️ ডেটা যোগ করুন অথবা API Key দিন।"
    summary = df.groupby("Category")["Amount"].sum().to_dict()
    total = df["Amount"].sum()
    prompt = f"""
You are FinGuard — a smart Bengali financial assistant.
Context: Total Expense ₹{total}, Breakdown: {summary}.
Question: {question}
Respond in short, clear Bengali sentences.
"""
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"AI error: {e}"

# ============================
# 🧠 SESSION STATE
# ============================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "expense_df" not in st.session_state:
    st.session_state["expense_df"] = load_data()
if "monthly_budget" not in st.session_state:
    st.session_state["monthly_budget"] = load_budget()

df = st.session_state["expense_df"]
model = setup_gemini()

# ============================
# 👤 LOGIN SCREEN
# ============================
if not st.session_state["logged_in"]:
    st.title("🔐 FinGuard Secure Login")
    option = st.radio("Select an option:", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Register" and st.button("Create Account"):
        register_user(username, password)
        st.success("✅ Account created successfully!")

    if option == "Login" and st.button("Login"):
        if verify_user(username, password):
            st.session_state["logged_in"] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

# ============================
# 🧭 TABS
# ============================
tab1, tab2, tab3, tab4 = st.tabs(["📊 ড্যাশবোর্ড", "➕ খরচ যোগ করুন", "🤖 AI সহায়ক", "ℹ️ সম্পর্কে"])

# ============================
# TAB 1 — DASHBOARD
# ============================
with tab1:
    st.subheader("📈 ব্যয়ের বিশ্লেষণ")
    if not df.empty:
        total = df["Amount"].sum()
        st.metric("💰 মোট খরচ", f"₹{total:,.2f}")

        start_of_month = pd.Timestamp(datetime.date.today().replace(day=1))
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        monthly = df[df["Date"] >= start_of_month]

        st.metric("💳 এই মাসের খরচ", f"₹{monthly['Amount'].sum():,.2f}")
        st.bar_chart(df.groupby("Category")["Amount"].sum())
    else:
        st.info("খরচ যোগ করুন, তাহলে বিশ্লেষণ দেখা যাবে।")

    st.markdown("---")
    current_value = float(st.session_state["monthly_budget"])
    budget = st.number_input("🎯 মাসিক বাজেট (₹)", value=current_value, step=500.0, format="%.2f")
    if st.button("বাজেট সেভ করুন"):
        save_budget(budget)
        st.session_state["monthly_budget"] = budget
        st.success("✅ বাজেট সেট করা হয়েছে!")

# ============================
# TAB 2 — ADD EXPENSE
# ============================
with tab2:
    st.subheader("➕ নতুন খরচ যোগ করুন")
    with st.form("add_form", clear_on_submit=True):
        date = st.date_input("তারিখ", datetime.date.today())
        cat = st.selectbox("ক্যাটাগরি", CATEGORY_OPTIONS)
        desc = st.text_input("বিবরণ")
        amt = st.number_input("পরিমাণ (₹)", min_value=0.0, step=10.0)
        submitted = st.form_submit_button("✅ খরচ যোগ করুন")
        if submitted and amt > 0:
            if detect_fraud(desc):
                st.warning("🚨 সতর্কতা: এই খরচে সন্দেহজনক শব্দ পাওয়া গেছে!")
            new = pd.DataFrame([[date, cat, desc, amt]], columns=["Date", "Category", "Description", "Amount"])
            new["Date"] = pd.to_datetime(new["Date"])
            df = pd.concat([df, new], ignore_index=True)
            save_data(df)
            st.session_state["expense_df"] = df
            st.success("খরচ যোগ করা হয়েছে!")

# ============================
# TAB 3 — AI ASSISTANT
# ============================
with tab3:
    st.subheader("🤖 FinGuard AI সহায়ক")
    q = st.text_area("তোমার প্রশ্ন লিখো...", placeholder="এই মাসে কোথায় বেশি খরচ করেছি?")
    if st.button("উত্তর দেখাও 🚀"):
        st.markdown(ask_ai(model, q, df))

# ============================
# TAB 4 — ABOUT
# ============================
with tab4:
    st.markdown("""
### ℹ️ FinGuard - Advanced Secure Edition  
FinGuard এখন আরও শক্তিশালী ও সুরক্ষিত।

**🔐 নতুন ফিচারসমূহ:**  
- AES এনক্রিপশন দ্বারা ডেটা সুরক্ষা  
- ইউজার লগইন সিস্টেম  
- Fraud Detection সিস্টেম  

**📘 ডেটা প্রাইভেসি:**  
FinGuard আপনার ডেটা সুরক্ষিত রাখে। সব তথ্য লোকাল JSON ফাইল-এ সংরক্ষণ হয়, ক্লাউডে পাঠানো হয় না।  
ভবিষ্যৎ ভার্সনে উন্নত AI অ্যানালিটিক্স ও ব্যাংক-লেভেল এনক্রিপশন যুক্ত করা হবে।

👨‍💻 তৈরি করেছেন: **Zahid Hasan**  
🏆 ICT Innovation Award 2025 Submission
""")
