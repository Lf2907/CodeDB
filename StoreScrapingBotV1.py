import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import csv


def find_listings(pgn):
   url = f"#EbayURLGoesHere{pgn}"
   driver = webdriver.Chrome()
   driver.get(url)
   time.sleep(15)


   listings = driver.find_elements(By.XPATH, "//li[contains(@class, 's-item s-item__dsa-on-bottom s-item__pl-on-bottom')]")
   data = []
   for listing in listings:
       item = {}
       item['NAME'] = listing.find_element(By.XPATH, ".//div[contains(@class, 's-item__title')]").text
       item['COST'] = listing.find_element(By.XPATH, ".//span[contains(@class, 's-item__price')]").text


       item_url = listing.find_element((By.XPATH, ".//a[contains(@classs, '-item__link')]"))
       item['URL'] = item_url


       response = requests.get(item_url)
       soup = BeautifulSoup(response.text, 'lxml')
       sold_count_elem = soup.find('span', class_='ux-textspans ux-textspans--BOLD ux-textspans--EMPHASIS')
       if sold_count_elem and 'sold' in sold_count_elem.text.lower():
           item['SC'] = sold_count_elem.text.strip('sold')
       else:
           sold_count_elems = soup.find_all('span', class_='ux-textspans')
           for elem in sold_count_elems:
               if 'sold' in elem.text.lower():
                   item['SC'] = elem.text.strip('sold')
                   break
           else:
               item['SC'] = ''


       data.append(item)


       # Write item to CSV file
       with open('complete1.csv', 'a', newline='', encoding='utf-8') as csvfile:
           writer = csv.writer(csvfile)
           writer.writerow([item['NAME'], item['COST'], item['URL'], item['SC']])


   driver.quit()
   return data




def export_data(data):
   with open('complete1.csv', 'w', newline='', encoding='utf-8') as csvfile:
       writer = csv.writer(csvfile)
       writer.writerow(['Ebay Name', 'Ebay Cost', 'Ebay URL', 'Sold Count'])


       for item in data:
           name = item['NAME']
           cost = item['COST']
           url = item['URL']
           sc = item['SC']


           # Write the item data to the CSV file
           writer.writerow([name, cost, url, sc])


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
