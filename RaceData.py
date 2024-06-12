import fastf1
import pandas as pd

# Define the list of drivers on the 2024 grid (using abbreviations)
drivers_2024_grid = [
    'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA', 
    'ALO', 'OCO', 'GAS', 'TSU', 'ALB', 'SAR', 'HUL', 'MAG', 
    'STR', 'RIC', 'BOT', 'ZHO'
]

# Initialize an empty list to store data for all rounds
all_data = []

# Specify the year
year = 2021

# Loop through all rounds of the 2021 season
for round_number in range(1, 23):  # 22 rounds in the 2021 season
    try:
        event = fastf1.get_event(year, round_number)
        race_name = event['EventName']
        race = event.get_race()

        # Load race data
        race.load()

        # Get race start and end positions
        race_results = race.results[['DriverNumber', 'DriverId', 'TeamId', 'Abbreviation', 'Position', 'GridPosition']].copy()
        race_results.rename(columns={'Position': 'race_endposition', 'GridPosition': 'race_startposition'}, inplace=True)

        # Update start position from 0 to 20 if necessary
        race_results['race_startposition'] = race_results['race_startposition'].replace(0, 20)

        # Calculate overtakes made during the race
        overtakes = {driver: 0 for driver in drivers_2024_grid}
        laps = race.laps

        for driver in drivers_2024_grid:
            driver_laps = laps.pick_driver(driver)
            for i in range(1, len(driver_laps)):
                if driver_laps.iloc[i]['Position'] < driver_laps.iloc[i - 1]['Position']:
                    overtakes[driver] += 1

        race_results['race_overtakes_made'] = race_results['Abbreviation'].map(overtakes)

        # Find the fastest lap of the race
        fastest_lap_time = pd.Timedelta.max
        fastest_driver = None

        for driver in drivers_2024_grid:
            driver_laps = laps.pick_driver(driver)
            if not driver_laps.empty:
                driver_fastest_lap = driver_laps.pick_fastest()
                if driver_fastest_lap is not None and isinstance(driver_fastest_lap['LapTime'], pd.Timedelta) and driver_fastest_lap['LapTime'] < fastest_lap_time:
                    fastest_lap_time = driver_fastest_lap['LapTime']
                    fastest_driver = driver

        # Assign 1 to the driver who set the fastest lap and 0 to others
        race_results['fastest_lap'] = race_results['Abbreviation'].apply(lambda x: 1 if x == fastest_driver else 0)

        # Filter to include only drivers on the 2024 grid
        race_results = race_results[race_results['Abbreviation'].isin(drivers_2024_grid)]

        # Create a DataFrame with the extracted data
        data = {
            'driver_id': race_results['DriverId'],
            'constructor_id': race_results['TeamId'],
            'race_id': [round_number] * len(race_results),
            'race_name': [race_name] * len(race_results),
            'season': [year] * len(race_results),
            'race_startposition': race_results['race_startposition'],
            'race_endposition': race_results['race_endposition'],
            'race_overtakes_made': race_results['race_overtakes_made'],
            'fastest_lap': race_results['fastest_lap']
        }

        df = pd.DataFrame(data)
        all_data.append(df)

    except Exception as e:
        print(f"Error processing year {year}, round {round_number}: {e}")

# Concatenate all DataFrames into one
if all_data:
    all_data_df = pd.concat(all_data, ignore_index=True)
    # Save the DataFrame to a CSV file
    all_data_df.to_csv('f1_race_data_2021.csv', index=False)
    print("Data saved to 'f1_race_data_2021.csv'")
else:
    print("No data to save")
