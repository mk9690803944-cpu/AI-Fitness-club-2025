import streamlit as st
import pandas as pd
import os
import uuid
from io import BytesIO

st.title("Welcome to 🏋️‍♂️ AI Fitness Club 2025")
st.write("Get fit with us!")

file = "members.csv"

# 👉 YOUR UPI ID (CHANGE THIS)
UPI_ID = "paytmqr6cljoj@ptys"

plans = ["Monthly", "Quarterly", "Half yearly", "Yearly"]

regular_charges = {
    "Monthly": 1000,
    "Quarterly": 2700,
    "Half yearly": 4000,
    "Yearly": 6000
}

pt_charges = {
    "Monthly": 4900,
    "Quarterly": 12900,
    "Half yearly": 24000,
    "Yearly": 42000
}

# user input
name = st.text_input("Enter your name")
age = st.number_input("Enter your age", min_value=10, max_value=80)
Plan = st.selectbox("Select plan", plans)
pt = st.checkbox("Add Personal Training (PT)")

# calculate total
if pt:
    total = regular_charges[Plan] + pt_charges[Plan]
else:
    total = regular_charges[Plan]

st.write(f"🧾 Total Charges: ₹ {total}")

# 💳 PAYMENT SECTION
st.subheader("💳 Pay via UPI")

# create UPI payment link
upi_link = f"upi://pay?pa={UPI_ID}&pn=FitnessClub&am={total}&cu=INR"

st.write(f"👉 Pay to UPI ID: **{UPI_ID}**")

st.markdown(f"[📲 Click here to pay via UPI]({upi_link})")


st.info("After payment, click confirm below")

payment_done = st.checkbox("I have completed the payment")

# register
if st.button("Register"):
    if name == "":
        st.warning("Please enter name")
    elif not payment_done:
        st.error("Please complete payment first")
    else:
        pt_selected = "yes" if pt else "no"

        token = str(uuid.uuid4())[:8]

        new_data = pd.DataFrame(
            [[name, age, Plan, pt_selected, total, UPI_ID, token]],
            columns=["Name", "Age", "Plan", "PT", "Total Charges", "UPI", "Token"]
        )

        if os.path.exists(file):
            new_data.to_csv(file, mode='a', header=False, index=False)
        else:
            new_data.to_csv(file, index=False)

        st.success(f"✅ {name} Registered successfully!")
        st.success(f"🎟️ Your Token ID: {token}")

# show data
if os.path.exists(file):
    df = pd.read_csv(file)
    st.subheader("💰 Membership List")
    st.dataframe(df)
else:
    st.info("No members yet")
