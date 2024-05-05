from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Setup webdriver
s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)

# Navigate to the webpage
driver.get('https://coincodex.com/historical-data/crypto/?date=2024-04-01T17:00:00Z')

# Wait for the JavaScript to load the table
driver.implicitly_wait(10)

# Find the table
table = driver.find_element(By.TAG_NAME, 'table')

# Extract the table rows
rows = table.find_elements(By.TAG_NAME, 'tr')

# Extract data from each row
for row in rows:
    cols = row.find_elements(By.TAG_NAME, 'td')
    for col in cols:
        print(col.text)

# Close the driver
driver.quit()


# wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
# echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
# sudo apt-get update
# sudo apt-get install google-chrome-stable

