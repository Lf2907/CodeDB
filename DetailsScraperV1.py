import csv
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re


def process_order(driver, order_url):
    driver.get(order_url)

    # Add your processing logic here

    print("Done")
    time.sleep(5)  # Pause for 5 seconds before moving to the next URL


def find_links():
    url = "https://www.ebay.com/sh/ord?filter=timerange%3ATODAY"
    driver = webdriver.Chrome()
    driver.get(url)
    input('Enter Anything to continue')

    orders = driver.find_elements(By.XPATH, "//div[contains(@class, 'order-buyer-details')]")

    initial_data = []  # Store initial data here

    for order in orders:
        order_id_element = order.find_element(By.XPATH, ".//div[contains(@class, 'order-details ')]")
        order_id = order_id_element.text
        order_url = f"https://www.ebay.com/mesh/ord/details?mode=SH&srn=1222&orderid={order_id}&source=Orders&ru=https%3A%2F%2Fwww.ebay.com%2Fsh%2Ford%3Ffilter%3Dtimerange%253ATODAY"
        print(order_id, order_url)

        initial_data.append((order_id, order_url))

    for order_id, order_url in initial_data:
        process_order(driver, order_url)

    driver.quit()


find_links()
