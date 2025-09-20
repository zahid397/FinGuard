import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # Safe backend for Streamlit
import matplotlib.pyplot as plt

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

# Show chart
fig, ax = plt.subplots()
ax.pie(df["Amount"], labels=df["Category"], autopct="%1.1f%%", startangle=90)
ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular
st.pyplot(fig)

# AI Saving Tip (Static demo tip)
st.subheader("💡 Smart Saving Tip")
st.write("Try reducing your shopping expenses by 20% this month to increase your savings!")
