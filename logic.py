from supabase import create_client, Client
from datetime import datetime
import pandas as pd
import numpy as np

url: str = "https://mwivhbuesrdrfhihxjqs.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im13aXZoYnVlc3JkcmZoaWh4anFzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk4NjE0NzQsImV4cCI6MjAzNTQzNzQ3NH0.cG7N8em6tqc2OWijtqTQg-EkUqHM6Bcf7grg-bPDcDA"
supabase: Client = create_client(url, key)

def get_volume_last8weeks() -> dict:
    response = supabase.table('vw_volume_last8weeks') \
        .select('*') \
        .order('week_of_year', desc=False) \
        .execute()
    return response.data

def get_adaptation_last4weeks() -> dict:
    response = supabase.table('vw_adaptation_last4weeks') \
        .select('*') \
        .order('week_of_year', desc=False) \
        .execute()
    return response.data

def get_last_activities(limit):
    # Query to fetch the last 'limit' activities from the fact_activity table
    response = supabase.table("fact_activity") \
        .select("activity_id, name, datetime, distance, moving_time, elevation_gain") \
        .or_("sport_type_key.eq.15,sport_type_key.eq.14") \
        .order("datetime", desc=True) \
        .limit(limit) \
        .execute()
    return response.data

def get_last_file_date() -> dict:
    response = supabase.table('fact_hrv') \
        .select('updated_at') \
        .order('date_key', desc=True) \
        .limit(1) \
        .execute()
    
    if response.data:  # Check if there is data returned
        timestamp = response.data[0]['updated_at']  # Get the timestamp
        formatted_date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')  # Convert to yyyy-mm-dd format
        return {'formatted_date': formatted_date}  # Return the formatted date
    return {}  # Return an empty dict if no data

def get_last_training_date() -> dict:
    response = supabase.table('fact_activity') \
        .select('datetime') \
        .order('date_key', desc=True) \
        .limit(1) \
        .execute()
    
    if response.data:  # Check if there is data returned
        timestamp = response.data[0]['datetime']  # Get the timestamp
        formatted_date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')  # Convert to yyyy-mm-dd format
        return {'formatted_date': formatted_date}  # Return the formatted date
    return {}  # Return an empty dict if no data

def calculate_moving_time_variation() -> dict:
    data = get_volume_last8weeks()
    
    # Get the most recent week's data
    current_week_time = data[-1]['total_moving_time']
    current_week_distance = data[-1]['distance']
    current_week_elevation = data[-1]['elevation_gain']
    
    # Calculate average of last 3 weeks (if available)
    if len(data) >= 4:  # Need at least 4 weeks (current + 3 previous)
        # Calculate averages excluding current week
        previous_weeks = data[-4:-1]  # Get last 3 weeks before current week
        avg_time = sum(week['total_moving_time'] for week in previous_weeks) / 3
        avg_distance = sum(week['distance'] for week in previous_weeks) / 3
        avg_elevation = sum(week['elevation_gain'] for week in previous_weeks) / 3
        
        time_variation = ((current_week_time - avg_time) / avg_time) * 100
        distance_variation = ((current_week_distance - avg_distance) / avg_distance) * 100
        elevation_variation = ((current_week_elevation - avg_elevation) / avg_elevation) * 100

    else:
        time_variation = None
        distance_variation = None
        elevation_variation = None
    
    return {
        'current_week_moving_time': current_week_time,
        'week_over_week_variation': time_variation,
        'current_week_distance': current_week_distance,
        'distance_variation': distance_variation,
        'current_week_elevation': current_week_elevation,
        'elevation_variation': elevation_variation
    }

def calculate_adaptation_last4weeks() -> dict:
    data = get_adaptation_last4weeks()

    current_week_hrv = data[-1]['hrv_points']
    current_week_sleep_quality = data[-1]['sleep_quality']
    current_week_fatigue = data[-1]['avg_fatigue']
    current_week_mental_energy = data[-1]['avg_mental_energy']

    # Calculate average of last 3 weeks (if available)
    if len(data) >= 4:  # Need at least 4 weeks (current + 3 previous)
        # Calculate averages excluding current week
        previous_weeks = data[-4:-1]  # Get last 3 weeks before current week
        avg_hrv = sum(week['hrv_points'] for week in previous_weeks) / 3
        avg_sleep_quality = sum(week['sleep_quality'] for week in previous_weeks) / 3
        avg_fatigue = sum(week['avg_fatigue'] for week in previous_weeks) / 3
        avg_mental_energy = sum(week['avg_mental_energy'] for week in previous_weeks) / 3
        
        hrv_variation = ((current_week_hrv - avg_hrv) / avg_hrv) * 100
        sleep_quality_variation = ((current_week_sleep_quality - avg_sleep_quality) / avg_sleep_quality) * 100
        fatigue_variation = ((current_week_fatigue - avg_fatigue) / avg_fatigue) * 100
        mental_energy_variation = ((current_week_mental_energy - avg_mental_energy) / avg_mental_energy) * 100
    else:
        hrv_variation = None
        sleep_quality_variation = None
        fatigue_variation = None
        mental_energy_variation = None

    return {
        'current_week_hrv': current_week_hrv,
        'hrv_variation': hrv_variation, 
        'current_week_sleep_quality': current_week_sleep_quality,
        'sleep_quality_variation': sleep_quality_variation,
        'current_week_fatigue': current_week_fatigue,
        'fatigue_variation': fatigue_variation,
        'current_week_mental_energy': current_week_mental_energy,
        'mental_energy_variation': mental_energy_variation
    }

