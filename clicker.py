from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import JavascriptException
from threading import Thread, Event
import time
import os.path
import glob
from datetime import datetime
from operator import itemgetter
import math

URL = "https://orteil.dashnet.org/cookieclicker/"

SAVE_DATA_FILENAME = "save_data.txt"
SAVE_DATA_BACKUP_COUNT = 10
SAVE_DATA_AUTO_HOURS = 6

BUILDINGS_BULK_IDS = {
    1: 2,
    10: 3,
    100: 4,
}

UPGRADES_ALLOWED = {
    "prestige": -1,
    "kitten": -1,
    "tech": [65, 66, 67, 68, 70, 71, 72, 73, 87],
    "": -1,
    "cookie": -1,
}

PURCHASE_AUTO_MINUTES = 15

ELDER_PLEDGE_ID = 74

INTERACTION_DELAY = 1
ELEMENT_WAIT_DELAY = 5
THREAD_DELAY = 5

MILLNAMES = [
    '',
    ' Thousand',
    ' Million',
    ' Billion',
    ' Trillion',
    ' Quadrillion',
    ' Quintillion',
    ' Sextillion',
    ' Septillion',
    ' Octillion',
    ' Nonillion',
    ' Decillion',
    ' Undecillion',
    ' Duodecillion',
    ' Tredecillion',
    ' Quattuordecillion',
    ' Quindecillion',
    ' Sexdecillion',
    ' Septendecillion',
    ' Octodecillion',
    ' Novemdecillion',
    ' Vigintillion',
]


