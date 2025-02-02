from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import csv

class ExhibitorListScraper:

  BASE_URL = 'https://www.mwcbarcelona.com/exhibitors'

  @staticmethod
  def get_href(link) -> str:
      return str(link.get_attribute('href'))

  def __init__(self, driver: webdriver.Chrome):
    self.driver = driver

  def open_page(self, page_num: int):
      self.driver.get(f"{ExhibitorListScraper.BASE_URL}?page={page_num}")

  def find_all_exhib_links(self) -> list[str]:
    exhibitors_list = self.driver.find_element(By.CLASS_NAME, 'exhibitor-listing')
    links = exhibitors_list.find_elements(By.TAG_NAME, 'a')
    return list(map(ExhibitorListScraper.get_href, links))

  def get_all_exhibitor_links(self) -> list[str]:
    page_num = 1
    all_links = []
    while True:
        self.open_page(page_num)
        links = self.find_all_exhib_links()
        links_count = len(links)
        if links_count == 0:
          print('Did not find any exhibitor, assuming this was last page bye')
          return all_links
        print(f"Got {len(links)} exhibitors from page #{page_num}")
        all_links.extend(links)
        page_num += 1

class Exhibitor:
    def __init__(self, name: str, desc: str, location: str):
        self.name = name
        self.desc = desc
        self.location = location

    def __str__(self) -> str:
        return f"{self.name}"

    def to_csv_format(self) -> list[str]:
        return [self.name, self.desc, self.location]

class ExhibitorDetailScraper:
  def __init__(self, driver: webdriver.Chrome):
    self.driver = driver

  def get_company_name(self) -> str:
      # Company name is the only h1
      return self.driver.find_element(By.TAG_NAME, 'h1').text

  def get_information(self) -> str:
      # Information is in the 1st and only div of main
      main = self.driver.find_element(By.TAG_NAME, 'main')
      return main.find_element(By.TAG_NAME, 'div').text

  def get_location(self) -> str:
      # location is an url text that follows a fa-location-dot-icon
      locations_links = self.driver.find_elements(By.XPATH, "//a[i[@class='fa-solid fa-location-dot']]")
      locations = list(map(lambda  l : l.text, locations_links))
      return ";".join(locations)

  def get_exhibitor_info(self, url: str) -> Exhibitor:
      self.driver.get(url)
      return Exhibitor(
          self.get_company_name(),
          self.get_information(),
          self.get_location()
      )

def main():
  driver = webdriver.Chrome()
  driver.implicitly_wait(3)

  list_scraper = ExhibitorListScraper(driver)
  exhibitor_scraper = ExhibitorDetailScraper(driver)

  writer = csv.writer(open('exhibitors.csv', 'w'))
  writer.writerow(['Name', 'Description', 'Location'])

  i = 0
  for exhibitor_url in list_scraper.get_all_exhibitor_links():
    ex = exhibitor_scraper.get_exhibitor_info(exhibitor_url)
    print(f'Scrapped info from {ex}')
    writer.writerow(ex.to_csv_format())
    i += 1

  print(f'Scrapped info from {i} exhibitors')

if __name__ == '__main__':
  main()
