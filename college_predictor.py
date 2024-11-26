import streamlit as st
import pandas as pd
import datetime

# Title for the Streamlit app
st.title("KCET College Cutoff Viewer")

# Define the local file path for the Excel file
FILE_PATH = "https://raw.githubusercontent.com/mithrangowda07/College-Predictor/main/cet_colg_data1.xlsx"

# Load the Excel file
@st.cache_data
def load_excel_file():
    """Load Excel file from local storage."""
    try:
        data = pd.read_excel(FILE_PATH, engine='openpyxl')
        return data
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

df = load_excel_file()
if df is not None:
    # Clean column names
    df.columns = df.columns.str.strip()

    # Dropdown for selecting app mode
    app_mode = st.selectbox("Select an option", ["--Select--","Sort the college"])

    if app_mode == "Sort the college":
        st.write("Choose **Start** to enter the college sorting or **End** to end the session.")
        app_mode1 = st.selectbox("Select", ["--Select--","Start", "End"])

        # Initialize session state variables
        if "selected_colleges" not in st.session_state:
            st.session_state["selected_colleges"] = []

        if app_mode1 == "Start":
            # Select category every time
            category_list = [
                col
                for col in df.columns
                if col not in ["College Code", "College Name", "Branch", "Branch code", "Place"]
            ]
            selected_category = st.selectbox("Select Category", ["--Select--"] + category_list)

            # Dropdowns for college and branch selection
            selected_college = st.selectbox("Select College", ["--Select--"] + sorted(df["College Name"].unique()))
            selected_branch = st.selectbox(
                "Select Branch",
                ["--Select--"] + (sorted(df[df["College Name"] == selected_college]["Branch"].unique()) if selected_college != "--Select--" else [])
            )

            # Ensure valid selections before proceeding
            if st.button("Add to list"):
                if selected_category != "--Select--" and selected_college != "--Select--" and selected_branch != "--Select--":
                    # Filter data
                    filtered_data = df[
                        (df["College Name"] == selected_college) & (df["Branch"] == selected_branch)
                    ]
                    if not filtered_data.empty:
                        cutoff_rank = filtered_data[selected_category].values[0]
                        st.success(f"Cutoff Rank: {cutoff_rank}")
                        st.session_state["selected_colleges"].append(
                            [selected_college, selected_branch, cutoff_rank]
                        )
                    else:
                        st.error(f"No data available for {selected_college} in {selected_branch} under {selected_category}.")
                else:
                    st.warning("Please make valid selections for Category, College, and Branch.")

            # Show selected list
            if st.button("Show the sorted list"):
                if st.session_state["selected_colleges"]:
                    sorted_colleges = sorted(
                        st.session_state["selected_colleges"], key=lambda x: x[2]
                    )
                    st.write("Selected Colleges and Cutoffs:")
                    selected_df = pd.DataFrame(
                        sorted_colleges,
                        columns=["College", "Branch", "Cutoff"]
                    )
                    st.table(selected_df)

                    # Download button for CSV
                    csv = selected_df.to_csv(index=False).encode("utf-8")
                    today = datetime.date.today().strftime("%Y-%m-%d")
                    st.download_button(
                        label="Download as CSV",
                        data=csv,
                        file_name=f"selected_colleges_{today}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No selections made yet.")

        elif app_mode1 == "End":
            st.success("Session ended successfully!")
            st.session_state["selected_colleges"].clear()  # Clear the list
else:
    st.error("Unable to load the Excel file. Check the file path or format.")
