import json
import os
import pkgutil
import sys

from .DataValidation import DataValidation, ValidationError

# blatantly copied from the minecraft ap world because why not
def load_data_file(*args) -> dict:
    fname = os.path.join("data", *args)

    try:
        filedata = json.loads(pkgutil.get_data(__name__, fname).decode())
    except:
        filedata = []

    return filedata

game_table = load_data_file('game.json')
item_table = load_data_file('items.json')
#progressive_item_table = load_data_file('progressive_items.json')
progressive_item_table = {}
location_table = load_data_file('locations.json')
region_table = load_data_file('regions.json')

# seed all of the tables for validation
DataValidation.game_table = game_table
DataValidation.item_table = item_table
DataValidation.location_table = location_table
DataValidation.region_table = region_table

try:
    # check that requires have correct item names in locations and regions
    DataValidation.checkItemNamesInLocationRequires()
    DataValidation.checkItemNamesInRegionRequires()

    # check that region names are correct in locations
    DataValidation.checkRegionNamesInLocations()

    # check that items that are required by locations and regions are also marked required
    DataValidation.checkItemsThatShouldBeRequired()

    # check that regions that are connected to are correct
    DataValidation.checkRegionsConnectingToOtherRegions()

    # check that the apworld creator didn't specify multiple victory conditions
    DataValidation.checkForMultipleVictoryLocations()
except ValidationError as e:
    print("\nValidationError: %s\n\n" % (e))
    print("You can close this window.\n")
    keeping_terminal_open = input("If you are running from a terminal, press Ctrl-C followed by ENTER to break execution.")
    
# show the apworld creator what their game name and filename should be
# commenting this out for now because it mainly just causes confusion for users
# DataValidation.outputExpectedGameNames()