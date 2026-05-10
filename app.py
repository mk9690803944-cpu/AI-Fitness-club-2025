from ast import Name

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from twilio.rest import Client

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Fitness Club 2025", layout="wide")

ADMIN_USERNAME = "aifitnessclub2025"

ADMIN_PASSWORD = "abcd1234"

DATA_FILE = "members.csv"

# ---------- WHATSAPP FUNCTION ----------
def send_whatsapp(to_number, message):
    try:
        account_sid = "AC80acafb570def28c4b2913904830ecbe"
        auth_token = "3c77e14c384e3bf9855265ec1dd1a785"
        client = Client(account_sid, auth_token)

        client.messages.create(
            body=message,
            from_="whatsapp:+14155238886",  # Twilio Sandbox number
            to=f"whatsapp:{to_number}"
        )
    except Exception as e:
        print("WhatsApp Error:", e)

# ---------- LOAD DATA ----------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "S.No", "Name", "Contact", "Fees Status",
        "Start Date", "Expiry Date", "Receipt No", "Notified"
    ])

# ---------- LOGIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🏋️ AI Fitness Club 2025 - Admin Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

# ---------- DASHBOARD ----------
def dashboard():
    global df

    st.title("🏋️ AI Fitness Club 2025 Dashboard")

    # ---- ADD MEMBER ----
    st.subheader("➕ Add New Member")

    with st.form("form"):
        name = st.text_input("Name")
        mobile = st.text_input("Contact")
        fees = st.selectbox("Fees Status", ["Paid", "Unpaid"])
        start = st.date_input("Start Date")
        expiry = st.date_input("Expiry Date")
        receipt = st.text_input("Receipt No.")

        submit = st.form_submit_button("Add Member")

        if submit:
            new_row = {
                "S.No": len(df) + 1,
                "Name": name,
                "Contact": mobile ,
                "Fees Status": fees,
                "Start Date": start,
                "Expiry Date": expiry,
                "Receipt No": receipt,
                "Notified": "No"
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Member Added")
        # fix mobile no.type
        df = pd.read_csv("members.csv")
        df["Contact"] = df["Contact"].astype(str)

     # ---- DISPLAY ----
    st.subheader("📋 Members List")

    def color_status(val):
        if val == "Paid":
            return "background-color: lightgreen"
        else:
            return "background-color: saffron"

    if not df.empty:
        styled = df.style.applymap(color_status, subset=["Fees Status"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.warning("No data available")

    # ---- EXPIRY CHECK ----
    st.subheader("🔔 Expiry Notifications")

    today = datetime.today().date()
    expired_list = []

    for i, row in df.iterrows():
        try:
            expiry_date = pd.to_datetime(row["Expiry Date"]).date()

            if expiry_date < today:
                expired_list.append(row)

                # SEND WHATSAPP ONLY ONCE
                if row["Notified"] == "No":
                    send_whatsapp(
                        row["Contact"],
                        f"Hello {row['Name']}, your gym membership has expired. Please renew."
                    )
                    df.at[i, "Notified"] = "Yes"

        except:
            continue

    df.to_csv(DATA_FILE, index=False)

    if expired_list:
        st.warning(f"{len(expired_list)} Membership(s) Expired")
        st.dataframe(pd.DataFrame(expired_list))
    else:
        st.success("No expired memberships")

     # ---- DOWNLOAD ----
    st.download_button(
        "⬇ Download Data",
        df.to_csv(index=False),
        "members.csv",
        "text/csv"
    )

 # ---------- MAIN ----------
if not st.session_state.logged_in:
    login()
else:
    if st.sidebar.button("logout"):
        st.session_state.logged_in = False
        st.rerun()

    dashboard()
