import csv
from datetime import datetime

# Function to filter data from a given date onwards
def filter_data_from_date(file_path, start_date):
    with open(file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        filtered_rows = [row for row in reader if datetime.strptime(row['date'], '%Y-%m-%d') >= start_date]
        return filtered_rows

# Function to write data to a new CSV file
def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# Read data from the file starting from 2011-01-01 onwards
start_date = datetime(2014, 1, 1)
filtered_data = filter_data_from_date('crypto_data.csv', start_date)

# Write filtered data to a new CSV file
write_to_csv(filtered_data, 'filtered_crypto_data.csv')