def millify(n: float) -> str:
    """Convert large number to human friendly string."""
    # From https://stackoverflow.com/a/3155023
    millidx = max(0, min(len(MILLNAMES) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.3f}{}'.format(n / 10 ** (3 * millidx), MILLNAMES[millidx]).lower()


class Clicker:
    """Open game in browser. Set up game. Import save data (if found). Start clicking if save data imported."""

    def __init__(self):
        # Set up browser driver.
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(name="detach", value=True)
        chrome_options.add_argument("--mute-audio")
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
            cookie_thread = Thread(target=self._cookie_click)
            cookie_thread.start()

            # Start wrinkler popping thread.
            wrinkler_thread = Thread(target=self._wrinkler_pop)
            wrinkler_thread.start()

            # Start elder pledge thread.
            elder_pledge_thread = Thread(target=self._elder_pledge)
            elder_pledge_thread.start()

            # Start auto save thread.
            auto_save_thread = Thread(target=self._auto_save)
            auto_save_thread.start()

            # Start auto purchase thread.
            auto_purchase_thread = Thread(target=self._auto_purchase_thread)
            auto_purchase_thread.start()

    def get_clicking_status(self) -> bool:
        return self.clicking_event.is_set()

    def _cookie_click(self):
        """Repeatedly click the big cookie."""
        # Continue until requested to stop.
        while self.clicking_event.is_set():
            # Get number of golden cookies.
            golden_cookie_count = int(self.driver.execute_script('return Game.shimmers.length;'))

            # Pop on any golden cookies found (including wrath, reindeer, etc.).
            for i in range(0, golden_cookie_count):
                try:
                    self.driver.execute_script(f'Game.shimmers[{i}].pop();')
                except JavascriptException:
                    pass

            # Click the big cookie.
            self.driver.execute_script('Game.ClickCookie();')

    def _wrinkler_pop(self):
        """Periodically check for any spawned wrinklers and pop them."""
        # Continue until requested to stop.
        while self.clicking_event.is_set():
            # https://www.reddit.com/r/CookieClicker/comments/hl5e8i/shiny_wrinkler_and_a_javascript_code_for/
            # Javascript to pop any spawned wrinklers.
            # type == 0 to only pop non-shiny wrinklers
            # sucked > 0 to ensure wrinkler touches cookie and starts eating
            try:
                self.driver.execute_script(
                    'for (var i in Game.wrinklers)'
                    '{'
                    '   if (Game.wrinklers[i].type == 0 && Game.wrinklers[i].sucked > 0)'
                    '       {Game.wrinklers[i].hp = 0;'
                    '   }'
                    '}'
                )
            except JavascriptException:
                pass

            # Throttle the next wrinkler check.
            time.sleep(THREAD_DELAY)

    def _elder_pledge(self):
        """Periodically check if the elder pledge is unlocked, and elder pledge remaining time has run out.
        If so, automatically purchase a new elder pledge."""
        # Continue until requested to stop.
        while self.clicking_event.is_set():
            # Get elder pledge unlocked status.
            pledge_unlocked = int(self.driver.execute_script(f'return Game.UpgradesById[{ELDER_PLEDGE_ID}].unlocked;'))

            # Check if elder pledge is unlocked.
            if pledge_unlocked == 1:
                # Get elder pledge remaining time.
                pledge_time = int(self.driver.execute_script(f'return Game.pledgeT;'))

                # Check if elder pledge time has run out.
                if pledge_time <= 0:
                    try:
                        # Purchase elder pledge.
                        self.driver.execute_script(f'return Game.UpgradesById[{ELDER_PLEDGE_ID}].click();')
                    except JavascriptException:
                        pass

            # Throttle the next elder pledge check.
            time.sleep(THREAD_DELAY)

    def purchase_building(self, count: int = 1, bulk: bool = False):
        """Purchase most efficient affordable building, up to a maximum of 'count'. Default 1."""
        # Determine bulk purchasing.
        # No bulk purchasing.
        if not bulk:
            bulk_quantity = 1
        # Purchase bulk in 100 quantities.
        elif count // 100 > 0:
            bulk_quantity = 100
        # Purchase bulk in 10 quantities.
        elif count // 10 > 0:
            bulk_quantity = 10
        # Purchase bulk in 1 quantity.
        else:
            bulk_quantity = 1

        # Set bulk purchasing mode.
        self.driver.execute_script(f'Game.storeBulkButton({BUILDINGS_BULK_IDS[bulk_quantity]});')

        # Continue purchasing up to maximum requested buildings.
        while count // bulk_quantity > 0:
            # If purchase was not successful (not enough cookies in bank), end while loop.
            if not self._purchase_best_building(bulk_quantity):
                break

            count -= bulk_quantity

        # Restore bulk purchasing to 1.
        self.driver.execute_script(f'Game.storeBulkButton({BUILDINGS_BULK_IDS[1]});')
        print()

    def _purchase_best_building(self, bulk_quantity: int = 1) -> bool:
        """Purchase the most efficient affordable building. Return True if purchase was successful, otherwise False."""
        # Store list.
        store = []

        # Get number of store items.
        store_count = int(self.driver.execute_script('return Game.ObjectsById.length;'))

        # Get global cps multiplier.
        global_cps_mult = float(self.driver.execute_script(f'return Game.globalCpsMult;'))

        # Get number of cookies in bank.
        cookies = float(self.driver.execute_script(f'return Game.cookies;'))

        # Examine each store item.
        for i in range(0, store_count):
            # Determine if store item is available or locked.
            store_item_locked = int(self.driver.execute_script(f'return Game.ObjectsById[{i}].locked;'))

            # Store item is available (not locked).
            if store_item_locked == 0:
                # Get store item name.
                store_item_name = self.driver.execute_script(f'return Game.ObjectsById[{i}].dname;')

                # Get store item price.
                store_item_price = int(self.driver.execute_script(f'return Game.ObjectsById[{i}].bulkPrice;'))

                # Get store item cps.
                # Alternate cps formula from source code: (me.storedTotalCps / me.amount) * Game.globalCpsMult
                store_item_cps = float(
                    self.driver.execute_script(
                        f'return Game.ObjectsById[{i}].storedCps;')) * bulk_quantity * global_cps_mult

                # Proceed if store item is purchasable (have enough cookies in bank).
                if cookies >= store_item_price:
                    # Calculate store item efficiency.
                    store_item_efficiency = (store_item_cps * global_cps_mult) / store_item_price
                else:
                    # Mark store item as not purchasable.
                    store_item_efficiency = -1

                # If store item is purchasable, add to store list.
                if store_item_efficiency != -1:
                    store.append(
                        {
                            "id": i,
                            "name": store_item_name,
                            "price": store_item_price,
                            "cps": store_item_cps,
                            "efficiency": store_item_efficiency,
                        }
                    )

        # Sort store list by efficiency, from largest to smallest.
        store = sorted(store, key=itemgetter('efficiency'), reverse=True)

        # Verify at least one store item exists.
        if len(store) > 0:
            # Purchase most efficient store item.
            self.driver.execute_script(f'Game.ClickProduct({store[0]["id"]});')
            print(f"Purchased {bulk_quantity} x {store[0]["name"]} for {millify(store[0]["price"])} cookies, "
                  f"generating {millify(store[0]["cps"])} cps")

            # Return True indicating successful purchase.
            return True

        # Return False indicating no successful purchase.
        return False

    def purchase_upgrade(self, count: int = 1):
        """Purchase next allowed upgrade, up to a maximum of 'count'. Default 1."""
        # Continue purchasing up to maximum requested upgrades.
        while count > 0:
            # If purchase was not successful (not enough cookies in bank), end while loop.
            if not self._purchase_next_upgrade():
                break

            count -= 1

        print()

    def _purchase_next_upgrade(self) -> bool:
        """Purchase the next allowed upgrade. Return True if purchase was successful, otherwise False."""
        # Get number of upgrades in store.
        upgrade_count = int(self.driver.execute_script('return Game.UpgradesInStore.length;'))

        # Get number of cookies in bank.
        cookies = float(self.driver.execute_script(f'return Game.cookies;'))

        try:
            # Examine each upgrade.
            for i in range(0, upgrade_count):
                # Get updated number of upgrades in store every iteration.
                upgrade_count_updated = int(self.driver.execute_script('return Game.UpgradesInStore.length;'))

                # Confirm current upgrade index is still valid (sometimes store can update during
                # for loop and can cause an error).
                if i < upgrade_count_updated:
                    # Determine if store item is available or locked.
                    upgrade_unlocked = int(self.driver.execute_script(f'return Game.UpgradesInStore[{i}].unlocked;'))

                    # Upgrade is available (not locked).
                    if upgrade_unlocked == 1:
                        # Get upgrade name.
                        upgrade_name = self.driver.execute_script(f'return Game.UpgradesInStore[{i}].dname;')

                        # Get upgrade id.
                        upgrade_id = int(self.driver.execute_script(f'return Game.UpgradesInStore[{i}].id;'))

                        # Get upgrade price.
                        upgrade_price = int(self.driver.execute_script(f'return Game.UpgradesInStore[{i}].basePrice;'))

                        # Get upgrade purchase status.
                        upgrade_bought = int(self.driver.execute_script(f'return Game.UpgradesInStore[{i}].bought;'))

                        # Get upgrade type.
                        upgrade_pool = self.driver.execute_script(f'return Game.UpgradesInStore[{i}].pool;')

                        # Check if upgrade not bought, is in list of allowed upgrades and have enough cookies.
                        if upgrade_bought == 0 and upgrade_pool in UPGRADES_ALLOWED and cookies >= upgrade_price:
                            # Check if we can purchase any upgrade in pool or only certain ones.
                            if UPGRADES_ALLOWED[upgrade_pool] == -1 or upgrade_id in UPGRADES_ALLOWED[upgrade_pool]:
                                # Purchase upgrade.
                                self.driver.execute_script(f'return Game.UpgradesInStore[{i}].click();')
                                print(f"Purchased '{upgrade_name}' for {millify(upgrade_price)} cookies")

                                # Return True to indicate successful purchase.
                                return True

        except JavascriptException:
            pass

        # Return False to indicate no successful purchase.
        return False

    def save_file(self):
        """Export save data to file."""
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

    def _auto_save(self):
        """Automatically save the game at defined interval."""
        # Set next auto save interval.
        auto_save_next = time.time() + SAVE_DATA_AUTO_HOURS * 3600

        # Continue until requested to stop.
        while self.clicking_event.is_set():
            # Check if we have reached the auto save interval.
            if time.time() >= auto_save_next:
                # Save the game.
                self.save_file()

                # Set next auto save interval.
                auto_save_next = time.time() + SAVE_DATA_AUTO_HOURS * 3600

            # Throttle the next auto save check.
            time.sleep(THREAD_DELAY)

    def _auto_purchase_thread(self):
        """Automatically purchase all available upgrades and buildings at defined intervals."""
        # Set next auto purchase interval.
        auto_purchase = time.time() + PURCHASE_AUTO_MINUTES * 60

        # Continue until requested to stop.
        while self.clicking_event.is_set():
            # Check if we have reached the auto purchase interval.
            if time.time() >= auto_purchase:
                # Purchase all available buildings and upgrades.
                self.auto_purchase()

                # Set next auto purchase interval.
                auto_purchase = time.time() + PURCHASE_AUTO_MINUTES * 60

            # Throttle the next auto save check.
            time.sleep(THREAD_DELAY)

    def auto_purchase(self):
        """Automatically purchase all available upgrades and buildings."""
        # Purchase all available upgrades.
        # Purchase all upgrades if "Inspired checklist" is unlocked.
        upgrades_buy_all_status = self.driver.execute_script(f'return Game.storeBuyAll();')
        # Otherwise purchase manually
        if not upgrades_buy_all_status:
            while self._purchase_next_upgrade():
                pass

        # Set bulk purchasing mode x100.
        self.driver.execute_script(f'Game.storeBulkButton({BUILDINGS_BULK_IDS[100]});')

        # Purchase all available buildings.
        while self._purchase_best_building(100):
            pass

        # Set bulk purchasing mode x10.
        self.driver.execute_script(f'Game.storeBulkButton({BUILDINGS_BULK_IDS[10]});')

        # Purchase all available buildings.
        while self._purchase_best_building(10):
            # Purchase all upgrades if "Inspired checklist" is unlocked.
            self.driver.execute_script(f'Game.storeBuyAll();')

        # Set bulk purchasing mode x1.
        self.driver.execute_script(f'Game.storeBulkButton({BUILDINGS_BULK_IDS[1]});')

        # Purchase all available upgrades again.
        # Purchase all upgrades if "Inspired checklist" is unlocked.
        upgrades_buy_all_status = self.driver.execute_script(f'return Game.storeBuyAll();')
        # Otherwise purchase manually
        if not upgrades_buy_all_status:
            while self._purchase_next_upgrade():
                pass

    def quit(self, save: bool = True):
        """Save the game data to file. Quit the game."""
        # Stop clicking threads.
        if self.clicking_event.is_set():
            self.clicking_event.clear()

            # Wait for threads to end.
            time.sleep(THREAD_DELAY + 1)

        # Save game data to file if requested.
        if save:
            self.save_file()

        # Quit browser.
        self.driver.quit()

# Tips https://gist.github.com/ob-ivan/6800011
