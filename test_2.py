import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- Setup Google Sheets access ---
def get_sheet_data(sheet_url, creds_path):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

# --- Streamlit App ---
st.title("📊 Google Sheets Viewer & Editor")

# Input form
sheet_url = r"https://docs.google.com/spreadsheets/d/1r2PdQK-_N1PHf4YaJKez5DtHhRH7W_4-8m85JQ_-ARU/edit"
creds_path = r"C:\Users\MAINTENANCE\Downloads\client_secret_297568253721-l65cjuolslg8f34l7u19iacuqkpcgh7t.apps.googleusercontent.com (1).json"

if sheet_url and creds_path:
    try:
        df, sheet = get_sheet_data(sheet_url, creds_path)
        st.success("Sheet loaded successfully!")
        st.dataframe(df)

        # Optional: Add a row
        with st.form("Add new row"):
            new_data = {}
            for col in df.columns:
                new_data[col] = st.text_input(f"{col}")
            submitted = st.form_submit_button("Add Row")
            if submitted:
                sheet.append_row(list(new_data.values()))
                st.success("Row added!")

    except Exception as e:
        st.error(f"Error: {e}")
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- Setup Google Sheets access ---
def get_sheet_data(sheet_url, creds_path):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

# --- Streamlit App ---
st.title("📊 Google Sheets Viewer & Editor")

# Input form
sheet_url = st.text_input("Google Sheet URL")
creds_path = st.text_input("Path to credentials JSON file", type="password")

if sheet_url and creds_path:
    try:
        df, sheet = get_sheet_data(sheet_url, creds_path)
        st.success("Sheet loaded successfully!")
        st.dataframe(df)

        # Optional: Add a row
        with st.form("Add new row"):
            new_data = {}
            for col in df.columns:
                new_data[col] = st.text_input(f"{col}")
            submitted = st.form_submit_button("Add Row")
            if submitted:
                sheet.append_row(list(new_data.values()))
                st.success("Row added!")

    except Exception as e:
        st.error(f"Error: {e}")
