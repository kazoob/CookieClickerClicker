from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from threading import Thread, Event
import time
import os.path
import glob
from datetime import datetime

URL = "https://orteil.dashnet.org/cookieclicker/"

SAVE_DATA_FILENAME = "save_data.txt"
SAVE_DATA_BACKUP_COUNT = 10

INTERACTION_DELAY = 1
ELEMENT_WAIT_DELAY = 5
WRINKLER_CHECK_FREQUENCY = 5


class Clicker:
    """Open game in browser. Set up game. Import save data (if found). Start clicking if save data imported."""

    def __init__(self):
        # Set up browser driver.
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(name="detach", value=True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(URL)

        # Wait for the cookie policy prompt.
        try:
            element_present = EC.presence_of_element_located((By.LINK_TEXT, "Got it!"))
            WebDriverWait(self.driver, ELEMENT_WAIT_DELAY).until(element_present)
        except TimeoutException:
            print("Timed out waiting for cookie policy prompt")
        else:
            # Click the cookie policy prompt.
            try:
                cookie_policy_element = self.driver.find_element(By.LINK_TEXT, value="Got it!")
                cookie_policy_element.click()
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                pass
            except ElementClickInterceptedException:
                pass
            except ElementNotInteractableException:
                pass
            else:
                # Brief sleep to allow cookie policy selection.
                time.sleep(INTERACTION_DELAY)

        # Wait for the language selection menu.
        try:
            element_present = EC.presence_of_element_located((By.ID, "langSelect-EN"))
            WebDriverWait(self.driver, ELEMENT_WAIT_DELAY).until(element_present)
        except TimeoutException:
            print("Timed out waiting for language selection menu")
        else:
            # Select language.
            try:
                lang_element = self.driver.find_element(By.ID, value="langSelect-EN")
                lang_element.click()
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                pass
            except ElementClickInterceptedException:
                pass
            except ElementNotInteractableException:
                pass
            else:
                # Brief sleep to allow language selection.
                time.sleep(INTERACTION_DELAY)

        # Load existing save if present.
        save_data_result = False
        try:
            # Load save data from file.
            with open(SAVE_DATA_FILENAME) as save_file:
                save_data = save_file.read()
        except FileNotFoundError:
            print(f"Save data not found: {SAVE_DATA_FILENAME}")
        else:
            # Load save data into game.
            save_data_result = self.driver.execute_script(f'return Game.ImportSaveCode("{save_data.strip()}");')

            # Brief sleep to allow save data load.
            time.sleep(INTERACTION_DELAY)

        # Disable save prompt.
        self.driver.execute_script('Game.prefs.showBackupWarning = 0; Game.CloseNote(1);')
        time.sleep(INTERACTION_DELAY)

        # Do not click cookie by default.
        self.clicking_event = Event()

        # If save data loaded successfully, start clicking.
        if save_data_result:
            self.toggle_clicking()

    def toggle_clicking(self):
        """Start / stop cookie clicking."""
        # Invert cookie clicking status.
        if self.clicking_event.is_set():
            # Stop cookie clicking.
            self.clicking_event.clear()
        else:
            # Start cookie clicking.
            self.clicking_event.set()

            # Start cookie clicking thread.
            cookie_thread = Thread(target=self.cookie_click)
            cookie_thread.start()

            # Start wrinkler popping thread.
            wrinkler_thread = Thread(target=self.wrinkler_pop)
            wrinkler_thread.start()

    def get_clicking_status(self):
        return self.clicking_event.is_set()

    def cookie_click(self):
        """Repeatedly click the big cookie."""
        # Continue until requested to stop.
        while self.clicking_event.is_set():
            # Check for a golden cookie.
            try:
                golden_cookie = self.driver.find_element(By.CLASS_NAME, value="shimmer")
            except NoSuchElementException:
                pass
            else:
                try:
                    # Click the golden cookie.
                    # TODO alternative Javascript
                    #  https://www.reddit.com/r/CookieClicker/comments/6ntgjf/autoclick_golden_cookie_code_confirmed_to_work/
                    golden_cookie.click()
                except StaleElementReferenceException:
                    pass
                except ElementClickInterceptedException:
                    pass
                except ElementNotInteractableException:
                    pass

            # Click the big cookie.
            self.driver.execute_script('Game.ClickCookie();')

    def wrinkler_pop(self):
        """Periodically check for any spawned wrinklers and pop them."""
        # Continue until requested to stop.
        while self.clicking_event.is_set():
            # https://www.reddit.com/r/CookieClicker/comments/hl5e8i/shiny_wrinkler_and_a_javascript_code_for/
            # Javascript to pop any spawned wrinklers.
            # type == 0 to only pop non-shiny wrinklers
            # sucked > 0 to ensure wrinkler touches cookie and starts eating
            self.driver.execute_script(
                'for (var i in Game.wrinklers)'
                '{'
                '   if (Game.wrinklers[i].type == 0 && Game.wrinklers[i].sucked > 0)'
                '       {Game.wrinklers[i].hp = 0;'
                '   }'
                '}'
            )

            # Throttle the next wrinkler check.
            time.sleep(WRINKLER_CHECK_FREQUENCY)

    def purchase_best_building(self):
        # TODO purchase best building
        try:
            store_elements = self.driver.find_element(By.CLASS_NAME, value="products")
        except NoSuchElementException:
            pass
        else:
            pass

    # TODO elder pledge
    # TODO bingo research purchase

    def save_file(self):
        """Export save data to file."""
        # TODO periodic save
        # Get save data.
        save_data = self.driver.execute_script('return Game.WriteSave(1);')

        if save_data:
            # Check if existing save file is present.
            if os.path.isfile(SAVE_DATA_FILENAME):
                # Rename existing save file, append current date time.
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_file_name = f"{SAVE_DATA_FILENAME.replace(".", f"_{timestamp}.")}"
                os.rename(src=SAVE_DATA_FILENAME, dst=backup_file_name)

            # Get list of backup save files, sorted oldest to newest.
            save_backup_files = sorted(glob.glob(SAVE_DATA_FILENAME.replace(".", "_*.")))

            # Check if backup save file count exceeds max count.
            if len(save_backup_files) > SAVE_DATA_BACKUP_COUNT:
                # Delete oldest files.
                for i in range(0, len(save_backup_files) - SAVE_DATA_BACKUP_COUNT):
                    try:
                        os.remove(save_backup_files[i])
                    except FileNotFoundError:
                        print(f"Unable to delete old save file: {save_backup_files[i]}")

            # Export save data to text file.
            with open(file=SAVE_DATA_FILENAME, mode="w") as save_file:
                save_file.write(save_data)

    def quit(self, save: bool = True):
        """Save the game data to file. Quit the game."""
        # Stop clicking threads.
        if self.clicking_event.is_set():
            self.clicking_event.clear()

        # Save game data to file if requested.
        if save:
            self.save_file()

        # Quit browser.
        self.driver.quit()
