from clicker import Clicker


def get_count(text: str) -> int:
    """Return the maximum purchase count entered by the user. If no count or an error, return 1."""
    # See if user entered a purchase quantity.
    if len(text.split(" ")) >= 2:
        try:
            # Get purchase quantity
            cnt = int(text.split(" ")[1])
        except ValueError:
            # Invalid purchase quantity entered.
            cnt = 1
    # No purchase quantity entered.
    else:
        cnt = 1

    return cnt


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
    print(f"c     = {clicking_string} clicking")
    print("p     = Purchase best building")
    print("p #   = Purchase best # buildings (individually)")
    print("p # b = Purchase best # buildings (bulk)")
    print("u     = Purchase next upgrade")
    print("u #   = Purchase next # upgrades")
    print("s     = Save game to file")
    print("q     = Quit (save)")
    print("x     = Quit (do not save)")
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
        # Determine if bulk purchasing is requested.
        bulk_purchase = menu_input.endswith("b")
        # Purchase requested number of buildings (maximum).
        clicker.purchase_building(get_count(menu_input), bulk_purchase)
    # Purchase best upgrade.
    elif menu_input.startswith("u"):
        # Purchase requested number of upgrades (maximum).
        clicker.purchase_upgrade(get_count(menu_input))
    # Quit and save data.
    elif menu_input.startswith("q"):
        clicker.quit(save=True)
    # Quit and do not save data.
    elif menu_input.startswith("x"):
        clicker.quit(save=False)
