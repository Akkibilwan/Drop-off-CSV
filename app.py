import streamlit as st
import pandas as pd
from collections import defaultdict
import io

st.title("Cohort Session Attendance Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file, skiprows=1)
    df.columns = ["Sl No", "User Name", "User Email", "User ID", "Duration", "Sessions"]

    # Function to convert duration string to minutes
    def duration_to_minutes(duration):
        if 'h' in duration:
            hours = int(duration.split('h')[0])
            minutes = int(duration.split('h')[1].split('m')[0]) if 'm' in duration else 0
            return hours * 60 + minutes
        elif 'm' in duration:
            return int(duration.split('m')[0])
        else:
            return 0

    # Function to parse sessions and calculate retention/drop-off
    def calculate_retention_dropoff(sessions_str):
        retained_users = defaultdict(int)
        dropped_users = defaultdict(int)
        for session in sessions_str.strip().split('\n'):
            start_time_str, end_time_str = session.split(' - ')
            start_time = pd.to_datetime(start_time_str, format='%d/%m/%Y, %I:%M:%S %p')
            end_time = pd.to_datetime(end_time_str, format='%d/%m/%Y, %I:%M:%S %p')
            session_duration_minutes = (end_time - start_time).total_seconds() // 60
            for i in range(int(session_duration_minutes // 5) + 1):
                interval_start = start_time + pd.Timedelta(minutes=i * 5)
                interval_end = min(start_time + pd.Timedelta(minutes=(i + 1) * 5), end_time)
                time_interval_str = interval_start.strftime('%H:%M:%S')
                retained_users[time_interval_str] += 1
                if interval_end == end_time:
                    dropped_users[interval_end.strftime('%H:%M:%S')] += 1
        return retained_users, dropped_users

    # Calculate retention/drop-off for all users
    retention_dropoff_data = []
    for index, row in df.iterrows():
        sessions_str = row["Sessions"]
        retained_users, dropped_users = calculate_retention_dropoff(sessions_str)
        for interval, count in retained_users.items():
            retention_dropoff_data.append([interval, count, dropped_users.get(interval, 0)])

    # Create DataFrame
    retention_df = pd.DataFrame(retention_dropoff_data, columns=["Time Interval", "Users Retained", "Users Dropped"])
    retention_df = retention_df.groupby("Time Interval").sum().reset_index()

    # Display DataFrame
    st.dataframe(retention_df)

    # Download button
    csv_buffer = io.StringIO()
    retention_df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    st.download_button(label="Download data as CSV",
                       data=csv_string,
                       file_name="retention_data.csv",
                       mime='text/csv')
