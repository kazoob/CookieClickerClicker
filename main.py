from clicker import Clicker
import time

clicker = Clicker()

menu_input: str = ""
while menu_input != "q":
    print("Menu: ")
    print("c = Enable / disable clicking")
    print("p = Purchase upgrade")
    print("q = Quit")
    menu_input = input("Enter your selection: ")

    print()

# Quit browser.
clicker.quit()
