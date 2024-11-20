import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Title for the Streamlit app
st.title("KCET College Cutoff Viewer")

# Google Sheets export URL
url = "https://docs.google.com/spreadsheets/d/1yD2ct4_UxjamT3PtRWQPgewCrD2zaKuoRQHsqado8s4/export?format=xlsx"

# Try downloading and reading the Excel file
try:
    # Download the file
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Load the file into a Pandas DataFrame
    file = BytesIO(response.content)
    df = pd.read_excel(file, engine="openpyxl")  # Specify the engine explicitly

    st.success("File loaded successfully")
except Exception as e:
    st.error(f"An error occurred: {e}")
    st.stop()  # Stop execution if there's an error

# Clean column names
df.columns = df.columns.str.strip()  # Remove extra spaces from column names

# Dropdown for selecting app mode
app_mode = st.selectbox("Select an option", ["Sort the college"])

if app_mode == "Sort the college":
    st.write("Choose **Start** to enter the college sorting or **End** to end the session.")
    app_mode1 = st.selectbox("Select", ["Start", "End"])

    # Initialize session state variables
    if "selected_colleges" not in st.session_state:
        st.session_state["selected_colleges"] = []

    if app_mode1 == "Start":
        # Select category every time
        category_list = [
            col
            for col in df.columns
            if col not in ["College Code", "College Name", "Branch", "Branch code"]
        ]
        selected_category = st.selectbox(
            "Select Category", ["Select"] + category_list
        )

        # Dropdowns for college and branch selection
        selected_college = st.selectbox(
            "Select College", ["Select"] + list(df["College Name"].unique())
        )
        selected_branch = st.selectbox(
            "Select Branch", ["Select"] + list(df["Branch"].unique())
        )

        # Ensure valid selections before proceeding
        if st.button("Submit"):
            if (
                selected_category != "Select"
                and selected_college != "Select"
                and selected_branch != "Select"
            ):
                # Filter data
                filtered_data = df[
                    (df["College Name"] == selected_college)
                    & (df["Branch"] == selected_branch)
                ]
                if not filtered_data.empty:
                    cutoff_rank = filtered_data.iloc[0][selected_category]
                    st.success(f"Cutoff Rank: {cutoff_rank}")
                    st.session_state["selected_colleges"].append(
                        [selected_college, selected_branch, cutoff_rank]
                    )
                else:
                    st.error("No data available for the selected options.")
            else:
                st.warning("Please make valid selections for Category, College, and Branch.")

        # Show selected list
        if st.button("Show the list"):
            st.session_state["selected_colleges"] = sorted(
            st.session_state["selected_colleges"], key=lambda x: x[2]
            )
            if st.session_state["selected_colleges"]:
                st.write("Selected Colleges and Cutoffs:")
                selected_df = pd.DataFrame(
                    st.session_state["selected_colleges"],
                    columns=["College", "Branch", "Cutoff"]
                )
                st.table(selected_df)

                # Download button for CSV
                csv = selected_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name="selected_colleges.csv",
                    mime="text/csv"
                )
            else:
                st.info("No selections made yet.")

    elif app_mode1 == "End":
        st.success("Session ended successfully!")
        st.session_state["selected_colleges"] = []  # Clear the list
