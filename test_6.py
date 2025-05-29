import streamlit as st
import pandas as pd
from io import BytesIO
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

# Color constants
GREEN = "#C6EFCE"
BLUE = "#ADD8E6"
RED = "#FFC7CE"
WHITE = "#FFFFFF"

# Session state storage
if "confirmed_rows" not in st.session_state:
    st.session_state.confirmed_rows = []
if "new_rows" not in st.session_state:
    st.session_state.new_rows = []
if "edited_cells" not in st.session_state:
    st.session_state.edited_cells = set()

st.title("📦 Inventory Management System")

uploaded_file = st.file_uploader("Upload Excel Sheet", type=["xlsx"])

if uploaded_file:
    # Load Excel sheet
    df = pd.read_excel(uploaded_file)

    # ✅ Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

    # ✅ Add CONFIRMED column based on row color
    def is_confirmed(row_idx):
        return "Y" if row_idx in st.session_state.confirmed_rows else "N"

    df["CONFIRMED"] = [is_confirmed(i) for i in range(len(df))]

    # 🔍 Search functionality
    st.subheader("🔍 Search Machine")
    query = st.text_input("Enter Serial Number, Name, etc.")

    if query:
        results = df[df.astype(str).apply(lambda row: query.lower() in row.str.lower().to_string(), axis=1)]
        st.write("### Matching Machines")
        st.dataframe(results, use_container_width=True)
    else:
        st.write("ℹ️ Enter a search term to find a machine.")

    # Display styled dataframe
    st.write("### 🧾 Machine Records")

    def highlight_row(row):
        idx = row.name
        color = WHITE
        if idx in st.session_state.confirmed_rows:
            color = GREEN
        elif idx in st.session_state.new_rows:
            color = BLUE
        return [f"background-color: {color}"] * len(row)

    st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

    # ✅ Confirm/Edit functionality
    st.subheader("✅ Confirm or Edit Machines")
    row_to_confirm = st.number_input("Row number to confirm (0-indexed)", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Confirm"):
        if row_to_confirm not in st.session_state.confirmed_rows:
            st.session_state.confirmed_rows.append(row_to_confirm)
        df.at[row_to_confirm, "CONFIRMED"] = "Y"
        st.success(f"Row {row_to_confirm} confirmed ✅")

    edited_row = st.number_input("Row number to edit (0-indexed)", min_value=0, max_value=len(df)-1, step=1, key="edit_row")
    edit_col = st.selectbox("Column to edit", options=df.columns, key="edit_col")
    new_val = st.text_input("New value", key="edit_val")

    if st.button("Edit"):
        old_val = df.at[edited_row, edit_col]
        if new_val and str(new_val) != str(old_val):
            df.at[edited_row, edit_col] = new_val
            st.session_state.edited_cells.add((edited_row, edit_col))
            st.success(f"Cell [{edited_row}, {edit_col}] updated 🔴")

    # View unconfirmed machines
    st.subheader("📘 View Unconfirmed Machines")
    unconfirmed = df[df["CONFIRMED"] != "Y"]
    st.dataframe(unconfirmed, use_container_width=True)

    # 📤 Save Final Excel with Colors
    def save_final_with_colors(df, original_uploaded_file, confirmed_rows, new_rows, edited_cells):
        wb = openpyxl.load_workbook(original_uploaded_file)
        ws = wb.active

        # Remove unnamed columns in Excel too
        clean_columns = [col for col in df.columns if not col.lower().startswith("unnamed")]
        df = df[clean_columns]

        # Rewrite updated rows to Excel
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
            for c_idx, value in enumerate(row, start=1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)

                # Coloring
                if r_idx == 1:
                    continue  # Skip header row
                row_index = r_idx - 2
                col_name = df.columns[c_idx - 1]

                if row_index in confirmed_rows:
                    cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                elif row_index in new_rows:
                    cell.fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
                if (row_index, col_name) in edited_cells:
                    cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        final_output = BytesIO()
        wb.save(final_output)
        final_output.seek(0)
        return final_output

    st.subheader("💾 Download Final Excel Sheet")
    original_filename = uploaded_file.name.replace(".xlsx", "")
    final_output = save_final_with_colors(df, uploaded_file, st.session_state.confirmed_rows, st.session_state.new_rows, st.session_state.edited_cells)
    st.download_button("📥 Download FINAL Sheet", final_output, file_name=f"FINAL {original_filename}.xlsx")
