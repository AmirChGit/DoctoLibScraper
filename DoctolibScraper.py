import os
import time
import pandas as pd
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Function to initialize the webdriver
def init_driver():
    options = Options()
    # Comment out the next line to see the browser
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

# Function to scrape data from a single page
def scrape_page(driver):
    print("Scraping page...")
    links = []
    names = []

    try:
        # Wait for the elements to load
        wait = WebDriverWait(driver, 10)
        doctor_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'dl-flex-row.dl-justify-between.dl-align-items-start')))
    except Exception as e:
        print(f"Error finding doctor elements: {e}")
        return links, names

    for element in doctor_elements:
        try:
            link_element = element.find_element(By.CSS_SELECTOR, 'a.dl-p-doctor-result-link.dl-full-width.dl-flex-center')
            name_element = element.find_element(By.CSS_SELECTOR, 'div.dl-layout-item.dl-layout-size-xs-12 h2.dl-text.dl-text-body.dl-text-bold.dl-text-s.dl-text-primary-110')

            link = link_element.get_attribute('href')
            name = name_element.text

            links.append(link)
            names.append(name)
        except Exception as e:
            print(f"Error extracting data from element: {e}")

    return links, names

# Main function to orchestrate the scraping
def main():
    # Get user inputs from terminal
    docteur = input("Please enter the type of doctor (e.g., psychologue): ").lower()
    localisation = input("Please enter the location (e.g., france): ").lower()
    
    print(f"User input received - Docteur: {docteur}, Localisation: {localisation}")
    base_url = f'https://www.doctolib.fr/{docteur}/{localisation}?page='
    driver = init_driver()
    print("WebDriver initialized.")
    page_number = 1
    empty_page_count = 0
    max_empty_pages = 2

    all_links = []
    all_names = []

    # Check if the file already exists
    file_name = f'{docteur}_{localisation}.xlsx'.replace(' ', '_')
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        all_links = df['Link'].tolist()
        all_names = df['Name'].tolist()
        page_number = (len(all_links) // 20) + 1  # Assuming each page has 10 entries, adjust if different
        print(f"Resuming from page {page_number}")
    else:
        df = pd.DataFrame(columns=['Name', 'Link'])

    while empty_page_count < max_empty_pages:
        url = base_url + str(page_number)
        print(f"Opening URL: {url}")
        driver.get(url)

        time.sleep(2)  # Ensure at least 2 seconds spent on the page

        try:
            links, names = scrape_page(driver)
            if not links and not names:
                empty_page_count += 1
                print(f"No data found on page {page_number}. Empty page count: {empty_page_count}")
            else:
                empty_page_count = 0
                all_links.extend(links)
                all_names.extend(names)
                print(f"Found {len(links)} links and {len(names)} names on this page.")
                
                # Append new data to the DataFrame
                new_data = pd.DataFrame({'Name': names, 'Link': links})
                df = pd.concat([df, new_data], ignore_index=True)

                # Save the results to an Excel file after each page
                df.to_excel(file_name, index=False)
                print(f'Data has been saved to {file_name}')

        except Exception as e:
            print(f"Error scraping page: {e}")

        # Increment the page number and wait before moving to the next page
        page_number += 1
        time.sleep(3)  # Wait for 3 seconds before moving to the next page

    driver.quit()
    print('Scraping completed.')

    # Call the DoctorProfileScraper.py script with the generated file name
    subprocess.run(['python', 'DoctorProfileScraper.py', file_name])

if __name__ == "__main__":
    main()
