from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def extract_str(a):
    try:
        if 'K' in a:
            a = a.replace('K', '')
            a = float(a) * 1000
        elif '+ Employees' in a:
            a = a.replace('+ Employees', '')
            a = float(a)
    except:
        a = None
    return a


def crawl_data(driver):
    data = []
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    allCompanysContainer = soup.find("div", {"class": "col-md-12 col-lg-8"})

    if allCompanysContainer:
        companys = allCompanysContainer.findAll("div", {"class": "mt-0 mb-std p-std css-mdw3bo css-errlgf"})

        if companys:
            for company in companys:
                obj = {}
                try:
                    # name
                    obj['name'] = company.find('h2', attrs={'data-test': 'employer-short-name'}).text

                    # rate
                    span_tag = company.find('span', class_='pr-xsm', attrs={'data-test': 'rating'})
                    obj['rate'] = span_tag.find('b').text

                    # image
                    obj['image'] = company.find('img', attrs={'class': 'employerInfo__EmployerInfoStyles__logoStyle',
                                                               'data-test': 'employer-logo', 'src': True})["src"]

                    company_size = company.find('span', class_='d-block mt-0 css-56kyx5',
                                                attrs={'data-test': 'employer-size'}).text
                    # global company size
                    obj['glb_company_size'] = extract_str(company_size)

                    # industry
                    obj['industry'] = company.find('span', class_='d-block mt-0 css-56kyx5',
                                                   attrs={'data-test': 'employer-industry'}).text

                    # review
                    review = company.find('div', class_='d-flex flex-column align-items-center', 
                                          attrs={'data-test': 'cell-Reviews'})
                    review = review.find('h3', attrs={'data-test': 'cell-Reviews-count'}).text
                    obj['review'] = extract_str(review)

                    # salary
                    salary = company.find('div', class_='d-flex flex-column align-items-center',
                                          attrs={'data-test': 'cell-Salaries'})
                    salary = salary.find('h3', attrs={'data-test': 'cell-Salaries-count'}).text
                    obj['salary'] = extract_str(salary)

                    # jobs
                    jobs = company.find('div', class_='d-flex flex-column align-items-center',
                                        attrs={'data-test': 'cell-Jobs'})
                    jobs = jobs.find('h3', attrs={'data-test': 'cell-Jobs-count'}).text
                    obj['jobs'] = extract_str(jobs)
                    #locations
                    obj['locations'] = company.find('span', class_='d-block mt-0 css-56kyx5').text
                    # description
                    obj['description'] = company.find('p', class_='css-1sj9xzx css-56kyx5').text

                except:
                    obj['name'] = None
                    obj['rate'] = None
                    obj['image'] = None
                    obj['glb_company_size'] = None
                    obj['industry'] = None
                    obj['review'] = None
                    obj['salary'] = None
                    obj['jobs'] = None
                    obj['locations'] = None
                    obj['description'] = None

                data.append(obj)

            df = pd.DataFrame(data)
            file_name = 'glassdoor_data.csv'

            if not os.path.isfile(file_name):
                df.to_csv(file_name, mode='w', header=True, index=False, encoding='utf-8')
            else:
                df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8')
        else:
            print('Không tìm thấy sản phẩm')
    else:
        print('Không tìm thấy sản phẩm')


def main():
    # Define chrome_options within the main function
    chrome_options = webdriver.ChromeOptions()

    # ... (rest of the function)

    chrome_driver_path = "E:/crawl_data/chromedriver.exe"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)


    url = "https://www.glassdoor.com/Reviews/index.htm?overall_rating_low=3.5&page=1&filterType=RATING_OVERALL"
    driver.get(url)

    print('Chuẩn bị crawl')
    print('Vui lòng không tắt tool hoặc trình duyệt')
    print('===============================')

    visited_urls = set()

    for i in range(1, 15):
        try:
            print('Chuẩn bị crawl trang', i)
            url = f"https://www.glassdoor.com/Reviews/index.htm?overall_rating_low=3.5&page={i}&filterType=RATING_OVERALL"

            if url in visited_urls:
                continue

            visited_urls.add(url)

            driver.get(url)
            crawl_data(driver)

        except Exception as e:
            print(f"Lỗi khi trích xuất dữ liệu từ trang: {e}")

        print('Đã xong trang:', i)
        print('=============================')

    driver.quit()


if __name__ == "__main__":
    main()
