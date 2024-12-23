import streamlit as st
from utils.logic import calculate_moving_time_variation, process_uploaded_file, insert_measurements_to_db, calculate_adaptation_last4weeks, get_last_file_date, get_last_training_date, calculate_intensity_variation, get_last_activities, store_fuelling_data, get_fuelling_data, get_vo2_data, run_etl
import datetime
import pandas as pd
import plotly.express as px

def display_training_comparison():
    with st.container(border=True, height=250):
        st.write("### Did I train more hours?")
        
        # Get the variation data
        variation_data = calculate_moving_time_variation()
        variation = variation_data['week_over_week_variation']
        current_minutes = variation_data['current_week_moving_time']
        
        # Convert minutes to hours and minutes
        hours = int(current_minutes // 60)
        minutes = int(current_minutes % 60)
        time_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        # Determine if training increased
        if variation is not None:
            if variation > 10:
                st.markdown("<h2 style='color: #ffc107;'>Yes, notably</h2>", unsafe_allow_html=True)
                comparison_text = "more"
                variation_color = "#ffc107"  # yellow
            elif variation > 0:
                st.markdown("<h2 style='color: #28a745;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "more"
                variation_color = "#28a745"  # green
            elif variation >= -10:
                st.markdown("<h2 style='color: #ffc107;'>Nearly the same</h2>", unsafe_allow_html=True)
                comparison_text = "less"
                variation_color = "#ffc107"  # yellow
            else:
                st.markdown("<h2 style='color: #dc3545;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "less"
                variation_color = "#dc3545"  # red
            
            # Add the detailed comparison text with colored percentage
            st.write(
                f"You trained {time_text}, "
                f"<span style='color: {variation_color}'>{abs(variation):.1f}%</span> "
                f"{comparison_text} than the last 3-week avg.",
                unsafe_allow_html=True
            )
        else:
            st.write("Not enough data to compare")

def display_distance_comparison():
    with st.container(border=True, height=250):
        st.write("### Did I run further?")
        
        # Get the variation data
        variation_data = calculate_moving_time_variation()
        variation = variation_data['distance_variation']
        current_distance = variation_data['current_week_distance']
        
        # Convert distance to kilometers and format
        distance_text = f"{current_distance:.1f}km"
        
        # Determine if distance increased
        if variation is not None:
            if variation > 10:
                st.markdown("<h2 style='color: #ffc107;'>Yes, notably</h2>", unsafe_allow_html=True)
                comparison_text = "more"
                variation_color = "#ffc107"  # yellow
            elif variation > 0:
                st.markdown("<h2 style='color: #28a745;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "more"
                variation_color = "#28a745"  # green
            elif variation >= -10:
                st.markdown("<h2 style='color: #ffc107;'>Nearly</h2>", unsafe_allow_html=True)
                comparison_text = "less"
                variation_color = "#ffc107"  # yellow
            else:
                st.markdown("<h2 style='color: #dc3545;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "less"
                variation_color = "#dc3545"  # red
            
            # Add the detailed comparison text with colored percentage
            st.write(
                f"You ran {distance_text}, "
                f"<span style='color: {variation_color}'>{abs(variation):.1f}%</span> "
                f"{comparison_text} than the last 3-week avg.",
                unsafe_allow_html=True
            )
        else:
            st.write("Not enough data to compare")      

def display_elevation_comparison():
    with st.container(border=True, height=250):
        st.write("### Did I have more vert?")
        
        # Get the variation data
        variation_data = calculate_moving_time_variation()
        variation = variation_data['elevation_variation']
        current_elevation = variation_data['current_week_elevation']
        
        # Convert distance to kilometers and format
        elevation_text = f"{current_elevation:.0f}m"
        
        # Determine if distance increased
        if variation is not None:
            if variation > 10:
                st.markdown("<h2 style='color: #ffc107;'>Yes, notably</h2>", unsafe_allow_html=True)
                comparison_text = "more"
                variation_color = "#ffc107"  # yellow
            elif variation > 0:
                st.markdown("<h2 style='color: #28a745;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "more"
                variation_color = "#28a745"  # green
            elif variation >= -10:
                st.markdown("<h2 style='color: #28a745;'>Nearly</h2>", unsafe_allow_html=True)
                comparison_text = "less"
                variation_color = "#28a745"  # green
            else:
                st.markdown("<h2 style='color: #dc3545;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "less"
                variation_color = "#dc3545"  # red
            
            # Add the detailed comparison text with colored percentage
            st.write(
                f"You had {elevation_text} of vert, "
                f"<span style='color: {variation_color}'>{abs(variation):.1f}%</span> "
                f"{comparison_text} than the last 3-week avg.",
                unsafe_allow_html=True
            )
        else:
            st.write("Not enough data to compare") 

def display_hrv_score_comparison():
    with st.container(border=True, height=250):
        st.write("### Is my HRV score better?")

        adaptation_data = calculate_adaptation_last4weeks()
        current_week_hrv = adaptation_data['current_week_hrv']
        hrv_variation = adaptation_data['hrv_variation']

        if hrv_variation is not None:
            if hrv_variation > 0:
                st.markdown("<h2 style='color: #28a745;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "above"
                variation_color = "#28a745"  # green
            else:
                st.markdown("<h2 style='color: #dc3545;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "below"
                variation_color = "#dc3545"  # red
            
            # Add the detailed comparison text with colored percentage
            st.write(
                f"Your avg HRV score was {current_week_hrv }, "
                f"<span style='color: {variation_color}'>{abs(hrv_variation):.1f}%</span> "
                f"{comparison_text} last 3-week avg.",
                unsafe_allow_html=True
            )
        else:
            st.write("Not enough data to compare")

def display_sleep_quality_comparison():
    with st.container(border=True, height=250):
        st.write("### Is my sleep quality better?")

        adaptation_data = calculate_adaptation_last4weeks()
        current_week_sleep_quality = adaptation_data['current_week_sleep_quality']
        sleep_quality_variation = adaptation_data['sleep_quality_variation']

        if sleep_quality_variation is not None:
            if sleep_quality_variation > 0:
                st.markdown("<h2 style='color: #28a745;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "above"
                variation_color = "#28a745"  # green
            else:
                st.markdown("<h2 style='color: #dc3545;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "below"
                variation_color = "#dc3545"  # red
            
            st.write(
                f"Your avg sleep quality was "
                f"<span style='color: {variation_color}'>{abs(sleep_quality_variation):.1f}%</span> "
                f"{comparison_text} last 3-week avg.",
                unsafe_allow_html=True
            )
        else:
            st.write("Not enough data to compare")

def display_fatigue_comparison():
    with st.container(border=True, height=250):
        st.write("### Is my fatigue level higher?")

        adaptation_data = calculate_adaptation_last4weeks()
        current_week_fatigue = adaptation_data['current_week_fatigue']
        fatigue_variation = adaptation_data['fatigue_variation']

        if fatigue_variation is not None:
            if fatigue_variation < 0:  # Note: Lower fatigue is better, so logic is inverted
                st.markdown("<h2 style='color: #28a745;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "below"
                variation_color = "#28a745"  # green
            else:
                st.markdown("<h2 style='color: #dc3545;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "above"
                variation_color = "#dc3545"  # red
            
            st.write(
                f"Your avg fatigue level was "
                f"<span style='color: {variation_color}'>{abs(fatigue_variation):.1f}%</span> "
                f"{comparison_text} last 3-week avg.",
                unsafe_allow_html=True
            )
        else:
            st.write("Not enough data to compare")

def display_mental_energy_comparison():
    with st.container(border=True, height=250):
        st.write("### Is my mental energy better?")

        adaptation_data = calculate_adaptation_last4weeks()
        current_week_mental_energy = adaptation_data['current_week_mental_energy']
        mental_energy_variation = adaptation_data['mental_energy_variation']

        if mental_energy_variation is not None:
            if mental_energy_variation > 0:
                st.markdown("<h2 style='color: #28a745;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "above"
                variation_color = "#28a745"  # green
            else:
                st.markdown("<h2 style='color: #dc3545;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "below"
                variation_color = "#dc3545"  # red
            
            st.write(
                f"Your avg mental energy was "
                f"<span style='color: {variation_color}'>{abs(mental_energy_variation):.1f}%</span> "
                f"{comparison_text} last 3-week avg.",
                unsafe_allow_html=True
            )
        else:
            st.write("Not enough data to compare")

def display_intense_days_comparison():
    with st.container(border=True, height=250):
        st.write("### Did I have more hard days?")

        intensity_data = calculate_intensity_variation()
        current_week_days = intensity_data['current_week_days']
        days_variation = intensity_data['week_over_week_variation']

        if days_variation is not None:
            if days_variation == 0:
                st.markdown("<h2 style='color: #28a745;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "same"
                variation_color = "#28a745"  # green

                st.write(
                    f"You had {current_week_days} hard day(s), "
                    f"{comparison_text} as last week.",
                    unsafe_allow_html=True
                )

            elif days_variation > 0:
                st.markdown("<h2 style='color: #ffc107;'>Yes</h2>", unsafe_allow_html=True)
                comparison_text = "more"
                variation_color = "#ffc107"  # yellow

                st.write(
                    f"You had {current_week_days} hard day(s), "
                    f"<span style='color: {variation_color}'>{abs(days_variation)} </span>"
                    f"{comparison_text} than last week.",
                    unsafe_allow_html=True
                )

            else:
                st.markdown("<h2 style='color: #ffc107;'>No</h2>", unsafe_allow_html=True)
                comparison_text = "less"
                variation_color = "#ffc107"  # yellow

                st.write(
                    f"You had {current_week_days} hard day(s), "
                    f"<span style='color: {variation_color}'>{abs(days_variation)} </span>"
                    f"{comparison_text} than last week.",
                    unsafe_allow_html=True
                )
            
        else:
            st.write("Not enough data to compare")

def display_current_week():
    # Calculate current week start and end dates
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + datetime.timedelta(days=6)  # Sunday
    st.write(f"Showing period from **{start_of_week}** to **{end_of_week}**")  # Display week dates


if __name__ == "__main__":

    if st.session_state.user != None:
        st.set_page_config(page_title="Cami App", layout='wide', initial_sidebar_state='collapsed')
        
        st.title("Weekly Training Indicators:runner::bar_chart:")
        run_etl()
        display_current_week()
        st.write("")
        
        st.subheader("Volume")
        last_training_data = get_last_training_date()
        last_training_upload_date = last_training_data['formatted_date']
        st.caption(f"Last update: {last_training_upload_date}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            display_training_comparison()
        with col2:
            display_distance_comparison()
        with col3:
            display_elevation_comparison()

        st.divider()

        st.subheader("Intensity")
        last_file_data = get_last_file_date()
        last_file_upload_date = last_file_data['formatted_date']
        st.caption(f"Last update: {last_file_upload_date}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            display_intense_days_comparison()
        
        st.divider()
        
        st.subheader("Adaptation")
        st.caption(f"Last update: {last_file_upload_date}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            display_hrv_score_comparison()
        with col2:
            display_sleep_quality_comparison()
        with col3:
            display_fatigue_comparison()
        with col4:
            display_mental_energy_comparison()
    else:
        st.warning("You need to be logged in to see this page! Create a user or sign-in in the Home page")
        
