import streamlit as st
from utils.logic import get_fuelling_data, get_vo2_data
import pandas as pd
import plotly.express as px

def display_fuelling_log_chart(fuelling_df):
    col1, col2 = st.columns(2)
    # Create a point chart using plotly
    with col1:
        fig = px.scatter(fuelling_df, x='average_speed', y='carbs_per_hour',
                        title='Carbs Intake vs Average Speed',
                        labels={'average_speed': 'Average Speed (km/h)', 'carbs_per_hour': 'Carbs per Hour (g)'})
        fig.update_traces(marker=dict(size=10))  # Adjust the size as needed
        # Show the plot in Streamlit
        st.plotly_chart(fig)
    with col2:
        fig = px.scatter(fuelling_df, x='moving_time', y='carbs_per_hour',
                        title='Carbs Intake vs Moving Time',
                        labels={'moving_time': 'Moving Time (min)', 'carbs_per_hour': 'Carbs per Hour (g)'})
        fig.update_traces(marker=dict(size=10))  # Adjust the size as needed
        # Show the plot in Streamlit
        st.plotly_chart(fig)
        
def display_vo2_chart(vo2_df):
    # Check if vo2_df is a list and convert it to a DataFrame
    if isinstance(vo2_df, list):
        vo2_df = pd.DataFrame(vo2_df)

    # Ensure 'date_key' is treated as a string before conversion
    vo2_df['date_key'] = vo2_df['date_key'].astype(str)

    # Convert 'date_key' from 'yyyymmdd' to datetime
    vo2_df['date_key'] = pd.to_datetime(vo2_df['date_key'], format='%Y%m%d', errors='coerce')

    # Sort the DataFrame by 'date_key' in descending order
    vo2_df = vo2_df.sort_values(by='date_key', ascending=False)

    # Format 'date_key' to 'dd-mm' for display
    vo2_df['date_key_display'] = vo2_df['date_key'].dt.strftime('%d-%m')

    col1, col2 = st.columns(2)
    # Create a point chart using plotly
    with col1:
        fig = px.scatter(vo2_df, x='date_key_display', y='vo2max',
                        title='',
                        labels={'date_key_display': 'Date', 'vo2max': 'VO2max'})
        
        # Ensure the x-axis is treated as categorical
        fig.update_xaxes(type='category')

        fig.update_traces(marker=dict(size=10))  # Adjust the size as needed
        fig.update_yaxes(title_text='VO2max (mL/kg/min)', range=[53, 64])  # Set the title and range as needed
        # Show the plot in Streamlit
        st.plotly_chart(fig)

if st.session_state.user != None:
    st.title("Insights")
    st.write("")
    st.write(st.session_state.user)

    with st.expander("**Fuelling log**"):
        fuelling_df = get_fuelling_data()      
        display_fuelling_log_chart(fuelling_df)

    with st.expander("**Estimated VO2max**"):
        vo2_df = get_vo2_data()      
        display_vo2_chart(vo2_df)

else:
    st.warning("You need to be logged in to see this page! Create a user or sign-in in the Home page")
