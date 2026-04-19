
             



    import streamlit as st
import pandas as pd
import os

st.title("Welcome to 🏋️‍♂️ AI Fitness Club 2025")
st.write("get fit with us !")

file = "members.csv"

#plans and charges
plans = ["Monthly","quarterly","Half yearly","Yearly"]

regular_charges = {
     "Monthly":1000,
     "Quarterly":2700,
     "Half yearly":4000,
     "Yearly":6000
}

pt_charges = {
     "monthly":4900,
     "Quarterly":12900,
     "Half yearly":24000,
     "Yearly":42000
}
    


# user input form
name = st.text_input("Enter your name")
age = st.number_input("Enter your age", min_value=10, max_value=80)
Plan = st.selectbox("select plan", plans)
pt = st.checkbox("Add Personal Training (PT)")


#show selected charges 
if plan:
     st.write(f"💰 Regular charges: ₹ {regular_charges[Plan]}")
if pt:
    st.write(f"🏋️‍♂️ PT Charges: ₹ {pt_charges[Plan]}")
        total = regular_charges[Plan]+ pt_charges[Plan]
else:
     total = regular_charges[Plan]

     st.write(f"🧾Total Charges: ₹{total}")



# save data 
if st.button("Register"):
    if name =="":
       st.warning("please enter name")
    else:
         pt_selected = "yes" if pt else "no"

         new data = pd.DataFrame([[name,age,Plan,pt_selected,total]],
                                 columns=["Name","Age","Plan","PT,"Total charges"]]
                                                                    )

    #save file
    if os.path.exists(file):
        new_data.to_csv(file,mode='a',header=False, index=False)
    else:
        new_data.to_csv(file, index=False)
    st.success(f"✅ {name} Registered successfully!")

    
    # show data
    if os.path.exists(file):
    df = pd.read_csv(file)
    st.subheader("💰Membership List")
    st.dataframe(df)
    else:
        st.info("No members yet")
