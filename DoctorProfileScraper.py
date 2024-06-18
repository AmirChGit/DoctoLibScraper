import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Define the name of the Excel file
file_name = "ergotherapeute_france.xlsx"
file_path = f"./{file_name}"  # Assuming the file is in the same directory as this script

def scrape_profile(file_path):
    """
    Function to scrape consultation types and fees from Doctolib profiles.
    
    Parameters:
        file_path (str): The path to the Excel file containing Doctolib profile links.
    """
    # Load the Excel file
    df = pd.read_excel(file_path)
    print(f"Loaded Excel file: {file_path}")

    # Set up the Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)
    print("WebDriver initialized.")

    # Loop through each link in the DataFrame
    for index, row in df.iterrows():
        # Skip rows that already have consultation type and fee values
        if not (pd.isna(row.get('Consultation_Type_1')) and pd.isna(row.get('Consultation_Fee_1'))):
            continue

        link = row['Link']
        print(f"Processing {index + 1}/{len(df)}: {link}")

        try:
            # Open the page
            driver.get(link)
            time.sleep(3)  # Wait for 3 seconds on each page

            # Look for the specific div and spans
            profile_cards = driver.find_elements(By.CLASS_NAME, 'dl-profile-card-content')

            types = []
            fees = []

            for card in profile_cards:
                ul_elements = card.find_elements(By.TAG_NAME, 'ul')
                for ul in ul_elements:
                    li_elements = ul.find_elements(By.CLASS_NAME, 'list-none')
                    for li in li_elements:
                        fee_names = li.find_elements(By.CLASS_NAME, 'dl-profile-fee-name')
                        fee_tags = li.find_elements(By.CLASS_NAME, 'dl-profile-fee-tag')

                        for name, tag in zip(fee_names, fee_tags):
                            types.append(name.text)
                            fees.append(tag.text)

            if not types and not fees:
                print(f"No data found on page {index + 1}. Skipping this link.")
                continue

            # Ensure equal length by padding with empty strings if necessary
            max_length = max(len(types), len(fees))
            types.extend([''] * (max_length - len(types)))
            fees.extend([''] * (max_length - len(fees)))

            # Add the pairs to the DataFrame with explicit type casting to str
            for i in range(len(types)):
                column_name_type = f"Consultation_Type_{i+1}"
                column_name_fee = f"Consultation_Fee_{i+1}"
                if column_name_type not in df.columns:
                    df[column_name_type] = [''] * len(df)
                if column_name_fee not in df.columns:
                    df[column_name_fee] = [''] * len(df)
                df.at[index, column_name_type] = str(types[i])
                df.at[index, column_name_fee] = str(fees[i])

            print(f"Scraped data for {link}: {types}, {fees}")

        except Exception as e:
            print(f"Error processing {link}: {e}")
            time.sleep(5)

        # Save the updated DataFrame to a new Excel file after each page
        df.to_excel(file_path, index=False)
        print(f"Data saved to Excel file: {file_path}")

    # Close the WebDriver
    driver.quit()
    print("WebDriver closed.")
    print(f"Updated Excel file saved to {file_path}")

if __name__ == "__main__":
    # Directly calling the scrape_profile function with the specified file path
    scrape_profile(file_path)
