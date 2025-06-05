import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import os, json

GOOGLE_SHEET_NAME = "mochi-sheet"
WORKSHEET_NAME = "Sheet1"
# SERVICE_ACCOUNT_FILE = os.environ["google_service_account.json"]


# Google sheets connect
@st.cache_resource
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Load JSON from secrets
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    return client.open(GOOGLE_SHEET_NAME).worksheet(WORKSHEET_NAME)

sheet = get_sheet()
records = sheet.get_all_records()
df = pd.DataFrame(records)

# Mood logging
st.header("🎫 Label the Next Ticket")

unlabeled_df = df[df["Mood"] == ""]
next_ticket = unlabeled_df.iloc[0]
ticket_index = unlabeled_df.index[0] + 2

st.markdown(f"**ID:** {next_ticket['ID']}")
st.markdown(f"**Timestamp:** {next_ticket['Timestamp']}")
st.markdown(f"**Content:** {next_ticket['Content']}")

mood = st.selectbox("Select mood (required)", ["😊 Happy", "😠 Frustrated", "😕 Confused", "🎉 Joyful"])
note = st.text_input("Optional note")

if st.button("Submit"):
    sheet.update(f"D{ticket_index}", [[mood]])
    sheet.update(f"E{ticket_index}", [[note]])
    st.success("Successfully labeled ticket :)")
    st.rerun()

# Visualizations
st.header("📊 Mood Overview (Today)")

df["Timestamp"] = pd.to_datetime(df["Timestamp"])
today_df = df[df["Timestamp"].dt.date == date.today()]
today_df = today_df[today_df["Mood"] != ""]

if today_df.empty:
    st.info("No moods have been logged today.")
else:
    mood_counts = today_df["Mood"].value_counts().reset_index()
    mood_counts.columns = ["Mood", "Count"]

    fig = px.bar(
        mood_counts,
        x="Mood",
        y="Count",
        text="Count",
        title=f"Mood Count for {date.today().isoformat()}",
    )
    st.plotly_chart(fig)

# Display current ticket DB
with st.expander("📄 Show Full Sheet"):
    st.dataframe(df, use_container_width=True)
