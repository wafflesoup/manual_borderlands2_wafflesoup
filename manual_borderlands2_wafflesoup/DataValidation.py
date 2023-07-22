import logging
import re
import json

class ValidationError(Exception):
    pass

class DataValidation():
    game_table = {}
    item_table = []
    location_table = []
    region_table = {}

    @staticmethod
    def outputExpectedGameNames():
        logging.warning("With the information in your game.json, ")
        logging.warning("  - The expected game name in your YAML is: Manual_%s_%s" % (DataValidation.game_table["game"], DataValidation.game_table["player"]))
        logging.warning("  - The expected apworld filename and directory is: manual_%s_%s" % (DataValidation.game_table["game"].lower(), DataValidation.game_table["player"].lower()))
        logging.warning("")
        logging.warning("")

    @staticmethod
    def checkItemNamesInLocationRequires():
        for location in DataValidation.location_table:
            if "requires" not in location:
                continue

            if isinstance(location["requires"], str):
                # parse user written statement into list of each item
                reqires_raw = re.split('(\AND|\)|\(|OR|\|)', location["requires"])
                remove_spaces = [x.strip() for x in reqires_raw]
                remove_empty = [x for x in remove_spaces if x != '']
                requires_list = [x for x in remove_empty if x != '|']

                for i, item in enumerate(requires_list):
                    if item.lower() == "or" or item.lower() == "and" or item == ")" or item == "(":
                        continue
                    else:
                        item_parts = item.split(":")
                        item_name = item

                        if len(item_parts) > 1:
                            item_name = item_parts[0]

                        item_exists = len([item["name"] for item in DataValidation.item_table if item["name"] == item_name]) > 0

                        if not item_exists:
                            raise ValidationError("Item %s is required by location %s but is misspelled or does not exist." % (item_name, location["name"]))
                        
            else:  # item access is in dict form
                for item in location["requires"]:
                    # if the require entry is an object with "or" or a list of items, treat it as a standalone require of its own
                    if (isinstance(item, dict) and "or" in item and isinstance(item["or"], list)) or (isinstance(item, list)):
                        or_items = item
                        
                        if isinstance(item, dict):
                            or_items = item["or"]

                        for or_item in or_items:
                            or_item_parts = or_item.split(":")
                            or_item_name = or_item

                            if len(or_item_parts) > 1:
                                or_item_name = or_item_parts[0]

                            item_exists = len([item["name"] for item in DataValidation.item_table if item["name"] == or_item_name]) > 0

                            if not item_exists:
                                raise ValidationError("Item %s is required by location %s but is misspelled or does not exist." % (or_item_name, location["name"]))
                    else:
                        item_parts = item.split(":")
                        item_name = item
                        
                        if len(item_parts) > 1:
                            item_name = item_parts[0]

                        item_exists = len([item["name"] for item in DataValidation.item_table if item["name"] == item_name]) > 0

                        if not item_exists:
                            raise ValidationError("Item %s is required by location %s but is misspelled or does not exist." % (item_name, location["name"]))

    @staticmethod
    def checkItemNamesInRegionRequires():
        for region_name in DataValidation.region_table:
            region = DataValidation.region_table[region_name]

            if "requires" not in region:
                continue

            if isinstance(region["requires"], str):
                # parse user written statement into list of each item
                reqires_raw = re.split('(\AND|\)|\(|OR|\|)', region["requires"])
                remove_spaces = [x.strip() for x in reqires_raw]
                remove_empty = [x for x in remove_spaces if x != '']
                requires_list = [x for x in remove_empty if x != '|']

                for i, item in enumerate(requires_list):
                    if item.lower() == "or" or item.lower() == "and" or item == ")" or item == "(":
                        continue
                    else:
                        item_parts = item.split(":")
                        item_name = item

                        if len(item_parts) > 1:
                            item_name = item_parts[0]

                        item_exists = len([item["name"] for item in DataValidation.item_table if item["name"] == item_name]) > 0

                        if not item_exists:
                            raise ValidationError("Item %s is required by region %s but is misspelled or does not exist." % (item_name, region_name))
                        
            else:  # item access is in dict form
                for item in region["requires"]:
                    # if the require entry is an object with "or" or a list of items, treat it as a standalone require of its own
                    if (isinstance(item, dict) and "or" in item and isinstance(item["or"], list)) or (isinstance(item, list)):
                        or_items = item
                        
                        if isinstance(item, dict):
                            or_items = item["or"]

                        for or_item in or_items:
                            or_item_parts = or_item.split(":")
                            or_item_name = or_item

                            if len(or_item_parts) > 1:
                                or_item_name = or_item_parts[0]

                            item_exists = len([item["name"] for item in DataValidation.item_table if item["name"] == or_item_name]) > 0

                            if not item_exists:
                                raise ValidationError("Item %s is required by region %s but is misspelled or does not exist." % (or_item_name, region_name))
                    else:
                        item_parts = item.split(":")
                        item_name = item
                        
                        if len(item_parts) > 1:
                            item_name = item_parts[0]

                        item_exists = len([item["name"] for item in DataValidation.item_table if item["name"] == item_name]) > 0

                        if not item_exists:
                            raise ValidationError("Item %s is required by region %s but is misspelled or does not exist." % (item_name, region_name))

    @staticmethod
    def checkRegionNamesInLocations():
        for location in DataValidation.location_table:
            if "region" not in location:
                continue

            region_exists = len([name for name in DataValidation.region_table if name == location["region"]]) > 0
            
            if not region_exists:
                raise ValidationError("Region %s is set for location %s, but the region is misspelled or does not exist." % (location["region"], location["name"]))

    @staticmethod
    def checkItemsThatShouldBeRequired():
        for item in DataValidation.item_table:
            # if the item is already progression, no need to check
            if "progression" in item and item["progression"]:
                continue

            # check location requires for the presence of item name
            for location in DataValidation.location_table:
                if "requires" not in location:
                    continue

                # convert to json so we don't have to guess the data type
                location_requires = json.dumps(location["requires"])

                if item["name"] in location_requires:
                    raise ValidationError("Item %s is required by location %s, but the item is not marked as progression." % (item["name"], location["name"]))

            # check region requires for the presence of item name
            for region_name in DataValidation.region_table:
                region = DataValidation.region_table[region_name]

                if "requires" not in region:
                    continue

                # convert to json so we don't have to guess the data type
                region_requires = json.dumps(region["requires"])

                if item["name"] in region_requires:
                    raise ValidationError("Item %s is required by region %s, but the item is not marked as progression." % (item["name"], key))

    @staticmethod
    def checkRegionsConnectingToOtherRegions():
        for region_name in DataValidation.region_table:
            region = DataValidation.region_table[region_name]

            if "connects_to" not in region:
                continue

            for connecting_region in region["connects_to"]:
                region_exists = len([name for name in DataValidation.region_table if name == connecting_region]) > 0

                if not region_exists:
                    raise ValidationError("Region %s connects to a region %s, which is misspelled or does not exist." % (region_name, connecting_region))

    @staticmethod
    def checkForMultipleVictoryLocations():
        victory_count = len([location["name"] for location in DataValidation.location_table if "victory" in location and location["victory"]])

        if victory_count > 1:
            raise ValidationError("There are %s victory locations defined, but there should only be 1." % (str(victory_count)))
