# Doctor Profile Scraper

## Overview
The Doctor Profile Scraper is a Python script that automates the extraction of doctor profiles from the Doctolib website based on user-defined criteria. This tool utilizes Selenium to navigate web pages, retrieve relevant data, and save the collected information into an Excel file. 

## Use Case
This project is useful for healthcare professionals, researchers, or anyone interested in gathering information about doctors in a specific location and specialty. Users can specify the type of doctor and their location, and the script will compile a list of doctor names, their profile links, and consultation types and fees.

## Features
- **Web Scraping**: Automatically navigates through multiple pages of doctor listings.
- **Excel Integration**: Saves scraped data directly to an Excel file for easy viewing and analysis.
- **Headless Browser**: Runs the browser in headless mode to avoid GUI overhead, allowing for faster execution.
- **Error Handling**: Robust error handling to ensure the script can recover from unexpected issues during scraping.

## Requirements
- Python 3.x
- Selenium
- pandas
- openpyxl
- webdriver-manager
- An active internet connection

## Setup Instructions
1. **Install Dependencies**:
   Ensure you have the required Python packages installed. You can install them using pip:
   ```bash
   pip install selenium pandas openpyxl webdriver-manager
Download ChromeDriver: The script uses ChromeDriver for Selenium. The webdriver-manager package will automatically handle this during execution.

Run the Script: Execute the script in your terminal:
python doctor_profile_scraper.py

You will be prompted to enter: 
- **Type of doctor** (e.g., psychologue) 
- **Location** (e.g., france) 

## Data Storage 
The scraped data will be saved in an Excel file named `{docteur}_{localisation}.xlsx` in the same directory as the script. The file will include: 
- **Doctor Names** 
- **Links to their profiles** 
- **Consultation Types and Fees** 

## How It Works 
- **Initialization**: The script starts by initializing the WebDriver with headless options. 
- **User Input**: It prompts the user for the type of doctor and their location, forming the base URL for scraping. 
- **Scraping Process**: The script navigates through multiple pages, extracting doctor names and profile links. It tracks empty pages to avoid unnecessary requests. 
- **Profile Data Extraction**: For each doctor link collected, the script accesses the profile page and scrapes consultation types and fees. 
- **Excel Update**: All collected data is periodically saved to an Excel file to ensure no data loss. 

## Error Handling 
The script includes basic error handling for web element retrieval and page loading issues. If an error occurs, the script will log the error and attempt to continue scraping or retry after a delay. 

## Conclusion 
This Doctor Profile Scraper automates the tedious process of gathering doctor information from the Doctolib website, making it a valuable tool for anyone needing comprehensive data on medical professionals in a specified area.
