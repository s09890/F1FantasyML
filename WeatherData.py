import fastf1
import pandas as pd

# Function to calculate weather statistics for a session
def calculate_weather_stats(session):
    session.load(weather=True)
    weather_data = session.weather_data

    # Filter weather data every 10 data points
    weather_sampled = weather_data.iloc[::10, :]

    # Calculate statistics
    avg_airtemp = weather_sampled['AirTemp'].mean()
    avg_tracktemp = weather_sampled['TrackTemp'].mean()
    high_windspeed = weather_sampled['WindSpeed'].max()
    avg_windspeed = weather_sampled['WindSpeed'].mean()
    rain = 1 if weather_sampled['Rainfall'].any() else 0

    return rain, avg_airtemp, avg_tracktemp, high_windspeed, avg_windspeed

# Initialize an empty list to store data for all rounds
all_data = []

# Specify the year
year = 2021

# Loop through all rounds of the 2021 season
for round_number in range(1, 23):  # 22 rounds in the 2021 season
    try:
        event = fastf1.get_event(year, round_number)
        race_name = event['EventName']

        # Initialize dictionary to store weather data
        weather_stats = {
            'race_id': round_number,
            'race_name': race_name,
            'season': year,
            'rain_fp1': None, 'avg_airtemp_fp1': None, 'avg_tracktemp_fp1': None, 'high_windspeed_fp1': None, 'avg_windspeed_fp1': None,
            'rain_fp2': None, 'avg_airtemp_fp2': None, 'avg_tracktemp_fp2': None, 'high_windspeed_fp2': None, 'avg_windspeed_fp2': None,
            'rain_fp3': None, 'avg_airtemp_fp3': None, 'avg_tracktemp_fp3': None, 'high_windspeed_fp3': None, 'avg_windspeed_fp3': None,
            'rain_quali': None, 'avg_airtemp_quali': None, 'avg_tracktemp_quali': None, 'high_windspeed_quali': None, 'avg_windspeed_quali': None,
            'rain_race': None, 'avg_airtemp_race': None, 'avg_tracktemp_race': None, 'high_windspeed_race': None, 'avg_windspeed_race': None,
            'rain_sprint': None, 'avg_airtemp_sprint': None, 'avg_tracktemp_sprint': None, 'high_windspeed_sprint': None, 'avg_windspeed_sprint': None,
        }

        # Get sessions and calculate weather stats
        sessions = {
            'FP1': 'fp1',
            'FP2': 'fp2',
            'FP3': 'fp3',
            'Q': 'quali',
            'R': 'race',
            'S': 'sprint'  # Sprint session if available
        }

        for session_name, stat_prefix in sessions.items():
            try:
                session = event.get_session(session_name)
                stats = calculate_weather_stats(session)
                weather_stats[f'rain_{stat_prefix}'], weather_stats[f'avg_airtemp_{stat_prefix}'], weather_stats[f'avg_tracktemp_{stat_prefix}'], \
                weather_stats[f'high_windspeed_{stat_prefix}'], weather_stats[f'avg_windspeed_{stat_prefix}'] = stats
            except Exception as e:
                print(f"Could not process session {session_name} for round {round_number}: {e}")

        # Append the data for the current round
        all_data.append(weather_stats)

    except Exception as e:
        print(f"Error processing year {year}, round {round_number}: {e}")

# Convert the list of dictionaries to a DataFrame
all_data_df = pd.DataFrame(all_data)

# Save the DataFrame to a CSV file
all_data_df.to_csv('f1_weather_data_2021.csv', index=False)
print("Data saved to 'f1_weather_data_2021.csv'")
