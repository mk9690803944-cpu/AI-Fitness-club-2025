import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
from twilio.rest import Client
from urllib.parse import quote


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Fitness Club 2025",
    page_icon="🏋️",
    layout="wide"
)


# =========================================================
# SUPABASE CONNECTION
# =========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_PUBLISHABLE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# WHATSAPP FUNCTION
# =========================================================

def send_whatsapp(to_number, message):

    try:

        account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
        auth_token = st.secrets["TWILIO_AUTH_TOKEN"]

        client = Client(
            account_sid,
            auth_token
        )

        client.messages.create(
            body=message,
            from_="whatsapp:+14155238886",
            to=f"whatsapp:{to_number}"
        )

        return True

    except Exception as e:

        st.error(
            f"WhatsApp Error: {e}"
        )

        return False


# =========================================================
# LOAD MEMBERS FROM SUPABASE
# =========================================================

def load_members():

    try:

        response = (
            supabase
            .table("members")
            .select("*")
            .order("id")
            .execute()
        )

        data = response.data

        if not data:

            return pd.DataFrame(
                columns=[
                    "id",
                    "S.No",
                    "Name",
                    "Mobile",
                    "Fees Status",
                    "Start Date",
                    "Expiry Date",
                    "Receipt No",
                    "Notified"
                ]
            )

        return pd.DataFrame(data)

    except Exception as e:

        st.error(
            f"Database Error: {e}"
        )

        return pd.DataFrame()


# =========================================================
# SUPABASE AUTH LOGIN
# =========================================================

def login():

    st.title(
        "🏋️ AI Fitness Club 2025"
    )

    st.subheader(
        "Admin Login"
    )

    email = st.text_input(
        "Email"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        if not email or not password:

            st.error(
                "Please enter email and password."
            )

            return

        try:

            # Supabase Authentication

            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )

            # Save authenticated session

            st.session_state["access_token"] = (
                response.session.access_token
            )

            st.session_state["refresh_token"] = (
                response.session.refresh_token
            )

            st.session_state["user"] = (
                response.user
            )

            st.session_state["logged_in"] = True

            st.success(
                "Login Successful"
            )

            st.rerun()

        except Exception as e:

            st.error(
                "Invalid email or password."
            )

            st.caption(
                f"Login error: {e}"
            )


# =========================================================
# LOGOUT
# =========================================================

def logout():

    try:

        supabase.auth.sign_out()

    except Exception:

        pass

    st.session_state.pop(
        "access_token",
        None
    )

    st.session_state.pop(
        "refresh_token",
        None
    )

    st.session_state.pop(
        "user",
        None
    )

    st.session_state["logged_in"] = False

    st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

