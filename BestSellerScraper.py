import csv
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re

def find_listings(pgn):
    url = f"https://www.amazon.com/s?k=%5B%5D&i=beauty&s=exact-aware-popularity-rank&page={pgn}&crid=2KTN31JNMOB4X&qid=1692639435&sprefix=%2Cbeauty%2C534&ref=sr_pg_{pgn}"
    driver = webdriver.Chrome()
    driver.get(url)

    if pgn == 1:
        input("Press Enter to continue...")  # Wait for user input on the first page
    else:
        time.sleep(2)  # Wait for 3 seconds on subsequent pages

    listings = driver.find_elements(By.XPATH, "//div[contains(@class, 'sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20')]")
    data = []

    for listing in listings: #Scrapes Amazon for product information
       item = {}
       item['NAME'] = listing.find_element(By.XPATH,".//span[contains(@class, 'a-size-base-plus a-color-base a-text-normal')]").text
       item_link1 = listing.find_element(By.XPATH,".//a[contains(@class, 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')]")
       item_link2 = item_link1.get_attribute('href')
       item['URL'] = item_link2
       try:
           price_element = listing.find_element(By.XPATH, ".//span[contains(@class, 'a-price')]")
           price = price_element.text.replace('\n', '.')
       except Exception:
           price = '0'  # Set price to 0 if the price element is not found

       item['PRICE'] = price

       print(item)
       data.append(item)

       # Write item to CSV file
       with open('complete2.csv', 'a', newline='', encoding='utf-8') as csvfile:
           writer = csv.writer(csvfile)
           writer.writerow([item['NAME'], item['URL'], item['PRICE']])

    driver.quit()
    return data


def export_data(data):
    with open('complete2.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'URL', 'Price'])

        for item in data:
            name = item['NAME']
            url = item['URL']
            price = item['PRICE']



            # Write the item data to the CSV file
            writer.writerow([name, url, price])

             # Flush the buffer to ensure data is written to disk
            csvfile.flush()

if __name__ == '__main__':
   pgn = 1
   all_data = []
   while pgn <= 400:
       data = find_listings(pgn)
       if not data:
           break
       all_data.extend(data)
       pgn += 1
       print(pgn)
   export_data(all_data)
   print("Done")