def process_uploaded_file(uploaded_file):
    """
    Process the uploaded CSV file and return a filtered DataFrame
    """
    # Read CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)
    
    # Define the columns we want to keep
    columns_to_keep = [
        'timestamp_measurement', 'HR', 'HRV4T_Recovery_Points',
        'training', 'training_performance', 'physical_condition',
        'trainingRPE', ' trainingMotivation', ' sleep_quality',
        'mental_energy', 'muscle_soreness', 'fatigue',
        ' vo2max', ' daily_message'
    ]
    # Clean column names by removing leading/trailing spaces
    df = df[columns_to_keep]
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={
        'trainingmotivation': 'training_motivation'
    })
    # Filter out rows where timestamp_measurement is invalid
    df = df[df['timestamp_measurement'].notna() & 
            (df['timestamp_measurement'] != '-') & 
            (df['timestamp_measurement'] != '')]

    # Convert timestamp_measurement to datetime
    df['timestamp_measurement'] = pd.to_datetime(df['timestamp_measurement'])
    
    # Convert trainingrpe to numeric first, then round and convert to integer
    df['trainingrpe'] = pd.to_numeric(df['trainingrpe'], errors='coerce')  # Convert to numeric, invalid values become NaN
    df['trainingrpe'] = df['trainingrpe'].round().astype('Int64')  # Using Int64 to handle NaN values
    
    # Create date_key and wakeup_time columns
    df['date_key'] = df['timestamp_measurement'].dt.strftime('%Y%m%d')
    df['wakeup_time'] = df['timestamp_measurement'].dt.strftime('%H:%M:%S')
    
    df = df.replace('-', None)
    df = df.fillna(np.nan).replace([np.nan], [None])
    # Drop the original timestamp column
    df_processed = df.drop('timestamp_measurement', axis=1)
      
    return df_processed

def insert_measurements_to_db(df: pd.DataFrame) -> tuple[int, list]:
    """
    Insert new measurements into the database
    Returns: tuple(number of rows inserted, list of errors if any)
    """
    # Get existing records from the database to check for changes
    existing_records_response = supabase.table('fact_hrv').select('*').execute()
    existing_records = {row['date_key']: row for row in existing_records_response.data}

    # Filter out records that already exist in the database
    new_records = df[~df['date_key'].isin(existing_records.keys())]

    # Check for changed records and update them
    updated_records = []
    for index, row in df.iterrows():
        date_key = row['date_key']
        if date_key in existing_records:
            existing_record = existing_records[date_key]
            # Compare only the 'training' field
            if row['training'] != existing_record['training']:
                # Prepare the record for update
                updated_records.append({
                    'training': row['training'],
                    'date_key': date_key  # Include the key to identify the record
                })

    # Insert new records
    if not new_records.empty:
        records_to_insert = new_records.to_dict('records')
        try:
            response = supabase.table('fact_hrv').insert(records_to_insert).execute()
        except Exception as e:
            return 0, [str(e)]

    # Update existing records
    for record in updated_records:
        try:
            supabase.table('fact_hrv').update(record).eq('date_key', record['date_key']).execute()
        except Exception as e:
            return 0, [str(e)]

    return len(new_records) + len(updated_records), []

def get_intensity_last4weeks() -> dict:
    response = supabase.table('vw_intensity_last4weeks') \
        .select('*') \
        .order('week_of_year', desc=False) \
        .execute()
    return response.data

def calculate_intensity_variation() -> dict:
    data = get_intensity_last4weeks()
    # Get the most recent week's data
    current_week_days = data[-1]['hard_days']
    
    # Calculate average of last 3 weeks (if available)
    if len(data) >= 2:  # Need at least 4 weeks (current + 3 previous)
        # Calculate averages excluding current week
        previous_week = data[-2]['hard_days']  # Get last 3 weeks before current week
        count_variation = (current_week_days - previous_week)
    else:
        count_variation = None
    
    return {
        'current_week_days': current_week_days,
        'week_over_week_variation': count_variation
    }

def store_fuelling_data(activity_id, nutrition_type, carbs_gram, nutrition_tag, feeling_tag):
    # Create a DataFrame from the input data
    data = {
        'activity_id': [activity_id],
        'nutrition_type': [nutrition_type],
        'carbs_grams': [carbs_gram],
        'nutrition_tag': [nutrition_tag],
        'feeling_tag': [feeling_tag]
    }
    df = pd.DataFrame(data)  # Convert to DataFrame

    # Convert data types using pandas
    df['activity_id'] = df['activity_id'].astype(int)  # Ensure activity_id is an integer
    df['carbs_grams'] = df['carbs_grams'].astype(int)  # Ensure carbs_grams is an integer

    # Insert new records
    try:
        # Insert fuelling data into the database
        response = supabase.table('dim_fuelling').insert(df.to_dict('records')).execute()
    except Exception as e:
        return 0, [str(e)]