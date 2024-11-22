# CookieClickerClicker

An unofficial personal clicking bot and purchasing automator for the browser game Cookie Clicker.

https://orteil.dashnet.org/cookieclicker/

## Prerequisites:

1. Chrome
2. Python3
3. Selenium module `pip install selenium`

## Run:

`python3 main.py`

## Menu:

    c     = Enable/Disable big cookie / golden cookie / special cookie clicking
    e     = Enable/Disable Elder Pledge purchase
    d     = Enable/Disable auto purchase
    a     = Purchase all available upgrades and buildings (bulk x100 and x10)
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
4. Wrinkler popping (**when they attach** to the big cookie) **every 5 seconds**.
5. Fortune click **every 3 seconds**.
6. Elder Pledge purchase **every 5 seconds** (if not disabled).
7. Upgrades and buildings purchase **every 15 minutes** (if not disabled).
8. Save the game to file **every 6 hours**.

## Examples

1. `p` will purchase the most efficient building
2. `p 9` will purchase the 9 most efficient individual buildings (bulk x1)
3. `p 20 b` will purchase the 2 most efficient groups of 10 buildings (bulk x10)
4. `p 200 b` will purchase the 2 most efficient groups of 100 buildings (bulk x100)
5. `u` will purchase the next available upgrade in the store
6. `u 9` will purchase the next 9 available upgrades in the store

## Known Issues

1. When the auto upgrades and buildings purchase routine runs, the menu will no longer be displayed in the console.
   Simply press 'Enter' to restore the menu.
