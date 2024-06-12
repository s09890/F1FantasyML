import fastf1
import pandas as pd

# Define the list of drivers on the 2024 grid (using abbreviations)
drivers_2024_grid = [
    'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA', 
    'ALO', 'OCO', 'GAS', 'TSU', 'ALB', 'SAR', 'HUL', 'MAG', 
    'STR', 'RIC', 'BOT', 'ZHO'
]

# Define a function to calculate the best and average lap times for each driver, filtering out slow laps
def calculate_driver_lap_times(session):
    session.load()
    laps = session.laps
    
    # Get the best lap time from the fastest driver in the session
    fastest_lap = laps.pick_fastest()
    threshold_time = fastest_lap['LapTime'] * 1.05
    
    drivers = laps['Driver'].unique()
    driver_data = []
    
    for driver in drivers:
        if driver not in drivers_2024_grid:
            continue
        driver_laps = laps.pick_driver(driver)
        # Filter laps to only include those within 105% of the best lap time
        fast_laps = driver_laps[driver_laps['LapTime'] <= threshold_time]
        if not fast_laps.empty:
            best_time = fast_laps['LapTime'].min()
            avg_time = fast_laps['LapTime'].mean()
        else:
            best_time = pd.NaT
            avg_time = pd.NaT
        driver_data.append((driver, best_time, avg_time))
    
    return pd.DataFrame(driver_data, columns=['Driver', 'BestTime', 'AvgTime'])

# Initialize an empty list to store data for all races
all_data = []

# Loop through each round of the 2021 season
year = 2021
schedule = fastf1.get_event_schedule(year)
rounds = schedule['RoundNumber'].dropna().unique().astype(int)

for round_number in rounds:
    try:
        event = fastf1.get_event(year, round_number)
        race_name = event['EventName']
        race = event.get_race()
        fp1 = event.get_session('Practice 1')
        fp2 = event.get_session('Practice 2')
        fp3 = event.get_session('Practice 3')

        # Calculate lap times for each practice session
        fp1_times = calculate_driver_lap_times(fp1)
        fp2_times = calculate_driver_lap_times(fp2)
        fp3_times = calculate_driver_lap_times(fp3)
        
        # Load race results to get driver and constructor information
        race.load()
        drivers = race.results[['DriverNumber', 'DriverId', 'TeamId', 'Abbreviation']]
        
        # Merge practice session times with driver information
        fp1_times = fp1_times.rename(columns={'BestTime': 'fp1_best_time', 'AvgTime': 'fp1_avg_time'})
        fp2_times = fp2_times.rename(columns={'BestTime': 'fp2_best_time', 'AvgTime': 'fp2_avg_time'})
        fp3_times = fp3_times.rename(columns={'BestTime': 'fp3_best_time', 'AvgTime': 'fp3_avg_time'})
        
        driver_info = drivers.merge(fp1_times, left_on='Abbreviation', right_on='Driver', how='left') \
                             .merge(fp2_times, left_on='Abbreviation', right_on='Driver', how='left') \
                             .merge(fp3_times, left_on='Abbreviation', right_on='Driver', how='left')
        
        # Filter to include only drivers on the 2024 grid
        driver_info = driver_info[driver_info['Abbreviation'].isin(drivers_2024_grid)]
        
        # Create a DataFrame with the extracted data
        data = {
            'driver_id': driver_info['DriverId'],
            'constructor_id': driver_info['TeamId'],
            'race_id': [round_number] * len(driver_info),
            'race_name': [race_name] * len(driver_info),
            'season': [year] * len(driver_info),
            'fp1_best_time': driver_info['fp1_best_time'],
            'fp2_best_time': driver_info['fp2_best_time'],
            'fp3_best_time': driver_info['fp3_best_time'],
            'fp1_avg_time': driver_info['fp1_avg_time'],
            'fp2_avg_time': driver_info['fp2_avg_time'],
            'fp3_avg_time': driver_info['fp3_avg_time'],
        }
        
        df = pd.DataFrame(data)
        all_data.append(df)

    except Exception as e:
        print(f"Error processing year {year}, round {round_number}: {e}")

# Concatenate all DataFrames into one
all_data_df = pd.concat(all_data, ignore_index=True)

# Save the DataFrame to a CSV file
all_data_df.to_csv('f1_session_data_2021.csv', index=False)

print("Data saved to 'f1_session_data_2021.csv'")
