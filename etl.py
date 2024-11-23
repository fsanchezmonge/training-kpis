import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from supabase import Client, create_client

## GET ACTIVITIES FROM STRAVA ##
@st.cache_data
def fetch_strava():

    def get_access_token():
        auth_url = "https://www.strava.com/oauth/token"
        payload = {
        'client_id': '95885', 
        'client_secret': '9bd58f9a50e4a12d165a373bec9afe40754f4962',
        'refresh_token': '8c7224c28e9189553c08e193025f962f0936af76',
        'grant_type': "refresh_token",
        'f': 'json'
        }  
        res = requests.post(auth_url, data=payload, verify=False)
        try:
            access_token = res.json()['access_token']
            header = {'Authorization': 'Bearer ' + access_token}

        except KeyError:
            st.warning("An error occured while getting the data from Strava.")

        return access_token

    def get_unix_timestamp(date_string):
        dt = datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return int(dt.timestamp())

    def get_activities():
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            #"after": after_timestamp,
            #"before": before_timestamp,
            "per_page": 100,  # Number of activities to retrieve per page
            "page": 1
        }
        all_activities = []
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            activities = response.json()
            if not activities:
                break
            all_activities.extend(activities)
            params["page"] += 1
        return all_activities
    
    def clean_activities(all_activities):
        activity_data = []
        for activity in all_activities:
            activity_data.append({
                "athlete_id": activity["athlete"]["id"],
                "activity_id": activity["id"],
                "name": activity["name"],
                "sport": activity["type"],
                "type": activity["sport_type"],
                "datetime": activity["start_date_local"],
                "distance": activity["distance"]/1000,
                "moving_time": activity["moving_time"]/60,
                "elevation_gain": activity["total_elevation_gain"],
                "average_speed": activity["average_speed"] * 3.6,
                "average_heartrate": activity.get("average_heartrate", None),
                "workout_type": activity.get("workout_type", 'Training')
            })
        
        # Convert dictionary to dataframe
        activities_df = pd.DataFrame(activity_data, columns=['athlete_id', 'activity_id', 'name', 'sport', 'type', 'datetime', 'distance', 'moving_time', 'elevation_gain', 'average_speed', 'average_heartrate', 'workout_type'])
        
        # Extract date and time from date
        activities_df['datetime'] = pd.to_datetime(activities_df['datetime'])
        activities_df['date'] = activities_df['datetime'].dt.date
        activities_df['time'] = activities_df['datetime'].dt.time
        
        # Remove activities before 2023
        start_date = pd.to_datetime('2023-01-01')
        activities_df = activities_df[activities_df['date'] >= start_date]
        return activities_df
    
    # Replace with your access token
    access_token = get_access_token()

    # Supabase credentials
    supabase_url = 'https://mwivhbuesrdrfhihxjqs.supabase.co'
    supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im13aXZoYnVlc3JkcmZoaWh4anFzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk4NjE0NzQsImV4cCI6MjAzNTQzNzQ3NH0.cG7N8em6tqc2OWijtqTQg-EkUqHM6Bcf7grg-bPDcDA'

    # Initialize Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)

    # Get list of activities (json)
    activities = get_activities()

    # Converts activities in a df with the specified columns (not all source data is loaded in the df)
    activities_df = clean_activities(activities)

    activities_df = activities_df.sort_values(by='activity_id', ascending=True)
    #print(activities_df.tail(10))
    return activities_df

## DIM CALENDAR LOAD ##
@st.cache_data
def run_dim_calendar(db_url, db_key):
    # initialize Supabase client
    supabase: Client = create_client(db_url, db_key)

    # Calculate the start date as the minimum date from the initial data
    start_date = '2023-01-01' #activities_df['date'].min()

    # Calculate the end date as the current date
    end_date = datetime.now()

    # Generate the date range from start_date to end_date
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Create a DataFrame for the date dimension table
    date_dim = pd.DataFrame(date_range, columns=['date'])

    # Add date attributes
    date_dim['year'] = date_dim['date'].dt.year
    date_dim['month'] = date_dim['date'].dt.month
    date_dim['day'] = date_dim['date'].dt.day
    date_dim['day_of_week'] = date_dim['date'].dt.dayofweek
    date_dim['day_of_year'] = date_dim['date'].dt.dayofyear
    date_dim['week_of_year'] = date_dim['date'].dt.isocalendar().week
    date_dim['month_name'] = date_dim['date'].dt.strftime('%B')
    date_dim['day_name'] = date_dim['date'].dt.strftime('%A')
    #date_dim['is_leap_year'] = date_dim['date'].dt.is_leap_year

    # Reset index and set a surrogate key
    date_dim.reset_index(drop=True, inplace=True)
    date_dim['date_key'] = date_dim['date'].dt.strftime('%Y%m%d')

    # filter year 2023 or bigger
    date_dim = date_dim[date_dim['year'] >= 2023]

    # Rearrange columns to have the surrogate key first
    date_dim = date_dim[['date_key', 'date', 'year', 'month', 'day', 'day_of_week', 
                         'day_of_year', 'week_of_year', 'month_name', 'day_name']]

    date_dim['date'] = date_dim['date'].dt.strftime('%Y-%m-%d')

    # Display the first few rows of the date dimension table
    #print(date_dim.tail(5))

    # convert DataFrame to list of dictionaries
    date_dim_records = date_dim.to_dict(orient='records')

    # Truncate table
    table_name = 'dim_calendar'
    response = supabase.rpc('truncate_table', {'table_name': table_name}).execute()

    # insert data into Supabase table
    response = supabase.table('dim_calendar').insert(date_dim_records).execute()

