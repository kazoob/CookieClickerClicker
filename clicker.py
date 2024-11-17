from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from threading import Thread
import time

URL = "https://orteil.dashnet.org/cookieclicker/"
SAVE_DATA_FILENAME = "save_data.txt"


class Clicker:
    def __init__(self):
        # Set up browser driver.
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(name="detach", value=True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(URL)

        # Wait for the language selection menu
        try:
            element_present = EC.presence_of_element_located((By.ID, "langSelect-EN"))
            WebDriverWait(self.driver, 5).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        else:
            # Select language
            try:
                lang_element = self.driver.find_element(By.ID, value="langSelect-EN")
                lang_element.click()
            except NoSuchElementException:
                print("No lang")

        # Click the cookie policy prompt
        try:
            cookie_policy_element = self.driver.find_element(By.LINK_TEXT, value="Got it!")
        except NoSuchElementException:
            pass
        else:
            cookie_policy_element.click()

        # Load existing save if present
        save_data_result = False
        try:
            # Load save data from file
            with open(SAVE_DATA_FILENAME) as save_file:
                save_data = save_file.read()
        except FileNotFoundError:
            print("Save data not found")
        else:
            # Load save data into game
            save_data_result = self.driver.execute_script(f'return Game.ImportSaveCode("{save_data.strip()}")')

        self.cookie_element = None
        self.clicking = False

        # If save data loaded successfully, start clicking
        if save_data_result:
            time.sleep(2)
            self.toggle_clicking()

    def toggle_clicking(self):
        self.clicking = not self.clicking

        if self.clicking:
            self.cookie_element = self.driver.find_element(By.ID, value="bigCookie")
            thread = Thread(target=self.click)
            thread.start()

    def click(self):
        while self.clicking:
            # Check for a golden cookie
            try:
                golden_cookie = self.driver.find_element(By.CLASS_NAME, value="shimmer")
            except NoSuchElementException:
                pass
            else:
                golden_cookie.click()

            # Click the big cookie
            self.cookie_element.click()

    def save_file(self):
        # Get save data.
        self.driver.execute_script('Game.ExportSave()')
        save_data_element = self.driver.find_element(By.ID, value="textareaPrompt")
        save_data = save_data_element.text

        # Export save data to text file.
        with open(file=SAVE_DATA_FILENAME, mode="w") as save_file:
            save_file.write(save_data)

    def quit(self):
        # Stop clicking
        if self.clicking:
            self.clicking = False

        # Save game data to file
        self.save_file()

        # Quit browser.
        self.driver.quit()

# PURCHASE_INTERVAL_SEC = 5  # Interval to purchase upgrades in seconds
# PURCHASE_MULTIPLE = False  # Purchase multiple items every purchase interval
# GAME_RUN_MIN = 5  # Game run time in minutes
#
#
# def purchase_upgrades():
#     """Purchase available upgrades."""
#     # Keep purchasing upgrades if multiple purchases enabled.
#     while purchase_next_upgrade() and PURCHASE_MULTIPLE:
#         # Delay to allow game to register purchase click
#         time.sleep(0.06)
#
#
# def purchase_next_upgrade() -> bool:
#     """Purchase the highest affordable upgrade. Return True if an upgrade was purchased, otherwise return False."""
#     # Get cookie value.
#     cookies = int(driver.find_element(By.ID, "money").text.replace(",", ""))
#
#     # Get store item names and prices.
#     store = get_store()
#
#     print(f"Purchasing upgrade with {cookies} cookies")
#
#     # Go through each store item.
#     for store_item in store:
#         # Check if enough cookies to purchase one item.
#         if cookies // store_item["price"] > 0:
#             # Purchase the item.
#             driver.find_element(By.ID, value=store_item["id"]).click()
#
#             # Return True to indicate successful purchase.
#             print(f"Purchased {store_item["id"].replace("buy", "")} for {store_item["price"]} cookies")
#             return True
#
#     # Return False to indicate unsuccessful purchase.
#     print("Not enough cookies to purchase an upgrade")
#     return False
#
#
# def get_store() -> list:
#     """Return the store items and prices. Prices are ordered from highest to lowest."""
#     # Store list.
#     store = []
#
#     # Get store element.
#     store_items = driver.find_elements(by=By.CSS_SELECTOR, value="#store > div")
#
#     # Go through each store item.
#     for store_item in store_items:
#         try:
#             # Get the store item element class name.
#             store_id = store_item.get_attribute("id").replace(" ", "\\ ")
#
#             # Get the store item price.
#             price_element = driver.find_element(By.CSS_SELECTOR, value=f"#{store_id} > b")
#             item_price = int(price_element.text.split("-")[1].strip().replace(",", ""))
#
#             # Build new store item dict.
#             new_item = {
#                 "id": store_id,
#                 "price": item_price,
#             }
#
#             # Append new store item dict to store list.
#             store.append(new_item)
#         # Skip over invalid store item.
#         except IndexError:
#             pass
#         # If store changes during processing (usually due to cookie number increasing from buildings and a new
#         # option becoming available), get a new store.
#         except StaleElementReferenceException:
#             return get_store()
#         # Skip over invalid store item.
#         except NoSuchElementException:
#             pass
#         # Print any other error to the console.
#         except Exception as e:
#             print(f"Error: {type(e).__name__}")
#
#     # Order the store prices from highest to lowest.
#     store.reverse()
#
#     # Return the store.
#     return store


# # Set the game end time.
# game_end: float = time.time() + GAME_RUN_MIN * 60
#
# # Set the next purchase interval.
# purchase_time: float = time.time() + PURCHASE_INTERVAL_SEC
#
# # Continue to run game until game end time.
# current_time: float = time.time()
# while current_time < game_end:
#     # Purchase interval has been reached.
#     if current_time >= purchase_time:
#         # Purchase items.
#         purchase_upgrades()
#
#         print("")
#
#         # Set next purchase interval.
#         purchase_time = current_time + PURCHASE_INTERVAL_SEC
#
#         # Display remaining game time.
#         minutes_remaining: int = round((game_end - current_time) // 60)
#         seconds_remaining: int = round((game_end - current_time) % 60)
#         print(f"Game time remaining: {minutes_remaining} minutes, {seconds_remaining} seconds\n")
#
#     # Click cookie every loop.
#     driver.find_element(By.ID, "cookie").click()
#
#     # Update current time.
#     current_time = time.time()
#
# # Display end score.
# print(f"Final score after {GAME_RUN_MIN} minutes: {driver.find_element(By.ID, "cps").text}")
