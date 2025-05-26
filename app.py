import datetime

import altair as alt
import streamlit as st
import pandas as pd
import time
import os

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    # Convert dict to DataFrame with a single row
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        # If CSV doesn't exist, write with headers
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        # Else, we need to append without writing the header!
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()


def main():
    st.title("Usability Testing Tool")

    home, consent, demographics, tasks, exit, report = st.tabs(
        ["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"])

    with home:
        st.header("Introduction")
        st.write("""
        Welcome to the Usability Testing Tool for HCI.

        In this app, you will:
        1. Provide consent for data collection.
        2. Fill out a short demographic questionnaire.
        3. Perform a specific task (or tasks).
        4. Answer an exit questionnaire about your experience.
        5. View a summary report (for demonstration purposes).
        """)

    with consent:
        st.header("Consent Form")

        # TODO: Create your consent form and a variable called consent_given
        st.write("Please read the following consent statement carefully:")
        st.write(
            "By checking the box below, you confirm that you understand and agree to the collection and use of your data for the purposes of the Usability Testing Tool, and that you can stop using the tool or revoke consent for the tool at any time.")
        consent_given = st.checkbox("I have read and agree")

        if st.button("Submit Consent"):
            if not consent_given:
                st.warning("You must agree to the consent terms before proceeding.")
            else:
                # Save the consent acceptance time
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "consent_given": consent_given
                }
                save_to_csv(data_dict, CONSENT_CSV)

    with demographics:
        st.header("Demographic Questionnaire")

        name = st.text_input("What is your name?")
        dob = st.date_input("When were you born?", min_value="1900-01-01", max_value="today")
        occupation = st.text_input("What do you do for a living?")
        familiarity = st.selectbox("How familiar are you  with Usability Testing Tools", ("Very Familiar", "Familiar", "Neutral", "Not As Familiar", "Never Used"))

        with st.form("demographic_form"):
            # TODO: Create the demographic form
            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                today = datetime.date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                if not name:
                    st.warning("Please enter your name")
                elif not age:
                    st.warning("Please enter your age")
                elif not occupation:
                    st.warning("Please enter your occupation")
                else:
                    data_dict = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "name": name,
                        "age": age,
                        "occupation": occupation,
                        "familiarity": familiarity
                    }
                    save_to_csv(data_dict, DEMOGRAPHIC_CSV)

    with tasks:
        st.header("Task Page")

        st.write("Please select a task and record your experience completing it.")

        # For this template, we assume there's only one task, in project 3, we will have to include the actual tasks
        selected_task = st.selectbox("Select Task", ["Task 1: Example Task"])
        st.write("Task Description: Perform the example task in our system...")

        # Track success, completion time, etc.
        start_button = st.button("Start Task Timer")
        if start_button:
            st.session_state["start_time"] = time.time()

        stop_button = st.button("Stop Task Timer")
        if stop_button and "start_time" in st.session_state:
            duration = time.time() - st.session_state["start_time"]
            st.session_state["task_duration"] = duration

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"])
        notes = st.text_area("Observer Notes")

        if st.button("Save Task Results"):
            duration_val = st.session_state.get("task_duration", None)

            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_name": selected_task,
                "success": success,
                "duration_seconds": duration_val if duration_val else "",
                "notes": notes
            }
            save_to_csv(data_dict, TASK_CSV)

            # Reset any stored time in session_state if you'd like
            if "start_time" in st.session_state:
                del st.session_state["start_time"]
            if "task_duration" in st.session_state:
                del st.session_state["task_duration"]

    with exit:
        st.header("Exit Questionnaire")

        satisfaction = st.slider("Rate your satisfaction level with the tool (1 = Lowest, 5 = Highest)", min_value=1, max_value=5, step=1, value=3)
        difficulty = st.slider("Rate the difficulty of using the tool (1 = Lowest, 5 = Highest)", min_value=1, max_value=5, step=1, value=3)
        open_feedback = st.text_area("Additional Feedback/Comments")

        with st.form("exit_form"):
            # TODO: likert scale or other way to have an exit questionnaire

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "satisfaction": satisfaction,
                    "difficulty": difficulty,
                    "open_feedback": open_feedback
                }
                save_to_csv(data_dict, EXIT_CSV)
                st.success("Exit questionnaire data saved.")

    with report:
        st.header("Usability Report - Aggregated Results")

        st.write("**Consent Data**")
        consent_df = load_from_csv(CONSENT_CSV)
        if not consent_df.empty:
            st.dataframe(consent_df)
        else:
            st.info("No consent data available yet.")

        st.write("**Demographic Data**")
        demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
        if not demographic_df.empty:
            st.dataframe(demographic_df)


            age_bins = [0, 17, 36, 55, 100] # Leave our upper bin at 100... unless we are doing Usability Testing with centenarians
            age_labels = ["0–17", "18–36", "37–55", "56+"]
            demographic_df["age_bracket"] = pd.cut(
                demographic_df["age"],
                bins=age_bins,
                labels=age_labels,
                include_lowest=True,
            )

            fam_order = ["Never Used", "Not As Familiar", "Neutral", "Familiar", "Very Familiar"]

            age_bracket_chart = (
                alt.Chart(demographic_df)
                .mark_bar()
                .encode(
                    x=alt.X("age_bracket:N", title="Age Bracket"),
                    y=alt.Y(
                        "count()",
                        title="Number of Participants",
                        axis=alt.Axis(format="d", tickMinStep=1)
                    )
                )
                .properties(title="Participants by Age Bracket")
            )
            st.altair_chart(age_bracket_chart, use_container_width=True)

            fam_chart = (
                alt.Chart(demographic_df)
                .mark_bar()
                .encode(
                    x=alt.X("familiarity:N", sort=fam_order, title="Familiarity"),
                    y=alt.Y(
                        "count()",
                        title="Count",
                        axis=alt.Axis(format="d", tickMinStep=1)
                    )
                )
                .properties(title="Familiarity with Usability Testing Tools")
            )
            st.altair_chart(fam_chart, use_container_width=True)
        else:
            st.info("No demographic data available yet.")

        st.write("**Task Performance Data**")
        task_df = load_from_csv(TASK_CSV)
        if not task_df.empty:
            st.dataframe(task_df)
        else:
            st.info("No task data available yet.")

        st.write("**Exit Questionnaire Data**")
        exit_df = load_from_csv(EXIT_CSV)
        if not exit_df.empty:
            st.dataframe(exit_df)
        else:
            st.info("No exit questionnaire data available yet.")


        # Demographic Averages
        if not demographic_df.empty:
            st.subheader("Demographic Questionnaire Averages")
            avg_participant_age = demographic_df["age"].mean()

            st.write(f"**Average Participant Age:** {avg_participant_age:.0f}")

        # Example of aggregated stats (for demonstration only)
        if not exit_df.empty:
            st.subheader("Exit Questionnaire Averages")
            avg_satisfaction = exit_df["satisfaction"].mean()
            avg_difficulty = exit_df["difficulty"].mean()
            st.write(f"**Average Satisfaction**: {avg_satisfaction:.2f}")
            st.write(f"**Average Difficulty**: {avg_difficulty:.2f}")


if __name__ == "__main__":
    main()