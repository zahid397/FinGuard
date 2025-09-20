import streamlit as st
import pandas as pd

# Title
st.title("💰 FinGuard - Smart Expense Tracker")

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

# Show bar chart
st.subheader("📈 Expense Distribution")
st.bar_chart(df.set_index("Category"))

# AI Saving Tip (Static demo tip)
st.subheader("💡 Smart Saving Tip")
st.write("Try reducing your shopping expenses by 20% this month to increase your savings!")
