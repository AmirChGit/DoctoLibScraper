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
    Function to scrape addresses from Doctolib profiles.
    
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
        # Skip rows that already have address values
        if not pd.isna(row.get('Address')):
            continue

        link = row['Link']
        print(f"Processing {index + 1}/{len(df)}: {link}")

        try:
            # Open the page
            driver.get(link)
            time.sleep(3)  # Wait for 3 seconds on each page

            # Look for the specific div and spans
            profile_cards = driver.find_elements(By.CLASS_NAME, 'dl-profile-card-content')

            address = []

            for card in profile_cards:
                # Check for the specific h2 element
                h2_elements = card.find_elements(By.TAG_NAME, 'h2')
                for h2 in h2_elements:
                    if h2.get_attribute('class') == 'dl-profile-card-title dl-text dl-text-title dl-text-bold dl-text-s dl-text-neutral-150' and h2.text == "Carte et informations d'accès":
                        # Get the div containing the address
                        address_div = card.find_element(By.CLASS_NAME, 'dl-profile-text')
                        address_text = address_div.text
                        address.append(address_text)

                        # # Scrape all nested divs under the address div
                        # nested_divs = address_div.find_elements(By.TAG_NAME, 'div')
                        # for nested_div in nested_divs:
                        #     address.append(nested_div.text)

            if not address:
                print(f"No address found on page {index + 1}. Skipping this link.")
                continue

            # Combine all address parts into a single string
            full_address = " ".join(address)
            df.at[index, 'Address'] = full_address

            print(f"Scraped address for {link}: {full_address}")

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
