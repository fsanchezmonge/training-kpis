import streamlit as st
from utils.logic import get_last_activities, store_fuelling_data, process_uploaded_file, insert_measurements_to_db
import pandas as pd
import plotly.express as px

def display_hrv_data_upload():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Process the uploaded file
            df_processed = process_uploaded_file(uploaded_file)
            
            # Display preview before insertion
            st.write("### Data Preview:")
            st.dataframe(df_processed.tail(5))
            
            # Insert data into database
            rows_inserted, errors = insert_measurements_to_db(df_processed)
            
            if errors:
                st.error("Errors occurred during insertion:")
                for error in errors:
                    st.error(error)
            else:
                if rows_inserted == 0:
                    st.info("No new records were found to insert (all dates already exist in database)")
                else:
                    st.success(f"Successfully processed file and inserted {rows_inserted} new records!")            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def display_fuelling_data_upload():
    # Get the last 5 activities
    last_activities = get_last_activities(10)  # Fetch last 5 activities
    # Create a DataFrame for better display
    activities_df = pd.DataFrame(last_activities)
    #st.dataframe(activities_df)

    # Create a new column in the DataFrame for display, including activity_id
    activities_df['display'] = activities_df.apply(lambda row: f"{row['name']} on {pd.to_datetime(row['datetime']).strftime('%m-%d-%Y')}, {row['distance']:.2f}km in {row['moving_time']:.0f} minutes", axis=1)
    
    # Allow user to select an activity based on the new display column
    activity_id = st.selectbox("Select an activity", activities_df['display'], format_func=lambda x: x)  # Updated to use the new display column

    # Get the selected activity_id based on the display selection
    selected_activity = activities_df[activities_df['display'] == activity_id]
    activity_id = selected_activity['activity_id'].values[0]  # Assuming 'id' is the column name for activity_id

    # Create a row for nutrition type and carbohydrate grams input
    col1, col2, col3, col4 = st.columns(4) 

    with col1:
        # Dropdown for nutrition type
        nutrition_type = st.selectbox("Select nutrition type", ["Gel", "Bar", "Solid", "Fruit", "Gummies", "Drink Mix"])
    with col2:
        # Input for grams of carbohydrates
        carbs_grams = st.number_input("Enter grams of carbohydrates", min_value=0, step=5)
    with col3:
        nutrition_tag = st.text_input("Enter the brand or any other tag")
    with col4:
        feeling_tag = st.selectbox("How did you feel?", ["Great", "Not great", "Terrible"])

    # Button to submit the fuelling data
    if st.button("Submit"):
        if carbs_grams > 0:
            # Store the fuelling data in the database
            store_fuelling_data(activity_id, nutrition_type, carbs_grams, nutrition_tag, feeling_tag)
            st.success("Fuelling data submitted successfully!")
        else:
            st.error("Please enter the required data.")

if st.session_state.user != None:
    st.title("Data Entry")
    st.write("")

    st.subheader("HRV Data Upload:anatomical_heart:")
    st.write("Upload your data from HRV4Training, you can export the file and send it to your email from the app.")
    display_hrv_data_upload()

    st.divider()

    st.subheader("Fuelling Data Entry:chocolate_bar:")
    st.write("Keep track of your carb intake during training and races.")
    display_fuelling_data_upload()

else:
    st.warning("You need to be logged in to see this page! Create a user or sign-in in the Home page")
