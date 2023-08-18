import csv
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re




def find_listings(pgn):
   url = "https://www.amazon.com/ab/business-discounts?ref_=abn_cs_ab_sg&pd_rd_r=e368e3ad-2508-4f44-b8f1-dceded47a6a2&pd_rd_w=buTkU&pd_rd_wg=z7ruP"
   driver = webdriver.Chrome()
   driver.get(url)
   input('Enter Anything to continue')

   listings = driver.find_elements(By.XPATH, "//div[contains(@class, 'b-item pluto-gallery-item')]")
   data = []
   for listing in listings:
       item = {}
       item['NAME'] = listing.find_element(By.XPATH, ".//a[contains(@class, 'a-link-normal pluto-product-title')]").text
       item_title1 =  listing.find_element(By.XPATH, ".//a[contains(@class, 'a-link-normal pluto-product-title')]")
       item_title2 = item_title1.get_attribute('href')
       item['URL'] = item_title2
       base_price = listing.find_element(By.XPATH, ".//span[contains(@class, 'a-price pluto-sg-product-price')]").text
       item['BASE PRICE'] = base_price.replace('\n', '.')
       b_price = listing.find_element(By.XPATH, ".//div[contains(@class, 'pluto-sg-product-price')]").text
       item['DISCOUNTED PRICE'] = b_price.replace('\n', '.')
       discount_rate = listing.find_element(By.XPATH, ".//div[contains(@class, 'pluto-sg-business-savings')]").text
       item['DISCOUNT RATE'] = discount_rate.replace('\nBUSINESS SAVINGS', ' ')
       item_picture1 = listing.find_element(By.XPATH, ".//img[contains(@class, 'b-responsive pluto-product-image')]")
       item_picture2 = item_picture1.get_attribute('src')
       item['PICTURE'] = item_picture2
       print(item)


       data.append(item)

       # Write item to CSV file
       with open('complete1.csv', 'a', newline='', encoding='utf-8') as csvfile:
           writer = csv.writer(csvfile)
           writer.writerow([item['NAME'], item['URL'], item['BASE PRICE'], item['DISCOUNTED PRICE'], item['DISCOUNT RATE'], item['PICTURE']])

   driver.quit()
   return data

def export_data(data):
    with open('complete1.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'URL', 'Base Price', 'Discounted Price', 'Discount Rate', 'Picture'])

        for item in data:
            name = item['NAME']
            url = item['URL']
            bprice = item['BASE PRICE']
            dprice = item['DISCOUNTED PRICE']
            rate = item['DISCOUNT RATE']
            picture = item['PICTURE']

            # Write the item data to the CSV file
            writer.writerow([name, url, bprice, dprice, rate, picture])

             # Flush the buffer to ensure data is written to disk
            csvfile.flush()

if __name__ == '__main__':
   pgn = 1
   all_data = []
   while pgn <= 1:
       data = find_listings(pgn)
       if not data:
           break
       all_data.extend(data)
       pgn += 1
   export_data(all_data)
   print("Done")
