import streamlit as st
import pandas as pd
from io import BytesIO

# --- App Title ---
st.title("📦 Inventory Management System")

# --- Upload Excel File ---
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("🔍 Search / Check Machine")
    search_col = st.selectbox("Search by column", df.columns)
    search_val = st.text_input("Enter search value")

    # Track whether match is found
    matched_rows = df[df[search_col].astype(str).str.contains(search_val, case=False, na=False)]

    if not matched_rows.empty:
        st.success(f"✅ Found {len(matched_rows)} matching rows.")

        def highlight_row_green(row):
            if row.name in matched_rows.index:
                return ['background-color: lightgreen'] * len(row)
            return [''] * len(row)

        st.dataframe(df.style.apply(highlight_row_green, axis=1))

    else:
        st.warning("🔎 No match found. This seems like a new machine.")

        # Add new row
        st.subheader("➕ Add New Machine Info")
        new_row = {}
        for col in df.columns:
            new_row[col] = st.text_input(f"{col}", "")

        if st.button("Add New Machine"):
            df.loc[len(df)] = new_row
            df.at[len(df)-1, 'REMARKS'] = "New entry added"
            st.success("✅ New machine added successfully.")

        def highlight_row_blue(row):
            if row.name == len(df) - 1 and row['REMARKS'] == "New entry added":
                return ['background-color: lightblue'] * len(row)
            return [''] * len(row)

        st.dataframe(df.style.apply(highlight_row_blue, axis=1))

        # Download updated Excel
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button("📥 Download Updated Excel", buffer, file_name="updated_inventory.xlsx")

