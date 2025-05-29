import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("📦 Inventory Management System")

uploaded_file = st.file_uploader("📤 Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Ensure 'REMARKS' and 'confirmed' columns exist
    if 'REMARKS' not in df.columns:
        df['REMARKS'] = ""
    if 'confirmed' not in df.columns:
        df['confirmed'] = ""

    st.subheader("🔍 Search / Check Machine")
    search_col = st.selectbox("Search by column", df.columns[df.columns != 'confirmed'])
    search_val = st.text_input("Enter search value")

    matched_rows = df[df[search_col].astype(str).str.contains(search_val, case=False, na=False)]

    if not matched_rows.empty:
        st.success(f"✅ Found {len(matched_rows)} matching row(s).")
        st.subheader("ℹ️ Details of Found Items")
        st.dataframe(matched_rows, use_container_width=True)

        if st.button("✔️ Confirm These Entries"):
            df.loc[matched_rows.index, 'REMARKS'] = "Confirmed"
            df.loc[matched_rows.index, 'confirmed'] = "Y"
            st.success("✅ Entries marked as confirmed.")
    else:
        st.warning("🔎 No match found. This seems like a new machine.")

        st.subheader("➕ Add New Machine Info")
        new_row = {}
        cols = st.columns(len(df.columns) - 2)  # Exclude 'REMARKS' and 'confirmed'

        for i, col in enumerate(df.columns):
            if col not in ['REMARKS', 'confirmed']:
                new_row[col] = cols[i % len(cols)].text_input(f"{col}", key=col)

        if st.button("➕ Add New Machine"):
            new_row["REMARKS"] = "New entry added"
            new_row["confirmed"] = "B"
            df.loc[len(df)] = new_row
            st.success("✅ New machine added with 'B' confirmation.")

    # --- Download Updated Excel ---
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "📥 Download Updated Excel",
        buffer,
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
