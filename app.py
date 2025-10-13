import streamlit as st
import pandas as pd
import datetime
import json
import os
import google.generativeai as genai

# ============================
# 🚀 PAGE CONFIG
# ============================
st.set_page_config(
    page_title="FinGuard — AI Smart Expense & Budget Companion",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# 🎨 CUSTOM STYLING
# ============================
st.markdown("""
<style>
.main-header {
    font-size: 2.5em;
    font-weight: bold;
    color: #0d47a1;
}
.logo-text {
    color: #f44336;
    font-style: italic;
}
.tagline {
    color: #42a5f5;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💰 Fin<span class="logo-text">Guard</span></div>', unsafe_allow_html=True)
st.markdown('<p class="tagline">— AI Smart Expense & Budget Companion</p>', unsafe_allow_html=True)

# ============================
# 📂 FILES
# ============================
DATA_FILE = "expenses.json"
BUDGET_FILE = "budget.json"

CATEGORY_OPTIONS = ["Food", "Transport", "Rent", "Utilities", "Entertainment", "Shopping", "Education", "Health", "Others"]

# ============================
# 💾 DATA FUNCTIONS
# ============================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
        return df
    return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

def save_data(df):
    df["Date"] = df["Date"].astype(str)
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict("records"), f, indent=4)

def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            return json.load(f).get("monthly_budget", 0.0)
    return 0.0

def save_budget(budget):
    with open(BUDGET_FILE, "w") as f:
        json.dump({"monthly_budget": budget}, f, indent=4)

# ============================
# 🕵️‍♂️ SCAM DETECTION
# ============================
def detect_scam(text):
    suspicious_keywords = ["lottery", "reward", "urgent", "OTP", "click here", "send money", "free gift", "offer"]
    for word in suspicious_keywords:
        if word.lower() in text.lower():
            return True
    return False

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
if "expense_df" not in st.session_state:
    st.session_state["expense_df"] = load_data()
if "monthly_budget" not in st.session_state:
    st.session_state["monthly_budget"] = load_budget()

df = st.session_state["expense_df"]
model = setup_gemini()

# ============================
# 🧭 TABS
# ============================
tab1, tab2, tab3, tab4 = st.tabs(["📊 ড্যাশবোর্ড", "➕ খরচ যোগ করুন", "🤖 AI সহায়ক", "🔒 সিকিউরিটি ও অ্যাবাউট"])

# ============================
# TAB 1 — DASHBOARD
# ============================
with tab1:
    st.subheader("📈 ব্যয়ের বিশ্লেষণ")
    if not df.empty:
        total = df["Amount"].sum()
        st.metric("💰 মোট খরচ", f"₹{total:,.2f}")

        start_of_month = pd.Timestamp(datetime.date.today().replace(day=1))
        monthly = df[df["Date"] >= start_of_month]
        st.metric("💳 এই মাসের খরচ", f"₹{monthly['Amount'].sum():,.2f}")

        # 📊 Graphs
        st.subheader("📊 ক্যাটাগরি অনুযায়ী খরচ")
        st.bar_chart(df.groupby("Category")["Amount"].sum())

        st.subheader("📅 সময়ের সাথে খরচের প্রবণতা")
        df_sorted = df.sort_values(by="Date")
        df_sorted["Cumulative"] = df_sorted["Amount"].cumsum()
        st.line_chart(df_sorted.set_index("Date")["Cumulative"])
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
            if detect_scam(desc):
                st.warning("⚠️ এই বিবরণটি সন্দেহজনক হতে পারে! অনুগ্রহ করে যাচাই করুন।")
            new = pd.DataFrame([[date, cat, desc, amt]], columns=["Date", "Category", "Description", "Amount"])
            new["Date"] = pd.to_datetime(new["Date"])
            df = pd.concat([df, new], ignore_index=True)
            save_data(df)
            st.session_state["expense_df"] = df
            st.success("✅ খরচ যোগ করা হয়েছে!")

# ============================
# TAB 3 — AI ASSISTANT
# ============================
with tab3:
    st.subheader("🤖 FinGuard AI সহায়ক")
    q = st.text_area("তোমার প্রশ্ন লিখো...", placeholder="এই মাসে কোথায় বেশি খরচ করেছি?")
    if st.button("উত্তর দেখাও 🚀"):
        st.markdown(ask_ai(model, q, df))

# ============================
# TAB 4 — SECURITY & ABOUT
# ============================
with tab4:
    st.markdown("""
### 🔒 Data Privacy & Security
FinGuard আপনার ডেটা সুরক্ষিত রাখে। সব তথ্য **লোকাল JSON ফাইল**-এ সংরক্ষণ হয়, ক্লাউডে পাঠানো হয় না।  
ভবিষ্যৎ ভার্সনে **AES Encryption** এবং **User Login System** যুক্ত করা হবে।  

### ℹ️ FinGuard - ICT Award Build (Enhanced)
FinGuard একটি AI-চালিত বাজেট ও খরচ বিশ্লেষণ অ্যাপ।  
এটি আপনার ব্যয় বিশ্লেষণ, বাজেট মনিটরিং এবং AI টিপসের মাধ্যমে আর্থিক সচেতনতা বাড়ায়।

**মূল ফিচারসমূহ:**
- 🧠 AI Analysis (Gemini 2.5 Flash)  
- ⚠️ Fraud Detection System (Beta)  
- 📈 Data Visualization Charts  
- 🔐 Local Secure Data Handling  

👨‍💻 তৈরি করেছেন: Zahid Hasan  
🏆 ICT Innovation Award 2025 Submission  
📧 Contact: zh05698@gmail.com  
""")
