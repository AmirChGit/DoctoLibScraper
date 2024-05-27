import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys

def scrape_profile(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Set up the Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Initialize lists to store the scraped data
    consultation_types = []
    consultation_fees = []

    # Identify the starting point based on existing data
    start_index = 0
    empty_pages = 0
    max_empty_pages = 10
    
    # Loop through each link in the DataFrame starting from the identified index
    for index, row in df.iterrows():
        if not (pd.isna(row['Consultation_Type_1']) and pd.isna(row['Consultation_Fee_1'])):
            continue  # Skip rows that already have consultation type and fee values

        link = row['Link']
        print(f"Processing {index + 1}/{len(df)}: {link}")
        try:
            # Open the page
            driver.get(link)
            time.sleep(3)  # Wait for 3 seconds on each page

            # Look for the specific div and spans
            fee_divs = driver.find_elements(By.CLASS_NAME, 'dl-profile-card-content')
            
            types = []
            fees = []
            
            for fee_div in fee_divs:
                fee_names = fee_div.find_elements(By.CLASS_NAME, 'dl-profile-fee-name')
                fee_tags = fee_div.find_elements(By.CLASS_NAME, 'dl-profile-fee-tag')
                
                for name, tag in zip(fee_names, fee_tags):
                    types.append(name.text)
                    fees.append(tag.text)

            if not types and not fees:
                empty_pages += 1
                print(f"No data found on page {index + 1}. Empty page count: {empty_pages}")
                if empty_pages >= max_empty_pages:
                    print(f"Found {max_empty_pages} empty pages in a row. Stopping the scraper.")
                    break
            else:
                empty_pages = 0

            # Ensure equal length by padding with empty strings if necessary
            max_length = max(len(types), len(fees))
            types.extend([''] * (max_length - len(types)))
            fees.extend([''] * (max_length - len(fees)))
            
            consultation_types.append(types)
            consultation_fees.append(fees)
            
            # Add the pairs to the DataFrame
            for i in range(len(types)):
                column_name_type = f"Consultation_Type_{i+1}"
                column_name_fee = f"Consultation_Fee_{i+1}"
                if column_name_type not in df.columns:
                    df[column_name_type] = [''] * len(df)
                if column_name_fee not in df.columns:
                    df[column_name_fee] = [''] * len(df)
                df.at[index, column_name_type] = types[i]
                df.at[index, column_name_fee] = fees[i]

        except Exception as e:
            print(f"Error processing {link}: {e}")
            consultation_types.append([])
            consultation_fees.append([])
            time.sleep(5)  # Retry after 5 seconds

        # Save the updated DataFrame to a new Excel file after each page
        df.to_excel(file_path, index=False)

    # Close the WebDriver
    driver.quit()

    print(f"Updated Excel file saved to {file_path}")

if __name__ == "__main__":
    file_path = sys.argv[1]
    scrape_profile(file_path)
