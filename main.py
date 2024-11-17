from clicker import Clicker
import time

clicker = Clicker()

menu_input: str = ""
while menu_input != "q":
    print("Menu: ")
    print("c = Enable / disable clicking")
    print("p = Purchase upgrade")
    print("s = Save game to file")
    print("q = Quit")
    print()
    menu_input = input("Enter your selection: ").lower()

    if menu_input == "c":
        clicker.toggle_clicking()
    elif menu_input == "s":
        clicker.save_file()

    print()

# Quit browser.
clicker.quit()
