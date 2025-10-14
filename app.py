import time
import streamlit as st
import pandas as pd
import datetime
import json
import os
import hashlib
from cryptography.fernet import Fernet
import google.generativeai as genai
import plotly.express as px

# ============================
# 🚀 PAGE CONFIGURATION
# ============================
st.set_page_config(
    page_title="💰 FinGuard Ultra Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# 💫 SAFE SPLASH SCREEN
# ============================
if "splash_done" not in st.session_state:
    splash_html = """
    <style>
    @keyframes fadeIn {
        0% {opacity: 0; transform: scale(0.95);}
        100% {opacity: 1; transform: scale(1);}
    }
    @keyframes pulse {
        from { transform: scale(1); color: #1E3A8A; }
        to { transform: scale(1.15); color: #2563EB; }
    }
    .splash {
        text-align: center;
        background-color: white;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: black;
        animation: fadeIn 2s ease-in-out;
        font-family: 'Poppins', sans-serif;
    }
    .splash .shield {
        font-size: 85px;
        animation: pulse 2.2s infinite alternate;
    }
    .splash h1 {
        font-size: 3em;
        font-weight: 700;
        margin: 8px 0;
    }
    .splash p {
        font-size: 1.2em;
        color: #555;
        margin-top: 10px;
    }
    </style>
    <div class="splash">
        <div class="shield">🛡️</div>
        <h1>FinGuard</h1>
        <p>AI Finance Guardian is Loading...</p>
    </div>
    """
    st.markdown(splash_html, unsafe_allow_html=True)
    time.sleep(3)
    st.session_state["splash_done"] = True
    st.rerun()
    st.markdown("""
<style>
.stApp {
    background-color: #FFFFFF;  /* Pure white background */
}

[data-testid="stSidebar"] {
    background-color: #FAFAFA;  /* Light sidebar for harmony */
}

h1, h2, h3, label, p, span, div, button, input, textarea {
    color: #111111 !important;   /* Deep black text */
}

.stTabs [data-baseweb="tab"] {
    color: #111111 !important;   /* Dark tab labels */
    font-weight: 600;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #000000 !important;
}

.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #FFD700 !important; /* Gold underline for active tab */
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ----------- BASE BACKGROUND ----------- */
.stApp {
    background-color: #FFFFFF !important; /* Pure white background */
}

/* ----------- SIDEBAR ----------- */
[data-testid="stSidebar"] {
    background-color: #FAFAFA !important; /* Light sidebar */
}

/* ----------- GLOBAL TEXT COLOR ----------- */
html, body, [class*="st-"], p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: #1E1E1E !important; /* Deep neutral black */
    font-weight: 500;
}

/* ----------- TAB LABELS ----------- */
.stTabs [data-baseweb="tab"] {
    color: #1E1E1E !important;
    font-weight: 600;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #000000 !important;
}
.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #FFD700 !important; /* Gold underline for active tab */
}

/* ----------- METRICS ----------- */
.stMetric {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #111111 !important;
}

/* ----------- BUTTONS ----------- */
.stButton>button {
    background-color: #FFFFFF !important;
    color: #1E3A8A !important;
    border: 1px solid #E0E0E0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    background-color: #F9FAFB !important;
    transform: scale(1.03);
}

/* ----------- CHART & CARD BG ----------- */
.block-container {
    background-color: #FFFFFF !important;
}

/* ----------- TITLE ----------- */
h1.title {
    text-align: center;
    font-size: 2.8em;
    font-weight: 700;
    color: #1E3A8A !important; /* Deep Blue Title */
}

p.subtext {
    text-align: center;
    color: #4B5563 !important;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

/* Final visibility override */
html, body, [class*="st-"], p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: #111111 !important;
}
# ============================
# 🎨 CUSTOM UI STYLE
# ============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #F0F2F6; }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease-in-out;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 8px rgba(0,0,0,0.1);
    }
    h1.title {
        text-align: center; font-size: 2.8em;
        font-weight: 700; color: #1E3A8A;
    }
    p.subtext { text-align: center; color: #4B5563; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ----------- BASE BACKGROUND ----------- */
.stApp {
    background-color: #FFFFFF !important; /* Pure white background */
}

/* ----------- SIDEBAR ----------- */
[data-testid="stSidebar"] {
    background-color: #FAFAFA !important; /* Light sidebar */
}

/* ----------- GLOBAL TEXT COLOR ----------- */
html, body, [class*="st-"], p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: #1E1E1E !important; /* Deep neutral black */
    font-weight: 500;
}

/* ----------- TAB LABELS ----------- */
.stTabs [data-baseweb="tab"] {
    color: #1E1E1E !important;
    font-weight: 600;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #000000 !important;
}
.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #FFD700 !important; /* Gold underline for active tab */
}

/* ----------- METRICS ----------- */
.stMetric {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #111111 !important;
}

/* ----------- BUTTONS ----------- */
.stButton>button {
    background-color: #FFFFFF !important;
    color: #1E3A8A !important;
    border: 1px solid #E0E0E0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    background-color: #F9FAFB !important;
    transform: scale(1.03);
}

/* ----------- CHART & CARD BG ----------- */
.block-container {
    background-color: #FFFFFF !important;
}

/* ----------- TITLE ----------- */
h1.title {
    text-align: center;
    font-size: 2.8em;
    font-weight: 700;
    color: #1E3A8A !important; /* Deep Blue Title */
}

p.subtext {
    text-align: center;
    color: #4B5563 !important;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>💰 FinGuard Ultra Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Your Advanced AI-Powered Financial Guardian</p>", unsafe_allow_html=True)

# ============================
# 🔐 ENCRYPTION & SECURITY
# ============================
KEY_FILE = "secret.key"
DATA_FILE = "expenses_encrypted.json"
BUDGET_FILE = "budget_data.json"
USER_FILE = "user_credentials.json"

@st.cache_resource
def get_fernet_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f: f.write(key)
    else:
        with open(KEY_FILE, "rb") as f: key = f.read()
    return key

fernet = Fernet(get_fernet_key())

def encrypt_data(data): return fernet.encrypt(json.dumps(data).encode()).decode()
def decrypt_data(data):
    try: return json.loads(fernet.decrypt(data.encode()).decode())
    except: return []

def hash_password(pwd, salt=None):
    if salt is None: salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt.encode(), 100000).hex()
    return f"{salt}${h}"

def verify_password(stored, provided):
    try:
        s, h = stored.split('$')
        return h == hash_password(provided, s).split('$')[1]
    except: return False

# ============================
# USER AUTH
# ============================
def register_user(u, p):
    if os.path.exists(USER_FILE):
        st.error("A user already exists. Only one supported."); return
    with open(USER_FILE, "w") as f:
        json.dump({"username": u, "password": hash_password(p)}, f)
    st.success("✅ Account created! Please login.")

def authenticate_user(u, p):
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f: data = json.load(f)
        if data["username"] == u and verify_password(data["password"], p): return True
    return False

# ============================
# DATA MANAGEMENT
# ============================
CATEGORY_OPTIONS = sorted([
    "🍕 Food","🚗 Transport","🏠 Rent","💡 Utilities","🎬 Entertainment",
    "🛍️ Shopping","🎓 Education","💊 Health","💼 Work","✈️ Travel","💸 Miscellaneous"
])

def load_data():
    if not os.path.exists(DATA_FILE): return pd.DataFrame(columns=["Date","Category","Description","Amount"])
    with open(DATA_FILE,"r") as f: enc=f.read().strip()
    if not enc: return pd.DataFrame(columns=["Date","Category","Description","Amount"])
    df=pd.DataFrame(decrypt_data(enc))
    if not df.empty: df["Date"]=pd.to_datetime(df["Date"])
    return df

def save_data(df):
    dfc=df.copy(); dfc["Date"]=dfc["Date"].astype(str)
    with open(DATA_FILE,"w") as f: f.write(encrypt_data(dfc.to_dict("records")))

def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE,"r") as f: return json.load(f).get("monthly_budget",0.0)
    return 0.0
def save_budget(b): 
    with open(BUDGET_FILE,"w") as f: json.dump({"monthly_budget":b},f,indent=4)

# ============================
# FRAUD DETECTION
# ============================
def detect_fraud(desc, amt):
    risky=["lottery","reward","gift","refund","otp","offer","bonus","winner"]
    s=sum(1 for w in risky if w in desc.lower())
    if amt>50000: s+=2
    if amt<10: s+=1
    risk=s/(len(risky)+3)
    if risk>0.3: return True, f"High risk ({risk:.0%})"
    if risk>0.1: return True, f"Medium risk ({risk:.0%})"
    return False,"Low risk"

# ============================
# GEMINI AI
# ============================
@st.cache_resource
def setup_gemini():
    try:
        api=st.secrets.get("GEMINI_API_KEY")
        if not api:
            st.sidebar.warning("🤖 Offline AI Mode", icon="⚠️")
            return None
        genai.configure(api_key=api)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.sidebar.error(f"Gemini Error: {e}"); return None

def get_ai_response(model,q,df,b):
    if df.empty: return "⚠️ Add some expenses first!"
    df['Date']=pd.to_datetime(df['Date'])
    total=df['Amount'].sum()
    month=df[df['Date'].dt.month==datetime.date.today().month]['Amount'].sum()
    summ=df.groupby('Category')['Amount'].sum().to_dict()
    if model:
        try:
            p=f"""You are FinGuard AI. Total ₹{total:,.2f}, Monthly ₹{month:,.2f}, Budget ₹{b:,.2f}.
            Categories: {json.dumps(summ)}. Question: {q}"""
            return model.generate_content(p).text
        except: pass
    top=max(summ,key=summ.get)
    return f"🤖 Offline: You spent ₹{total:,.2f}. Most in **{top}**. Save more next week! 💡"

# ============================
# SESSION STATE
# ============================
if "logged_in" not in st.session_state: st.session_state["logged_in"]=False
if "expense_df" not in st.session_state: st.session_state["expense_df"]=load_data()
if "monthly_budget" not in st.session_state: st.session_state["monthly_budget"]=load_budget()
if "ai_chat" not in st.session_state: st.session_state["ai_chat"]=[]

# ============================
# LOGIN PAGE
# ============================
def render_login():
    st.markdown("### 🔐 Secure Access")
    opt="Register" if not os.path.exists(USER_FILE) else "Login"
    sel=st.radio("Select",["Login","Register"],index=["Login","Register"].index(opt))
    with st.form("auth"):
        u=st.text_input("Username"); p=st.text_input("Password",type="password")
        if sel=="Register":
            if st.form_submit_button("Create Account"): register_user(u,p)
        else:
            if st.form_submit_button("Login"):
                if authenticate_user(u,p): st.session_state["logged_in"]=True; st.success("✅ Login OK!"); st.rerun()
                else: st.error("❌ Invalid credentials")
    st.stop()

# ============================
# MAIN APP
# ============================
if not st.session_state["logged_in"]: render_login()
gemini_model=setup_gemini(); df=st.session_state["expense_df"]

with st.sidebar:
    st.header("⚙️ Settings")
    new_b=st.number_input("🎯 Monthly Budget (₹)", value=st.session_state["monthly_budget"], step=1000.0)
    if st.button("💾 Save Budget"):
        save_budget(new_b); st.session_state["monthly_budget"]=new_b; st.success("Saved!")
    if st.button("🔐 Logout"): st.session_state["logged_in"]=False; st.rerun()

tab1,tab2,tab3,tab4,tab5=st.tabs(["📊 Dashboard","➕ Add Expense","🗂️ Manage Data","🤖 AI Assistant","ℹ️ About"])

with tab1:
    st.subheader("📈 Financial Dashboard")
    if df.empty: st.info("No data yet.")
    else:
        total=df["Amount"].sum(); month_start=datetime.date.today().replace(day=1)
        month_exp=df[df["Date"]>=pd.Timestamp(month_start)]["Amount"].sum()
        b=st.session_state["monthly_budget"]; rem=b-month_exp
        c1,c2,c3=st.columns(3)
        c1.metric("💰 Total",f"₹{total:,.2f}")
        c2.metric("💳 This Month",f"₹{month_exp:,.2f}")
        c3.metric("🎯 Remaining",f"₹{rem:,.2f}")
        if b>0: st.progress(min(month_exp/b,1.0))
        st.markdown("---")
        c1,c2=st.columns(2)
        with c1:
            fig=px.pie(df,names='Category',values='Amount',title='Spending by Category',hole=0.3)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            daily=df.groupby(df['Date'].dt.date)['Amount'].sum().reset_index()
            fig2=px.line(daily,x='Date',y='Amount',title='Daily Trend',markers=True)
            st.plotly_chart(fig2,use_container_width=True)

with tab2:
    st.subheader("➕ Add Expense")
    with st.form("add",clear_on_submit=True):
        d=st.date_input("🗓️ Date",datetime.date.today())
        c=st.selectbox("🗂️ Category",CATEGORY_OPTIONS)
        desc=st.text_input("✍️ Description")
        a=st.number_input("💵 Amount (₹)",min_value=0.0,step=10.0)
        if st.form_submit_button("✅ Add"):
            if a<=0: st.warning("Invalid amount.")
            else:
                f,msg=detect_fraud(desc,a)
                if f: st.warning(f"🚨 Suspicious: {msg}")
                new=pd.DataFrame([[d,c,desc,a]],columns=["Date","Category","Description","Amount"])
                df=pd.concat([df,new],ignore_index=True)
                st.session_state["expense_df"]=df; save_data(df)
                st.success("Expense added!")

with tab3:
    st.subheader("🗂️ Manage Data")
    if df.empty: st.info("No data yet.")
    else:
        edited=st.data_editor(df.sort_values("Date",ascending=False),num_rows="dynamic",use_container_width=True)
        if st.button("💾 Save Changes"):
            edited['Date']=pd.to_datetime(edited['Date'])
            st.session_state['expense_df']=edited; save_data(edited); st.success("Updated!"); st.rerun()

with tab4:
    st.subheader("🤖 FinGuard AI Assistant")
    for msg in st.session_state.ai_chat:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    q=st.chat_input("Ask something about your expenses...")
    if q:
        st.session_state.ai_chat.append({"role":"user","content":q})
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                r=get_ai_response(gemini_model,q,df,st.session_state["monthly_budget"])
                st.markdown(r)
        st.session_state.ai_chat.append({"role":"assistant","content":r})

with tab5:
    st.markdown("""
    ### ℹ️ About FinGuard Ultra Pro
    Secure, intelligent & elegant AI finance tracker.

    🔐 Encrypted Data + Hashed Login  
    📊 Smart Dashboard with Plotly  
    🤖 Gemini / Offline AI  
    🚨 Fraud Detection System  

    👨‍💻 Developer: **Zahid Hasan**
    """)
