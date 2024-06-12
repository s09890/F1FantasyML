import fastf1
import pandas as pd

# Define the list of drivers on the 2024 grid (using abbreviations)
drivers_2024_grid = [
    'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA', 
    'ALO', 'OCO', 'GAS', 'TSU', 'ALB', 'SAR', 'HUL', 'MAG', 
    'STR', 'RIC', 'BOT', 'ZHO'
]

# Initialize an empty list to store data for all rounds with sprints
all_data = []

# Specify the year
year = 2021

# Get the event schedule for the year
schedule = fastf1.get_event_schedule(year)

# Loop through each round in the schedule
for round_number in schedule['RoundNumber'].dropna().unique().astype(int):
    try:
        event = fastf1.get_event(year, round_number)
        race_name = event['EventName']
        
        # Check if the event has a sprint session
        try:
            sprint = event.get_session('Sprint')
        except Exception as e:
            print(f"No sprint session for round {round_number}: {e}")
            continue

        # Load sprint data
        sprint.load()

        # Get sprint start and end positions
        sprint_results = sprint.results[['DriverNumber', 'DriverId', 'TeamId', 'Abbreviation', 'Position', 'GridPosition', 'Status']].copy()
        sprint_results.rename(columns={'Position': 'sprint_endposition', 'GridPosition': 'sprint_startposition'}, inplace=True)
        
        # Determine DNF status from the sprint session
        sprint_results['dnf'] = sprint_results['Status'].apply(lambda x: 1 if x != 'Finished' else 0)

        # Calculate overtakes made during the sprint
        overtakes = {driver: 0 for driver in drivers_2024_grid}
        laps = sprint.laps

        for driver in drivers_2024_grid:
            driver_laps = laps.pick_driver(driver)
            for i in range(1, len(driver_laps)):
                if driver_laps.iloc[i]['Position'] < driver_laps.iloc[i - 1]['Position']:
                    overtakes[driver] += 1

        sprint_results['overtakes_made'] = sprint_results['Abbreviation'].map(overtakes)

        # Filter to include only drivers on the 2024 grid
        sprint_results = sprint_results[sprint_results['Abbreviation'].isin(drivers_2024_grid)]

        # Create a DataFrame with the extracted data
        data = {
            'driver_id': sprint_results['DriverId'],
            'constructor_id': sprint_results['TeamId'],
            'race_id': [round_number] * len(sprint_results),
            'race_name': [race_name] * len(sprint_results),
            'season': [year] * len(sprint_results),
            'sprint_startposition': sprint_results['sprint_startposition'],
            'sprint_endposition': sprint_results['sprint_endposition'],
            'overtakes_made': sprint_results['overtakes_made'],
            'dnf': sprint_results['dnf']
        }

        df = pd.DataFrame(data)
        all_data.append(df)

    except Exception as e:
        print(f"Error processing year {year}, round {round_number}: {e}")

# Concatenate all DataFrames into one
if all_data:
    all_data_df = pd.concat(all_data, ignore_index=True)
    # Save the DataFrame to a CSV file
    all_data_df.to_csv('f1_sprint_data_2021.csv', index=False)
    print("Data saved to 'f1_sprint_data_2021.csv'")
else:
    print("No data to save")