## FACT ACTIVITIES LOAD ##
@st.cache_data
def run_fact_activities(db_url, db_key, activities_df):
    # initialize Supabase client
    supabase: Client = create_client(db_url, db_key)

    # Function to fetch dimension tables from Supabase
    def fetch_dim_race_table():
        response = supabase.table('dim_race').select("race_key","name").execute()
        return pd.DataFrame(response.data)

    def fetch_dim_sport_type_table():
        response = supabase.table('dim_sport_type').select("sport_type_key","sport","type").execute()
        return pd.DataFrame(response.data)

    def fetch_dim_calendar_table():
        response = supabase.table('dim_calendar').select("date_key","date").execute()
        return pd.DataFrame(response.data)

    # Fetch existing fact table from Supabase
    def fetch_existing_fact_activity():
        response = supabase.table('fact_activity').select("activity_id").execute()
        return pd.DataFrame(response.data)

    # Function to lookup surrogate keys
    def lookup_dim_race_keys(source_df, dimension_df):
        merged_df = source_df.merge(dimension_df[['name', 'race_key']], on='name', how='left')
        return merged_df

    def lookup_dim_sport_type_keys(source_df, dimension_df):
        merged_df = source_df.merge(dimension_df[['type', 'sport_type_key']], on='type', how='left')
        return merged_df

    def lookup_dim_calendar_keys(source_df, dimension_df):
        merged_df = source_df.merge(dimension_df[['date','date_key']], on='date', how='left')
        return merged_df


    # Fetch the dim tables
    dim_race_df = fetch_dim_race_table()
    dim_sport_type_df = fetch_dim_sport_type_table()
    dim_calendar_df = fetch_dim_calendar_table()

    # RACE KEY LOOKUP
    result_df = lookup_dim_race_keys(activities_df, dim_race_df)

    # SPORT TYPE KEY LOOKUP
    result_df = lookup_dim_sport_type_keys(result_df, dim_sport_type_df)

    # Adjust date format from activities df
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')

    # DATE KEY LOOKUP
    result_df = lookup_dim_calendar_keys(result_df, dim_calendar_df)

    # Specify the columns you want to select
    fact_columns = ['activity_id', 'athlete_id', 'name','datetime','distance', 'moving_time', 'elevation_gain', 'average_speed',
                    'average_heartrate','date_key','sport_type_key','race_key']

    # Create a new DataFrame with only the specified columns
    fact_activity = result_df[fact_columns]

    # Convert timestamp to string for insert
    fact_activity['datetime'] = fact_activity['datetime'].astype(str)

    # Handling NaN values
    fact_activity = fact_activity.fillna({
        'distance': 0,
        'moving_time': 0,
        'elevation_gain': 0,
        'average_speed': 0,
        'average_heartrate': 0,
        'date_key': 999,
        'sport_type_key': 999,
        'race_key': 999
    })

    fact_activity['date_key'] = fact_activity['date_key'].astype(int)
    fact_activity['sport_type_key'] = fact_activity['sport_type_key'].astype(int)
    fact_activity['race_key'] = fact_activity['race_key'].astype(int)

    # Fetch existing records from the fact_activity table
    existing_fact_activity = fetch_existing_fact_activity()

    # Identify new rows that are not in the existing fact_activity table
    new_fact_activity = fact_activity[~fact_activity['activity_id'].isin(existing_fact_activity['activity_id'])]

    # Convert to dict and insert only new records into fact table
    fact_activity_records = new_fact_activity.to_dict(orient='records')

    # Insert new data
    if fact_activity_records:  # Only insert if there are new records
        response = supabase.table('fact_activity').insert(fact_activity_records).execute()
        return len(fact_activity_records), new_fact_activity
    else:
        new_fact_activity = []
        return 0, new_fact_activity