import pandas as pd

# Define the file path
file_path = '/Users/aryanraj/Desktop/ML Project/F1FantasyML/MasterData2324.xlsx'  # Replace with your actual file path

# Load data from Excel sheets
fp_df = pd.read_excel(file_path, sheet_name='Fp')
quali_df = pd.read_excel(file_path, sheet_name='Quali')
race_df = pd.read_excel(file_path, sheet_name='Race')
weather_df = pd.read_excel(file_path, sheet_name='Weather')

# Drop the unwanted columns from weather_df
columns_to_drop = ['rain_sprint', 'avg_airtemp_sprint', 'avg_tracktemp_sprint', 'high_windspeed_sprint', 'avg_windspeed_sprint']
weather_df.drop(columns=columns_to_drop, inplace=True)

# Merge DataFrames
# Merge fp_df with weather_df based on 'race_id', 'race_name', and 'season'
combined_df = pd.merge(fp_df, weather_df, on=['race_id', 'race_name', 'season'], how='left')

# Merge combined_df with quali_df based on 'driver_id', 'constructor_id', 'race_id', 'race_name', 'season'
combined_df = pd.merge(combined_df, quali_df, on=['driver_id', 'constructor_id', 'race_id', 'race_name', 'season'], how='left')

# Merge combined_df with race_df based on 'driver_id', 'constructor_id', 'race_id', 'race_name', 'season'
combined_df = pd.merge(combined_df, race_df, on=['driver_id', 'constructor_id', 'race_id', 'race_name', 'season'], how='left')

# Handle missing values if necessary
combined_df.fillna(0, inplace=True)  # Example: Filling missing values with 0

# Write the combined DataFrame to a new CSV file
output_path = '/Users/aryanraj/Desktop/ML Project/F1FantasyML/FINALcombined_f1_data.csv'  # Replace with your desired output path
combined_df.to_csv(output_path, index=False)

print(f"Data has been successfully combined and saved to {output_path}")
