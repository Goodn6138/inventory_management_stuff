import streamlit as st
import pandas as pd
import io

st.title("📦 Inventory Management Thingi")

# File uploader
uploaded_file = st.file_uploader("Upload your inventory Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Drop 'unknown' column if it exists
    if 'unknown' in df.columns:
        df = df.drop(columns=['unknown'])

    # Add 'confirmed' column if it doesn't exist
    if 'confirmed' not in df.columns:
        df['confirmed'] = ""

    # Search column selector
    search_column = st.selectbox("Search by column", options=df.columns[df.columns != 'confirmed'])

    # Search input
    search_value = st.text_input(f"Enter value to search in '{search_column}'")

    if search_value:
        # Filter the DataFrame
        filtered_df = df[df[search_column].astype(str).str.lower() == search_value.lower()]

        if not filtered_df.empty:
            st.write("✅ Match found:")
            st.dataframe(filtered_df)

            if st.button("Confirm"):
                # Update the 'confirmed' column for matched rows
                df.loc[df[search_column].astype(str).str.lower() == search_value.lower(), 'confirmed'] = "Y"
                st.success("✔️ Entry confirmed.")
        else:
            st.warning("⚠️ No match found.")

            if st.button("Add New Entry"):
                # Create a new row with the search value and 'B' in confirmed
                new_row = {col: "" for col in df.columns}
                new_row[search_column] = search_value
                new_row["confirmed"] = "B"
                df = df.append(new_row, ignore_index=True)
                st.success("➕ New entry added with 'B' confirmation.")

    # Save modified Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("💾 Download updated Excel file", output.getvalue(), "updated_inventory.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
