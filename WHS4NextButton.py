import csv
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains


def click_anywhere(driver):
    action = ActionChains(driver)
    action.move_by_offset(1, 1).click().perform()


def find_listings(start_page, max_next_clicks, csv_writer):
    base_url = "https://www.amazon.com/s?i=baby-products&bbn=10158976011&rh=n%3A10158976011%2Cn%3A165796011&"

    driver = webdriver.Chrome()

    for page in range(start_page, start_page + max_next_clicks):
        page_url = f"{base_url}&page={page}&pf_rd_i=10158976011&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=eab4102e-b108-46b0-8ab9-435d397c61f2&pf_rd_r=G28J5XYJG1216VCK40GX&pf_rd_s=merchandised-search-5&pf_rd_t=101&qid=1706118974&ref=sr_pg_{page}"
        driver.get(page_url)
        input("Press Any Key to continue")

        listings = driver.find_elements(By.XPATH,"//div[contains(@class, 'sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20')]")

        for listing in listings:
            item = {}
            item['Title'] = listing.find_element(By.XPATH,
                                                 ".//span[contains(@class, 'a-size-base-plus a-color-base a-text-normal')]").text
            item['Review Count'] = listing.find_element(By.XPATH,
                                                        ".//span[contains(@class, 'a-size-base s-underline-text')]").text
            item['Sold Count'] = listing.find_element(By.XPATH,
                                                      ".//span[contains(@class, 'a-size-base a-color-secondary')]").text
            item_link1 = listing.find_element(By.XPATH,
                                              ".//a[contains(@class, 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')]")
            item_link2 = item_link1.get_attribute('href')

            asin_start_index = item_link2.find("dp/") + 3
            asin_end_index = item_link2.find("/", asin_start_index)
            item['ASIN'] = item_link2[asin_start_index:asin_end_index]

            item['URL'] = item_link2

            try:
                options_button = listing.find_element(By.XPATH,
                                                      ".//a[contains(@class, 'a-link-normal s-link-style s-underline-text s-underline-link-text')]")
                options_button.click()
            except ElementNotInteractableException as e:
                print(f"Error clicking button: {e}")
                click_anywhere(driver)
                continue

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    ".//span[contains(@class, 'a-price aok-align-center centralizedApexPricePriceToPayMargin')]")))
            except TimeoutException as e:
                print(f"Error waiting for popup to load: {e}")
                close_button = driver.find_element(By.XPATH,
                                                   "//div[contains(@class, 'a-section a-spacing-none a-padding-none')]")
                close_button.click()
                click_anywhere(driver)
                continue

            new_price = driver.find_elements(By.XPATH,
                                             ".//span[contains(@class, 'a-price aok-align-center centralizedApexPricePriceToPayMargin')]")
            new_price1 = new_price[1].text.replace("\n", ".")
            item['New Price'] = new_price1

            # Filter for Prime and Like New
            filter_button = driver.find_element(By.XPATH, "//span[@id='aod-filter-string']")
            if filter_button.is_displayed():
                time.sleep(1)
                filter_button.click()
                time.sleep(1)

                try:
                    prime_button = driver.find_element(By.XPATH, "//div[@id='primeEligible']")
                    prime_button.click()
                    time.sleep(1)
                except ElementNotInteractableException as e:
                    print(f"Error clicking prime button: {e}")
                    print("Skipping filtering step for this item.")
                    close_button = driver.find_element(By.XPATH,
                                                       "//div[contains(@class, 'a-section a-spacing-none a-padding-none')]")
                    close_button.click()
                    click_anywhere(driver)
                    continue

                try:
                    like_new_button = driver.find_element(By.XPATH, "//div[@id='usedLikeNew']")
                    like_new_button.click()

                    # Wait until the presence of the element with class 'a-section a-spacing-none a-padding-base aod-information-block aod-clear-float'
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        ".a-section.a-spacing-none.a-padding-base.aod-information-block.aod-clear-float")))

                    time.sleep(1.5)
                except ElementNotInteractableException as e:
                    print(f"Error clicking like new button: {e}")
                    print("Skipping filtering step for this item.")
                    close_button = driver.find_element(By.XPATH,
                                                       "//div[contains(@class, 'a-section a-spacing-none a-padding-none')]")
                    close_button.click()
                    click_anywhere(driver)
                    continue

                try:
                    like_new_listings = driver.find_elements(By.XPATH, "//div[@id='aod-offer']")

                    for like_new_listing in like_new_listings:
                        like_new_price_element = like_new_listing.find_element(By.XPATH,
                                                                               ".//div[@id='aod-offer-price']")
                        like_new_price = like_new_price_element.text
                        like_new_price_parts = like_new_price.replace("\n", ".").split('.')
                        like_new_price2 = '.'.join(like_new_price_parts[:2])

                        item['Like-New Price'] = like_new_price2
                        print(like_new_price2)

                        try:
                            qty_scroller = WebDriverWait(like_new_listing, 4).until(
                                EC.presence_of_element_located((By.ID, "aod-qty-dropdown-scroller"))
                            )
                        except TimeoutException as e:
                            print(f"Error waiting for quantity scroller: {e}")
                            # Handle the error as needed
                            continue

                        qty_options = qty_scroller.find_elements(By.CLASS_NAME, "aod-qty-option")

                        max_quantity = len(qty_options)
                        print("Max Quantity:", max_quantity)
                        item['Max Quantity'] = max_quantity

                        print(item)
                        # Writing data to CSV file immediately after scraping for each like-new listing
                        csv_writer.writerow([item.get(key, '') for key in
                                             ['Title', 'Review Count', 'Sold Count', 'ASIN', 'URL', 'New Price',
                                              'Max Quantity', 'Like-New Price']])

                except Exception as e:
                    print(f"Error processing like-new listings: {e}")
            else:
                print("Filter button not found. Skipping filtering step.")

            try:
                close_button = driver.find_element(By.XPATH,
                                                   "//div[contains(@class, 'a-section a-spacing-none a-padding-none')]")
                close_button.click()
            except ElementNotInteractableException as e:
                print(f"Error clicking close button: {e}")

            time.sleep(2)

        # Additional logic for navigating to the next page
        try:
            next_button = driver.find_element(By.XPATH,
                                              "//a[contains(@class, 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator')]")
            next_button.click()
            time.sleep(2)  # Add a delay to allow the next page to load
        except NoSuchElementException:
            print("No 'Next' button found. Exiting pagination.")
            break

    # Close the WebDriver after processing all pages
    driver.quit()


# Usage example
start_page = 1
max_next_clicks = 5  # Set the number of times to iterate over pages
csv_filename = 'output.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(
        ['Title', 'Review Count', 'Sold Count', 'ASIN', 'URL', 'New Price', 'Max Quantity', 'Like-New Price'])
    find_listings(start_page, max_next_clicks, csv_writer)

print("Done")
