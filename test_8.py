import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Inventory Management", layout="wide")

# --- App Title ---
st.title("📦 Inventory Management System")

# --- Upload Excel File ---
uploaded_file = st.file_uploader("📤 Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Ensure REMARKS column exists
    if 'REMARKS' not in df.columns:
        df['REMARKS'] = ""

    st.subheader("🔍 Search / Check Machine")
    search_col = st.selectbox("Search by column", df.columns)
    search_val = st.text_input("Enter search value")

    # Filter for matching rows
    matched_rows = df[df[search_col].astype(str).str.contains(search_val, case=False, na=False)]

    if not matched_rows.empty:
        st.success(f"✅ Found {len(matched_rows)} matching row(s).")

        def highlight_row_green(row):
            if row.name in matched_rows.index:
                return ['background-color: lightgreen'] * len(row)
            return [''] * len(row)

        st.dataframe(df.style.apply(highlight_row_green, axis=1), use_container_width=True)

        if st.button("✔️ Confirm Entry"):
            df.loc[matched_rows.index, 'REMARKS'] = "Confirmed"
            st.success("✅ Entry marked as confirmed.")

    else:
        st.warning("🔎 No match found. This seems like a new machine.")

        # Add new row section
        st.subheader("➕ Add New Machine Info")
        new_row = {}
        cols = st.columns(len(df.columns))  # Spread fields across columns

        for i, col in enumerate(df.columns):
            if col != "REMARKS":  # Skip REMARKS for input
                new_row[col] = cols[i % len(cols)].text_input(f"{col}", key=col)

        if st.button("➕ Add New Machine"):
            new_row["REMARKS"] = "New entry added"
            df.loc[len(df)] = new_row
            st.success("✅ New machine added successfully.")

        def highlight_row_blue(row):
            if row.name == len(df) - 1 and row['REMARKS'] == "New entry added":
                return ['background-color: lightblue'] * len(row)
            return [''] * len(row)

        st.dataframe(df.style.apply(highlight_row_blue, axis=1), use_container_width=True)

    # --- Download updated Excel ---
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "📥 Download Updated Excel",
        buffer,
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
