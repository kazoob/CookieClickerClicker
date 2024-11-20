from clicker import Clicker

# Create clicker class.
clicker = Clicker()

menu_input: str = ""

# Display menu.
while menu_input != "q" and menu_input != "x":
    # Display correct enable / disable clicking string
    # Currently clicking
    if clicker.get_clicking_status():
        clicking_string = "Disable"
    # Currently not clicking
    else:
        clicking_string = "Enable"

    print("Menu: ")
    print(f"c   = {clicking_string} clicking")
    print("p   = Purchase best building")
    print("p # = Purchase best # buildings")
    print("s   = Save game to file")
    print("q   = Quit (save)")
    print("x   = Quit (do not save)")
    print()

    # Get user input.
    menu_input = input("Enter your selection: ").lower()
    print()

    # Start / stop clicking.
    if menu_input.startswith("c"):
        clicker.toggle_clicking()
    # Save game data to file.
    elif menu_input.startswith("s"):
        clicker.save_file()
    # Purchase best building.
    elif menu_input.startswith("p"):
        # See if user entered a purchase quantity.
        if len(menu_input.split(" ")) >= 2:
            try:
                # Get purchase quantity
                count = int(menu_input.split(" ")[1])
            except ValueError:
                # Invalid purchase quantity entered.
                count = 1
        # No purchase quantity entered.
        else:
            count = 1

        # Purchase requested number of buildings (maximum).
        clicker.purchase(count)
    # Quit and save data.
    elif menu_input.startswith("q"):
        clicker.quit(save=True)
    # Quit and do not save data.
    elif menu_input.startswith("x"):
        clicker.quit(save=False)
