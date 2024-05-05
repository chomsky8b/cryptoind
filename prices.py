import numpy as np

def simulate_price_movement(start_price, high_volume_levels, steps):
    prices = [start_price]
    current_level_index = 0  # Start at the first high volume level
    value_area = high_volume_levels[current_level_index]['value_area']
    point_of_control = high_volume_levels[current_level_index]['point_of_control']
    
    for _ in range(steps):
        # Simulate jump to the next high volume level
        current_level_index = (current_level_index + 1) % len(high_volume_levels)
        new_price = high_volume_levels[current_level_index]['point_of_control']
        
        # Simulate rotation within value area
        for _ in range(np.random.randint(5, 20)):  # Simulate 5 to 20 rotations
            new_price += np.random.uniform(-0.5, 0.5) * np.std(value_area)
            new_price = round(new_price, 2)
            prices.append(new_price)
            
    return prices

# Example usage
start_price = 510  # Starting price
high_volume_levels = [
    {'value_area': range(495, 530), 'point_of_control': 515},
    {'value_area': range(430, 470), 'point_of_control': 450},
    # Add more high volume levels as needed
]
steps = 1000  # Number of steps to simulate

simulated_prices = simulate_price_movement(start_price, high_volume_levels, steps)

#simulated_prices = simulate_price_movement(start_price, high_volume_levels, steps)

print(simulated_prices)

import csv

# Define the filename for the CSV file
filename = "simulated_prices.csv"

# Write the simulated prices to the CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    for price in simulated_prices:
        writer.writerow([price])

