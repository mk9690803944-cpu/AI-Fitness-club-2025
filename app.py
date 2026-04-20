import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Fitness club 2025")

# ---------------- LOGIN SYSTEM ----------------
st.sidebar.title("🔐 Admin Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if username == "admin" and password == "1234":
    st.sidebar.success("Login Successful")
    logged_in = True
else:
    logged_in = False
    st.sidebar.warning("Enter Admin Credentials")

# ---------------- FILE ----------------
def load_data():
    if not os.path.exists(file):
        return pd.DataFrame()

    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error("Data file corrupted. Resetting...")
        os.remove(file)
        return pd.DataFrame()


# ---------------- PLANS ----------------
plans = {
    "Monthly": 30,
    "Quarterly": 90,
    "Half Yearly": 180,
    "Yearly": 365
}

charges = {
    "Monthly": 1000,
    "Quarterly": 2700,
    "Half Yearly": 4000,
    "Yearly": 6000
}

pt_charges = {
    "Monthly": 4900,
    "Quarterly": 12900,
    "Half Yearly": 24900,
    "Yearly": 44900
}

# ---------------- MENU ----------------
menu = st.selectbox("Select Option", ["Register Member", "Admin Dashboard"])

# ================= REGISTER =================
if menu == "Register Member":
    st.title("🏋️ Register New Member")

    with st.form("form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        plan = st.selectbox("Plan", list(plans.keys()))
        pt = st.checkbox("Add Personal Training")
        payment_status = st.selectbox("Payment Status", ["Paid", "Pending"])
        
        submit = st.form_submit_button("Register")

    if submit:
        if name == "" or phone == "":
            st.error("Fill all details")
        else:
            start_date = datetime.today()
            expiry_date = start_date + timedelta(days=plans[plan])

            amount = charges[plan]
            if pt:
                amount += pt_charges[plan]

            data = {
                "Name": name,
                "Phone": phone,
                "Plan": plan,
                "PT": pt,
                "Amount": amount,
                "Payment": payment_status,
                "Start Date": start_date.strftime("%Y-%m-%d"),
                "Expiry Date": expiry_date.strftime("%Y-%m-%d")
            }

            df = pd.DataFrame([data])

            if os.path.exists(file):
                df.to_csv(file, mode='a', header=False, index=False)
            else:
                df.to_csv(file, index=False)

            st.success("Member Registered ✅")

            # WhatsApp Message
            msg = f"""
Hello {name},
Welcome to AI Fitnes club 2025 💪

Plan: {plan}
Amount: ₹{amount}
Start Date: {start_date.date()}
Expiry Date: {expiry_date.date()}

Thank you!
"""

            wa_link = f"https://wa.me/91{phone}?text={msg.replace(' ', '%20')}"
            st.markdown(f"[Send WhatsApp Confirmation]({wa_link})")

# ================= ADMIN DASHBOARD =================
# ---------------- LOAD FUNCTION (KEEP AT TOP OF FILE) ----------------

if menu == "Admin Dashboard":
    if not logged_in:
        st.error("Login required")
    else:
        st.title("📊 Admin Dashboard")

        df = load_data()   # ✅ CALL FUNCTION

        st.subheader("All Members")

        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("No data available")

            # Search
            search = st.text_input("Search by Name or Phone")
            if search:
                result = df[
                    df["Name"].str.contains(search, case=False) |
                    df["Phone"].astype(str).str.contains(search)
                ]
                st.dataframe(result)

            # Expiry Alert
            st.subheader("⚠️ Expiring Soon (Next 5 Days)")

            df["Expiry Date"] = pd.to_datetime(df["Expiry Date"])
            today = datetime.today()

            expiring = df[
                (df["Expiry Date"] - today).dt.days <= 5
            ]

            if not expiring.empty:
                st.dataframe(expiring)

                # WhatsApp Reminder
                for i, row in expiring.iterrows():
                    msg = f"""
Hello {row['Name']},
Your gym membership is expiring on {row['Expiry Date'].date()}.

Please renew soon 💪
"""
                    wa_link = f"https://wa.me/91{row['Phone']}?text={msg.replace(' ', '%20')}"
                    st.markdown(f"[Remind {row['Name']}]({wa_link})")

            else:
                st.success("No memberships expiring soon")

            # Download CSV
            st.download_button(
                "Download Data",
                df.to_csv(index=False),
                "members.csv",
                "text/csv"
            )

        else:
            st.warning("No data found")
