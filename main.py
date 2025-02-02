from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import csv

BASE_URL = 'https://www.mwcbarcelona.com/exhibitors'
exhib_regex = fr"{BASE_URL}/\d+"

def get_href(link) -> str:
    return str(link.get_attribute('href'))

def find_all_exhib_links() -> list[str]:
  exhibitors_list = driver.find_element(By.CLASS_NAME, 'exhibitor-listing')
  links = exhibitors_list.find_elements(By.TAG_NAME, 'a')
  return list(map(get_href, links))

def open_page(page_num: int):
    driver.get(f"{BASE_URL}?page={page_num}")

def get_all_exhibitor_links() -> list[str]:
  page_num = 1
  all_links = []
  while True:
      open_page(page_num)
      links = find_all_exhib_links()
      links_count = len(links)
      if links_count == 0:
        print('Did not find any exhibitor, assuming this was last page bye')
        return all_links
      print(f"Got {len(links)} exhibitors from page #{page_num}")
      all_links.extend(links)
      page_num += 1

def get_company_name() -> str:
    # Company name is the only h1
    return driver.find_element(By.TAG_NAME, 'h1').text

def get_information() -> str:
    # Information is in the 1st and only div of main
    main = driver.find_element(By.TAG_NAME, 'main')
    return main.find_element(By.TAG_NAME, 'div').text

def get_location() -> str:
    # location is an url text that follows a fa-location-dot-icon
    locations_links = driver.find_elements(By.XPATH, "//a[i[@class='fa-solid fa-location-dot']]")
    locations = list(map(lambda  l : l.text, locations_links))
    # Beurk aussi
    all_locations = ""
    for location in locations:
        all_locations += f"{location} "
    return all_locations.strip()

class Exhibitor:
    def __init__(self, name: str, desc: str, location: str):
        self.name = name
        self.desc = desc
        self.location = location

    def __str__(self) -> str:
        return f"{self.name}"

    def to_csv_format(self) -> list[str]:
        return [self.name, self.desc, self.location]

def get_exhib_info(url: str) -> Exhibitor:
    driver.get(url)
    time.sleep(.3)
    return Exhibitor(
        get_company_name(),
        get_information(),
        get_location()
    )

def get_all_exhib_info():
    with open('list.txt', 'r') as file:
        writer = csv.writer(open('output.csv', 'w'))
        writer.writerow(['Name', 'Description', 'Location'])
        i = 1
        for line in file:
            print(f'Extracting #{i}')
            formatted = get_exhib_info(line).to_csv_format()
            writer.writerow(formatted)
            i += 1
    print(f'All done, extracted f{i} rows')

driver = webdriver.Chrome()

driver.implicitly_wait(3)
all_links = get_all_exhibitor_links()
print(f'Found {len(all_links)} exhibitors')
