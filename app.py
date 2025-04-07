import streamlit as st
import pandas as pd
import os
from io import BytesIO
import plotly.express as px

# Page title and interface
st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("Data Sweeper")
st.write("Upload your CSV or Excel files for data cleaning, interactive visualization, and conversion.")

# Here is a file uploader (CSV and Excel)
uploaded_files = st.file_uploader("Upload your (CSV or Excel) files", type=["csv", "xlsx", "xls"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type {file_ext}!")
            continue

        st.markdown(f"### File: {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")

        # Our original Data Preview
        with st.expander("Original Data Preview"):
            st.dataframe(df.head())

        # Sidebar for Data Cleeaning Options for better interface 
        with st.sidebar.form(key=f'cleaning_options_{file.name}'):
            st.header("Data Cleaning Options")
            remove_duplicates = st.checkbox("Remove duplicates", value=False)
            fill_missing = st.checkbox("Fill missing numeric values", value=False)
            selected_columns = st.multiselect("Select columns to keep", options=df.columns.tolist(), default=df.columns.tolist())

            submit_filters = st.form_submit_button("Apply Cleaning Options")

        # section of apply data cleaning options
        
        if submit_filters:
            if remove_duplicates:
                df = df.drop_duplicates()
                st.success("Duplicates removed.")
            if fill_missing:
                numeric_cols = df.select_dtypes(include=["number"]).columns
                if not numeric_cols.empty:
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("Missing numeric values filled with mean.")
            if selected_columns:
                df = df[selected_columns]
            
            # for the cleaned Data Preview
            with st.expander("Cleaned Data Preview"):
                st.dataframe(df.head())

        # for the interactive Visualization
        st.subheader("Interactive Visualization")
        numeric_df = df.select_dtypes(include=["number"])
        if not numeric_df.empty:
            chart_type = st.selectbox("Choose chart type", ["Line Chart", "Bar Chart", "Scatter Plot"], key=f'chart_type_{file.name}')
            
            if chart_type == "Line Chart":
                fig = px.line(numeric_df, title="Line Chart of Numeric Data")
            elif chart_type == "Bar Chart":
                fig = px.bar(numeric_df, title="Bar Chart of Numeric Data")
            elif chart_type == "Scatter Plot":
                cols = numeric_df.columns.tolist()
                if len(cols) >= 2:
                    fig = px.scatter(numeric_df, x=cols[0], y=cols[1], title=f"Scatter Plot: {cols[0]} vs {cols[1]}")
                else:
                    fig = px.scatter(numeric_df, title="Scatter Plot of Numeric Data")

            st.plotly_chart(fig, use_container_width=True, key=f"plot_{file.name}")

        
        else:
            st.info("No numeric columns available for visualization.")

        # for the conversion Options
        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")

        if st.button(f"Convert {file.name}", key=f"convert_btn_{file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                output_filename = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
                
            elif conversion_type == "Excel":
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                output_filename = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            buffer.seek(0)
            st.download_button(label=f"Download {output_filename}", data=buffer, file_name=output_filename, mime=mime_type)

st.success("All files successfully processed!")
