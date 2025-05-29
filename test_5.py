import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config("Inventory Manager", layout="wide")
st.title("📦 Inventory Manager with Confirmation & Edits")

# Upload file
uploaded_file = st.file_uploader("Upload your inventory Excel file", type=["xlsx"])

if uploaded_file:
    original_filename = os.path.splitext(uploaded_file.name)[0]
    df = pd.read_excel(uploaded_file)
    df = df.fillna("")
    st.session_state.setdefault("confirmed_rows", set())
    st.session_state.setdefault("new_rows", set())
    st.session_state.setdefault("edited_cells", {})

    # SEARCH SECTION
    st.subheader("🔍 Search for Machine")
    col_to_search = st.selectbox("Select column to search", df.columns)
    val_to_search = st.text_input("Enter value to search")
    search_btn = st.button("🔍 Search")

    match_indices = []
    match_df = pd.DataFrame()

    if search_btn and val_to_search:
        match_df = df[df[col_to_search].astype(str).str.lower() == val_to_search.lower()]
        match_indices = match_df.index.tolist()
        if match_df.empty:
            st.warning("No match found.")
        else:
            st.success(f"Found {len(match_df)} match(es)")
            st.dataframe(match_df)

    # CONFIRM MATCH
    if match_indices:
        selected_index = match_indices[0]
        confirm_btn = st.button("✅ Confirm Match")

        if confirm_btn:
            st.session_state.confirmed_rows.add(selected_index)
            st.success("Confirmed. Row will be marked green in final sheet.")

        # EDIT MATCHED ROW
        st.subheader("✏️ Edit This Equipment")
        edited = False
        for col in df.columns:
            new_val = st.text_input(f"{col}", value=str(df.at[selected_index, col]), key=f"{col}_edit")
            if new_val != str(df.at[selected_index, col]):
                df.at[selected_index, col] = new_val
                st.session_state.edited_cells[(selected_index, col)] = True
                edited = True

        if edited:
            st.info("Changes saved. Edited cells will be highlighted red.")

    # ADD NEW ROW
    st.subheader("➕ Add New Machine (if not found)")
    new_data = {}
    for col in df.columns:
        new_data[col] = st.text_input(f"New {col}", key=f"new_{col}")

    if st.button("➕ Add Machine"):
        df.loc[len(df)] = new_data
        df.at[len(df)-1, 'REMARKS'] = "New entry added"
        st.session_state.new_rows.add(len(df)-1)
        st.success("New machine added.")

    # SHOW UNMARKED ROWS
    st.subheader("👀 Unmarked (Not Confirmed/New) Machines")
    other_rows = df[~df.index.isin(st.session_state.confirmed_rows.union(st.session_state.new_rows))]
    st.dataframe(other_rows, use_container_width=True)

    # SAVE FINAL EXCEL
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Inventory')
    workbook = writer.book
    worksheet = writer.sheets['Inventory']

    green_fmt = workbook.add_format({'bg_color': '#C6EFCE'})
    blue_fmt = workbook.add_format({'bg_color': '#ADD8E6'})
    red_fmt = workbook.add_format({'bg_color': '#FFC7CE'})

    for i, row in df.iterrows():
        fmt_row = None
        if i in st.session_state.confirmed_rows:
            fmt_row = green_fmt
        elif i in st.session_state.new_rows:
            fmt_row = blue_fmt

        if fmt_row:
            worksheet.set_row(i + 1, None, fmt_row)

        # Highlight edited cells
        for j, col in enumerate(df.columns):
            if (i, col) in st.session_state.edited_cells:
                worksheet.write(i + 1, j, row[col], red_fmt)

    writer.close()
    output.seek(0)

    final_name = f"FINAL {original_filename}.xlsx"
    st.download_button("💾 Download FINAL Sheet", output, file_name=final_name)
