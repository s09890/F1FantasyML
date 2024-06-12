import fastf1
import pandas as pd

# Define the list of drivers on the 2024 grid (using abbreviations)
drivers_2024_grid = [
    'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA', 
    'ALO', 'OCO', 'GAS', 'TSU', 'ALB', 'SAR', 'HUL', 'MAG', 
    'STR', 'RIC', 'BOT', 'ZHO'
]

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
        qualifying = event.get_session('Qualifying')

        # Load qualifying results
        qualifying.load()
        drivers = qualifying.results[['DriverNumber', 'DriverId', 'TeamId', 'Abbreviation', 'Position', 'Q1', 'Q2', 'Q3']]
        
        # Filter to include only drivers on the 2024 grid
        drivers = drivers[drivers['Abbreviation'].isin(drivers_2024_grid)]

        # Determine the correct qualifying time for each driver based on their position
        drivers['qual_time'] = drivers.apply(lambda row: row['Q3'] if row['Position'] <= 10 else (row['Q2'] if row['Position'] <= 15 else row['Q1']), axis=1)

        # Create a DataFrame with the extracted data
        data = {
            'driver_id': drivers['DriverId'],
            'constructor_id': drivers['TeamId'],
            'race_id': [round_number] * len(drivers),
            'race_name': [race_name] * len(drivers),
            'season': [year] * len(drivers),
            'qual_position': drivers['Position'],
            'qual_time': drivers['qual_time'],
        }
        
        df = pd.DataFrame(data)
        all_data.append(df)

    except Exception as e:
        print(f"Error processing year {year}, round {round_number}: {e}")

# Concatenate all DataFrames into one
all_data_df = pd.concat(all_data, ignore_index=True)

# Save the DataFrame to a CSV file
all_data_df.to_csv('f1_qualifying_data_2021.csv', index=False)

print("Data saved to 'f1_qualifying_data_2021.csv'")
