from BaseClasses import Entrance, MultiWorld, Region
from .Data import region_table
from .Locations import ManualLocation
from ..AutoWorld import World

if not region_table:
    region_table = {}

regionMap = { **region_table }
starting_regions = [ name for name in regionMap if "starting" in regionMap[name].keys() and regionMap[name]["starting"] ]

if len(starting_regions) == 0:
    starting_regions = region_table.keys() # the Manual region connects to all user-defined regions automatically if you specify no starting regions

regionMap["Manual"] = {
    "requires": [],
    "connects_to": starting_regions
}

def create_regions(base: World, world: MultiWorld, player: int): 
    # Create regions and assign locations to each region
    for region in regionMap:
        # if it's an empty or unusable region, skip it
        if not regionMap[region]: 
            continue

        exit_array = None

        if "connects_to" in regionMap[region]:
            exit_array = regionMap[region]["connects_to"]

        if not exit_array:
            exit_array = None

        new_region = create_region(base, world, player, region, [
            location["name"] for location in base.location_table if location["region"] == region
        ], exit_array)
        world.regions += [new_region]

    menu = create_region(base, world, player, "Menu", None, ["Manual"])
    world.regions += [menu]
    menuConn = world.get_entrance("MenuToManual", player)
    menuConn.connect(world.get_region("Manual", player))

    # Link regions together
    for region in regionMap:
        if "connects_to" in regionMap[region]:
            for linkedRegion in regionMap[region]["connects_to"]:
                connection = world.get_entrance(getConnectionName(region, linkedRegion), player)
                connection.connect(world.get_region(linkedRegion, player))

def create_region(base: World, world: MultiWorld, player: int, name: str, locations=None, exits=None):
    ret = Region(name, player, world)
    
    if locations:
        for location in locations:
            loc_id = base.location_name_to_id.get(location, 0)
            locationObj = ManualLocation(player, location, loc_id, ret)
            ret.locations.append(locationObj)
    if exits:
        for exit in exits:
            ret.exits.append(Entrance(player, getConnectionName(name, exit), ret))
    return ret

def getConnectionName(entranceName: str, exitName: str):
    return entranceName + "To" + exitName