def dashboard():

    st.title(
        "🏋️ AI Fitness Club 2025 Dashboard"
    )

    # -----------------------------------------------------
    # CURRENT USER
    # -----------------------------------------------------

    user = st.session_state.get(
        "user"
    )

    if user:

        st.caption(
            f"Logged in as: {user.email}"
        )


    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    df = load_members()


    # =====================================================
    # ADD MEMBER
    # =====================================================

    st.subheader(
        "➕ Add New Member"
    )

    with st.form(
        "member_form"
    ):

        name = st.text_input(
            "Name"
        )

        mobile = st.text_input(
            "Mobile Number",
            placeholder="+91XXXXXXXXXX"
        )

        fees = st.selectbox(
            "Fees Status",
            ["Paid", "Unpaid"]
        )

        start = st.date_input(
            "Start Date"
        )

        expiry = st.date_input(
            "Expiry Date"
        )

        receipt = st.text_input(
            "Receipt Number"
        )

        submit = st.form_submit_button(
            "Add Member",
            use_container_width=True
        )


        # =================================================
        # ADD MEMBER
        # =================================================

        if submit:

            # ---------------------------------------------
            # VALIDATION
            # ---------------------------------------------

            if not name.strip():

                st.error(
                    "Please enter member name."
                )

                st.stop()


            if not mobile.strip():

                st.error(
                    "Please enter mobile number."
                )

                st.stop()


            # ---------------------------------------------
            # DUPLICATE MOBILE CHECK
            # ---------------------------------------------

            try:

                existing = (
                    supabase
                    .table("members")
                    .select("id")
                    .eq(
                        "Mobile",
                        mobile.strip()
                    )
                    .execute()
                )

            except Exception as e:

                st.error(
                    f"Unable to check member: {e}"
                )

                st.stop()


            if existing.data:

                st.error(
                    "❌ Member with this mobile number already exists!"
                )

                st.stop()


            # ---------------------------------------------
            # NEXT SERIAL NUMBER
            # ---------------------------------------------

            if df.empty:

                next_serial = 1

            else:

                try:

                    serial_numbers = pd.to_numeric(
                        df["S.No"],
                        errors="coerce"
                    )

                    maximum = serial_numbers.max()

                    if pd.isna(maximum):

                        next_serial = 1

                    else:

                        next_serial = (
                            int(maximum) + 1
                        )

                except Exception:

                    next_serial = (
                        len(df) + 1
                    )


            # ---------------------------------------------
            # DATES
            # ---------------------------------------------

            start_date_str = (
                start.strftime("%Y-%m-%d")
            )

            expiry_date_str = (
                expiry.strftime("%Y-%m-%d")
            )


            # ---------------------------------------------
            # NEW MEMBER
            # ---------------------------------------------

            new_member = {

                "S.No": next_serial,

                "Name": name.strip(),

                "Mobile": mobile.strip(),

                "Fees Status": fees,

                "Start Date": start_date_str,

                "Expiry Date": expiry_date_str,

                "Receipt No": receipt.strip(),

                "Notified": "No"
            }


            # ---------------------------------------------
            # INSERT INTO SUPABASE
            # ---------------------------------------------

            try:

                supabase \
                    .table("members") \
                    .insert(new_member) \
                    .execute()


                st.success(
                    "✅ Member Added Successfully!"
                )


                # -----------------------------------------
                # WHATSAPP CONFIRMATION
                # -----------------------------------------

                message = f"""
Hello {name},

Welcome to AI Fitness Club 2025 💪

Plan: Monthly
Amount: ₹1000

Start Date: {start_date_str}
Expiry Date: {expiry_date_str}

Receipt No: {receipt}

Thank you!
AI Fitness Club 2025
"""


                encoded_message = quote(
                    message
                )


                wa_link = (
                    f"https://wa.me/"
                    f"{mobile.strip()}"
                    f"?text={encoded_message}"
                )


                st.markdown(
                    f"[📱 Send WhatsApp Confirmation]"
                    f"({wa_link})"
                )


                st.rerun()


            except Exception as e:

                st.error(
                    f"Unable to add member: {e}"
                )


    # =====================================================
    # REFRESH DATA
    # =====================================================

    df = load_members()


    # =====================================================
    # MEMBERS LIST
    # =====================================================

    st.subheader(
        "📋 Members List"
    )


    if not df.empty:

        df["Mobile"] = (
            df["Mobile"]
            .astype(str)
        )


        # ---------------------------------------------
        # STATUS COLOR
        # ---------------------------------------------

        def color_status(value):

            if value == "Paid":

                return (
                    "background-color: lightgreen"
                )

            elif value == "Unpaid":

                return (
                    "background-color: lightcoral"
                )

            return ""


        styled_df = (
            df.style
            .map(
                color_status,
                subset=["Fees Status"]
            )
        )


        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.warning(
            "No members available."
        )


    # =====================================================
    # EXPIRY CHECK
    # =====================================================

    st.subheader(
        "🔔 Expiry Notifications"
    )


    today = datetime.today().date()

    expired_list = []


    if not df.empty:

        for _, row in df.iterrows():

            try:

                expiry_date = (
                    pd.to_datetime(
                        row["Expiry Date"]
                    ).date()
                )


                # -----------------------------------------
                # EXPIRED
                # -----------------------------------------

                if expiry_date < today:

                    expired_list.append(
                        row
                    )


                    # -------------------------------------
                    # SEND ONLY ONCE
                    # -------------------------------------

                    if (
                        str(row["Notified"])
                        == "No"
                    ):

                        message = (
                            f"Hello {row['Name']}, "
                            f"your gym membership has expired. "
                            f"Please renew your membership."
                        )


                        success = send_whatsapp(
                            row["Mobile"],
                            message
                        )


                        if success:

                            (
                                supabase
                                .table("members")
                                .update({
                                    "Notified": "Yes"
                                })
                                .eq(
                                    "id",
                                    int(row["id"])
                                )
                                .execute()
                            )


            except Exception:

                continue


    # =====================================================
    # SHOW EXPIRED MEMBERS
    # =====================================================

    if expired_list:

        st.warning(
            f"⚠️ {len(expired_list)} "
            f"Membership(s) Expired"
        )


        expired_df = pd.DataFrame(
            expired_list
        )


        st.dataframe(
            expired_df,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.success(
            "✅ No expired memberships"
        )


    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    st.subheader(
        "⬇ Download Data"
    )


    current_df = load_members()


    if not current_df.empty:

        csv_data = current_df.to_csv(
            index=False
        )


        st.download_button(

            label="⬇ Download Members CSV",

            data=csv_data,

            file_name="members.csv",

            mime="text/csv",

            use_container_width=True
        )


    # =====================================================
    # LOGOUT
    # =====================================================

    st.divider()


    if st.button(
        "Logout",
        use_container_width=True
    ):

        logout()


# =========================================================
# MAIN
# =========================================================

if "logged_in" not in st.session_state:

    st.session_state["logged_in"] = False


if not st.session_state["logged_in"]:

    login()

else:

    dashboard()
