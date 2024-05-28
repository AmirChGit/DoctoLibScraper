import os
import sys
from telnetlib import EC
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

def init_driver():
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_page(driver):
    print("Scraping page...")
    links = []
    names = []

    try:
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

def scrape_profiles(file_path):
    df = pd.read_excel(file_path)

    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)

    start_index = 0
    empty_pages = 0
    max_empty_pages = 100
    
    for index, row in df.iterrows():
        if pd.isna(row.get('Consultation_Type_1')) and pd.isna(row.get('Consultation_Fee_1')):
            start_index = index
            break

    for index, row in df.iterrows():
        if index < start_index:
            continue
        if not (pd.isna(row.get('Consultation_Type_1')) and pd.isna(row.get('Consultation_Fee_1'))):
            print(f"Skipping row {index + 1} as it already has consultation data.")
            continue

        link = row['Link']
        print(f"Processing {index + 1}/{len(df)}: {link}")
        try:
            driver.get(link)
            time.sleep(3)

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

            max_length = max(len(types), len(fees))
            types.extend([''] * (max_length - len(types)))
            fees.extend([''] * (max_length - len(fees)))
            
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
            time.sleep(5)

        df.to_excel(file_path, index=False)

    driver.quit()

    print(f"Updated Excel file saved to {file_path}")

def main():
    docteur = input("Please enter the type of doctor (e.g., psychologue): ").lower()
    localisation = input("Please enter the location (e.g., france): ").lower()
    
    print(f"User input received - Docteur: {docteur}, Localisation: {localisation}")
    base_url = f'https://www.doctolib.fr/{docteur}/{localisation}?page='
    driver = init_driver()
    print("WebDriver initialized.")
    page_number = 1
    empty_page_count = 0
    max_empty_pages = 3

    all_links = []
    all_names = []

    file_name = f'{docteur}_{localisation}.xlsx'.replace(' ', '_')
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        all_links = df['Link'].tolist()
        all_names = df['Name'].tolist()
        page_number = (len(all_links) // 20) + 1
        print(f"Resuming from page {page_number}")
    else:
        df = pd.DataFrame(columns=['Name', 'Link'])

    while empty_page_count < max_empty_pages:
        url = base_url + str(page_number)
        print(f"Opening URL: {url}")
        driver.get(url)

        time.sleep(2)

        try:
            links, names = scrape_page(driver)
            if not links and not names:
                empty_page_count += 1
                print(f"No data found on page {page_number}. Empty page count: {empty_page_count}")
                if empty_page_count >= max_empty_pages:
                    print(f"Found {max_empty_pages} empty pages in a row. Stopping the scraper.")
                    break
            else:
                empty_page_count = 0
                all_links.extend(links)
                all_names.extend(names)
                print(f"Found {len(links)} links and {len(names)} names on this page.")
                
                new_data = pd.DataFrame({'Name': names, 'Link': links})
                df = pd.concat([df, new_data], ignore_index=True)

                df.to_excel(file_name, index=False)
                print(f'Data has been saved to {file_name}')

        except Exception as e:
            print(f"Error scraping page: {e}")

        page_number += 1
        time.sleep(3)

    driver.quit()
    print('Scraping completed.')

    scrape_profiles(file_name)

if __name__ == "__main__":
    main()
