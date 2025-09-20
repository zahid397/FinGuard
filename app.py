import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="FinGuard", page_icon="💰")

# Title
st.title("💰 FinGuard – AI-powered Finance Tracker")

# Intro
st.write("Welcome to **FinGuard** – your smart expense tracker with AI-powered saving tips!")

# Sample data
data = {
    "Category": ["Food", "Transport", "Shopping", "Bills", "Others"],
    "Amount": [120, 60, 90, 150, 40]
}
df = pd.DataFrame(data)

# Show table
st.subheader("📊 Expense Summary")
st.table(df)

# Show chart
fig, ax = plt.subplots()
ax.pie(df["Amount"], labels=df["Category"], autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)

# AI saving tip (static demo)
st.subheader("🤖 Smart Saving Tip")
st.success("Try to reduce Shopping expenses by 10% this month to save more!")
