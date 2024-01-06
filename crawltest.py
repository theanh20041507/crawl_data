from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os

def extract_str(value):
    try:
        if 'K' in value:
            value = float(value.replace('K', '')) * 1000
        elif '+ Employees' in value:
            value = float(value.replace('+ Employees', ''))
        else:
            value = None
    except ValueError:
        value = None
    return value

def extract_company_info(company):
    try:
        # Extracting various company information
        Conversations = company.find('div', class_='count', attrs={'data-test': 'ei-nav-faq-count'})
        Interviews = company.find('div', class_='count', attrs={'data-test': 'ei-nav-interviews-count'})
        Benefits = company.find('div', class_='count', attrs={'data-test': 'ei-nav-benefits-count'})
        Diversity = company.find('div', class_='count', attrs={'data-test': 'ei-nav-culture-count'})

        Conversations_text = Conversations.text if Conversations else None
        Interviews_text = Interviews.text if Interviews else None
        Benefits_text = Benefits.text if Benefits else None
        Diversity_text = Diversity.text if Diversity else None

        return {
            'Conversations': Conversations_text,
            'Interviews': Interviews_text,
            'Benefits': Benefits_text,
            'Diversity': Diversity_text,
        }
    except Exception as e:
        print(f"Error extracting information for a company: {e}")
        return None

def crawl_data(driver):
    data = []

    try:
        # Click on the 'mr-std' element
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'mr-std'))).click()
    except Exception as e:
        print(f"Error clicking on 'mr-std' element: {e}")
        return

    try:
        # Wait for the presence of the main container
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'col-md-12')))
        html_doc = driver.page_source
        soup = BeautifulSoup(html_doc, 'html.parser')
        all_companies_container = soup.find("div", {"class": "col-md-12 col-lg-8"})

        if all_companies_container:
            companies = all_companies_container.findAll("div", {"class": "mt-0 mb-std p-std css-mdw3bo css-errlgf"})

            if companies:
                for company in companies:
                    company_info = extract_company_info(company)
                    if company_info:
                        data.append(company_info)

                df = pd.DataFrame(data)
                file_name = 'data_glassdoor.csv'

                # Write to CSV file
                if not os.path.isfile(file_name):
                    df.to_csv(file_name, mode='w', header=True, index=False, encoding='utf-8')
                else:
                    df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8')
            else:
                print('Không tìm thấy sản phẩm')
        else:
            print('Không tìm thấy sản phẩm')

    except Exception as e:
        print(f"Error during data extraction: {e}")

    try:
        # Navigate back
        driver.back()
    except Exception as e:
        print(f"Error navigating back using driver.back(): {e}")

        try:
            # If navigating back fails, attempt using JavaScript
            print("Attempting to navigate back using JavaScript")
            driver.execute_script("window.history.go(-1)")
        except Exception as js_error:
            print(f"Error navigating back using JavaScript: {js_error}")

def main():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    # Add more options if needed

    # Set the path to the ChromeDriver executable
    chrome_driver_path = "E:/crawl_data/chromedriver.exe"
    service = Service(chrome_driver_path)
    
    # Initialize Chrome driver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Base URL for Glassdoor reviews with a specific overall rating
    url_base = "https://www.glassdoor.com/Reviews/index.htm?overall_rating_low=3.5&page={}&filterType=RATING_OVERALL"
    
    # Set of visited URLs to avoid duplicate crawling
    visited_urls = set()

    # Iterate through pages
    for i in range(1, 3):
        try:
            print('Chuẩn bị crawl trang', i)
            url = url_base.format(i)

            if url in visited_urls:
                continue

            visited_urls.add(url)

            # Navigate to the URL and crawl data
            driver.get(url)
            crawl_data(driver)

        except Exception as e:
            print(f"Lỗi khi trích xuất dữ liệu từ trang: {e}")

        print('Đã xong trang:', i)
        print('=============================')

    # Quit the driver after crawling all pages
    driver.quit()

if __name__ == "__main__":
    main()
