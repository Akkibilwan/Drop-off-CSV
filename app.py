import streamlit as st
import pandas as pd

def process_data(data):
    # Clean and parse session times
    data['Cleaned Session End'] = data['Sessions'].str.split(' - ').str[1].str.split('\n').str[0]
    data['Session Start'] = pd.to_datetime(data['Sessions'].str.split(' - ').str[0], format='%d/%m/%Y, %I:%M:%S %p')
    data['Session End'] = pd.to_datetime(data['Cleaned Session End'].str.strip(), format='%d/%m/%Y, %I:%M:%S %p')

    # Create a range of times at 5-minute intervals between the earliest and latest times in the data
    start_time = data['Session Start'].min().floor('5T')
    end_time = data['Session End'].max().ceil('5T')
    time_range = pd.date_range(start=start_time, end=end_time, freq='5T')

    # Initialize a DataFrame to hold drop-off counts and users present
    drop_off_counts = pd.DataFrame(0, index=time_range, columns=['Drop-offs', 'Users Present'])

    # Calculate the drop-offs and users present for each 5-minute interval
    for i in range(len(time_range) - 1):
        current_interval = (data['Session End'] >= time_range[i]) & (data['Session End'] < time_range[i + 1])
        users_present = (data['Session Start'] <= time_range[i]) & (data['Session End'] >= time_range[i])
        
        drop_off_counts.loc[time_range[i], 'Drop-offs'] = current_interval.sum()
        drop_off_counts.loc[time_range[i], 'Users Present'] = users_present.sum()

    drop_off_counts['Time'] = drop_off_counts.index.strftime('%H:%M')
    drop_off_counts.reset_index(drop=True, inplace=True)

    return drop_off_counts

def main():
    st.title("Session Analysis: Drop-offs and Users Present")
    st.write("Upload a CSV file containing session data to generate a report with drop-off counts and users present.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read the CSV file
        data = pd.read_csv(uploaded_file)

        # Process the data to get drop-off counts and users present
        report = process_data(data)

        # Display the report
        st.write("Report: Drop-offs and Users Present Every 5 Minutes")
        st.dataframe(report)

        # Convert DataFrame to CSV
        csv = report.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Report CSV", data=csv, file_name='drop_off_and_presence_report.csv', mime='text/csv')

if __name__ == "__main__":
    main()
