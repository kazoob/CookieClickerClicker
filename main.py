from clicker import Clicker

# Create clicker class.
clicker = Clicker()

menu_input: str = ""

# Display menu.
while menu_input != "q":
    print("Menu: ")
    print("c = Toggle clicking")
    print("p = Purchase best building")
    print("s = Save game to file")
    print("q = Quit")
    print()
    menu_input = input("Enter your selection: ").lower()
    print()

    # Start / stop clicking.
    if menu_input == "c":
        clicker.toggle_clicking()
    # Save game data to file.
    elif menu_input == "s":
        clicker.save_file()
    elif menu_input == "p":
        clicker.purchase_best_building()

# Quit clicker.
clicker.quit()
