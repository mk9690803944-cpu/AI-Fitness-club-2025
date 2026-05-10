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
            from_="whatsapp:+14155238886",  # Twilio Sandbox Number
            to=f"whatsapp:{to_number}"
        )
    except Exception as e:
        st.error(f"WhatsApp Error: {e}")


# ---------- LOAD DATA ----------
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Contact"] = df["Contact"].astype(str)
        return df
    else:
        return pd.DataFrame(columns=[
            "S.No",
            "Name",
            "Contact",
            "Fees Status",
            "Start Date",
            "Expiry Date",
            "Receipt No",
            "Notified"
        ])


# ---------- SAVE DATA ----------
def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ---------- LOGIN ----------
def login():
    st.title("🏋️ AI Fitness Club 2025 - Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")


# ---------- DASHBOARD ----------
def dashboard():
    df = load_data()

    st.title("🏋️ AI Fitness Club 2025 Dashboard")

    # ---------- ADD MEMBER ----------
    st.subheader("➕ Add New Member")

    with st.form("add_member_form"):
        name = st.text_input("Name")
        mobile = st.text_input("Contact Number")
        fees_status = st.selectbox("Fees Status", ["Paid", "Unpaid"])
        start_date = st.date_input("Start Date")
        expiry_date = st.date_input("Expiry Date")
        receipt_no = st.text_input("Receipt No.")

        submit = st.form_submit_button("Add Member")

        if submit:
            mobile = mobile.strip()

            if mobile == "":
                st.error("Contact number is required.")

            # ---------- DUPLICATE CHECK ----------
            elif mobile in df["Contact"].astype(str).values:
                st.warning("Member already exists.")

            else:
                new_row = {
                    "S.No": len(df) + 1,
                    "Name": name.strip(),
                    "Contact": mobile,
                    "Fees Status": fees_status,
                    "Start Date": start_date,
                    "Expiry Date": expiry_date,
                    "Receipt No": receipt_no.strip(),
                    "Notified": "No"
                }

                df = pd.concat(
                    [df, pd.DataFrame([new_row])],
                    ignore_index=True
                )

                save_data(df)
                st.success("Member Added Successfully.")
                st.rerun()

    # ---------- MEMBERS LIST ----------
    st.subheader("📋 Members List")

    def color_status(val):
        if val == "Paid":
            return "background-color: lightgreen"
        else:
            return "background-color: lightcoral"

    if not df.empty:
        styled_df = df.style.map(color_status, subset=["Fees Status"])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No members available.")

    # ---------- EXPIRY NOTIFICATIONS ----------
    st.subheader("🔔 Expiry Notifications")

    today = datetime.today().date()
    expired_members = []

    for i, row in df.iterrows():
        try:
            expiry = pd.to_datetime(row["Expiry Date"]).date()

            if expiry < today:
                expired_members.append(row)

                # Send WhatsApp only once
                if str(row["Notified"]) == "No":
                    send_whatsapp(
                        row["Contact"],
                        f"Hello {row['Name']}, your gym membership has expired. Please renew."
                    )
                    df.at[i, "Notified"] = "Yes"

        except Exception:
            continue

    save_data(df)

    if expired_members:
        st.warning(f"{len(expired_members)} membership(s) expired.")
        st.dataframe(pd.DataFrame(expired_members), use_container_width=True)
    else:
        st.success("No expired memberships.")

    # ---------- DOWNLOAD BUTTON ----------
    st.download_button(
        label="⬇ Download Data",
        data=df.to_csv(index=False),
        file_name="members.csv",
        mime="text/csv"
    )


# ---------- MAIN ----------
if not st.session_state.logged_in:
    login()
else:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        
    dashboard()