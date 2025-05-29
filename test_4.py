import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="Inventory Manager", layout="wide")
st.title("📦 Inventory Management Web App")

# Upload Excel
uploaded_file = st.file_uploader("Upload your inventory Excel file", type=["xlsx"])

if uploaded_file:
    original_filename = os.path.splitext(uploaded_file.name)[0]
    df = pd.read_excel(uploaded_file)
    df = df.fillna("")

    st.subheader("🔍 Search or Add Machine")
    search_column = st.selectbox("Select column to search", df.columns)
    search_value = st.text_input("Enter value to search")

    matched_indices = df[df[search_column].astype(str).str.contains(search_value, case=False)].index.tolist()

    # Add new entry if no match
    if search_value and not matched_indices:
        st.warning("No match found. This appears to be a new entry.")
        st.subheader("➕ Add New Machine Details")

        new_data = {}
        for col in df.columns:
            new_data[col] = st.text_input(f"{col}", "")

        if st.button("Add New Machine Entry"):
            new_data["REMARKS"] = "New entry added"
            df.loc[len(df)] = new_data
            matched_indices.append(len(df) - 1)
            st.success("✅ New machine added.")

    # Style rows (green for matched, blue for new)
    def apply_color(row):
        if row.name in matched_indices:
            if row.get("REMARKS", "") == "New entry added":
                return ['background-color: lightblue'] * len(row)
            else:
                return ['background-color: lightgreen'] * len(row)
        return [''] * len(row)

    st.subheader("📋 Inventory Table")
    st.dataframe(df.style.apply(apply_color, axis=1), use_container_width=True)

    # Show non-highlighted rows
    st.subheader("👀 View Non-highlighted Machines")
    non_highlighted_df = df.drop(index=matched_indices)
    st.dataframe(non_highlighted_df, use_container_width=True)

    # Save Excel with colors
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Inventory')
    workbook = writer.book
    worksheet = writer.sheets['Inventory']

    # Apply colors in Excel
    green_format = workbook.add_format({'bg_color': '#C6EFCE'})
    blue_format = workbook.add_format({'bg_color': '#ADD8E6'})

    for i, row in df.iterrows():
        fmt = None
        if i in matched_indices:
            if row.get("REMARKS", "") == "New entry added":
                fmt = blue_format
            else:
                fmt = green_format
        if fmt:
            worksheet.set_row(i + 1, None, fmt)  # +1 to skip header

    writer.close()
    output.seek(0)

    # Download button
    final_filename = f"FINAL {original_filename}.xlsx"
    st.download_button(
        label="💾 Download FINAL Excel Sheet",
        data=output,
        file_name=final_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
