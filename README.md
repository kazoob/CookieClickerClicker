
  
# CookieClickerClicker
A personal clicking bot and purchasing automator for the browser game Cookie Clicker.

## Prerequisites:

 1. Python3
 2. Selenium module
`pip install selenium`


## Run:

`python3 main.py`


## Menu:

    c     = Enable/Disable big cookie / golden cookie / special cookie clicking
    e     = Enable/Disable Elder Pledge purchase
    d     = Enable/Disable auto purchase
    a     = Purchase all available upgrades and buildings
    p     = Purchase best building
    p #   = Purchase best # buildings (individually)
    p # b = Purchase best # buildings (bulk)    
    u     = Purchase next upgrade    
    u #   = Purchase next # upgrades    
    s     = Save game to file    
    q     = Quit (save)
    x     = Quit (do not save)

## Functionality

If cookie clicking is enabled, the following tasks are performed:

 1. Big cookie clicking **as fast as possible**.
 2. Golden cookie clicking **as fast as possible**.
 3. Special cookie (wrath, reindeer, etc.) clicking **as fast as possible**.
 4. Wrinkler popping (**when they attach**) to the big cookie **every 5 seconds**.
 5. Fortune check and click **every 3 seconds**.
 6. Elder Pledge purchase **every 5 seconds** (if also enabled).
 7. Upgrades and buildings purchase **every 15 minutes** (if also enabled).
 8. Save the game to file **every 6 hours**.

## Known Issues

 1. When the auto upgrades and buildings purchase routine runs, the menu will no longer be displayed in the console. Simply press 'Enter' to restore the menu.