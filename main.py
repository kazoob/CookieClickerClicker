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
    if clicker.get_clicking_status():
        # Clicking is currently enabled, menu to disable
        clicking_string = "Disable"
    else:
        # Clicking is currently disabled, menu to enable
        clicking_string = "Enable"

    # Display correct enable / disable clicking string
    if clicker.get_elder_pledge_status():
        # Elder Pledge is currently enabled, menu to disable
        elder_pledge_string = "Disable"
    else:
        # Elder Pledge is currently disabled, menu to enable
        elder_pledge_string = "Enable"

    # Display correct enable / disable auto purchase string
    if clicker.get_auto_purchase_status():
        # Auto purchase is currently enabled, menu to disable
        auto_purchase_string = "Disable"
    else:
        # Auto purchase is currently disabled, menu to enable
        auto_purchase_string = "Enable"

    print("Menu: ")
    print(f"c     = {clicking_string} big cookie / golden cookie / special cookie clicking")
    print(f"e     = {elder_pledge_string} Elder Pledge purchase")
    print(f"d     = {auto_purchase_string} auto purchase")
    print("a     = Purchase all available upgrades and buildings")
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

    # TODO fix menu prompt display after auto purchase

    # Start / stop clicking.
    if menu_input.startswith("c"):
        clicker.toggle_clicking()
    # Start / stop Elder Pledge purchase.
    elif menu_input.startswith("e"):
        clicker.toggle_elder_pledge()
    # Start / stop auto purchase.
    elif menu_input.startswith("d"):
        clicker.toggle_auto_purchase()
    # Purchase all available upgrades and buildings.
    elif menu_input.startswith("a"):
        clicker.auto_purchase()
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
    # Save game data to file.
    elif menu_input.startswith("s"):
        clicker.save_file()
    # Quit and save data.
    elif menu_input.startswith("q"):
        clicker.quit(save=True)
    # Quit and do not save data.
    elif menu_input.startswith("x"):
        clicker.quit(save=False)
