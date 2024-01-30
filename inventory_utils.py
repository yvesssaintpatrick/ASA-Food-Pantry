from constants import *
from spreadsheets import get_spreadsheet_values
from spreadsheets import get_spreadsheet_service
from spreadsheets import clear_spreadsheet_range
from spreadsheets import append_rows_to_spreadsheet


def commit_inventory_update(new_inventory, inv_list):
    '''
    Using the given new inventory data, commits the updated inventory to the
    database and replaces the tuple array in the inv_list instance.
    '''
    inv_list.full_inventory = [tuple(item) for item in new_inventory]
    inv_list.selected_items = {}
    spreadsheet_service = get_spreadsheet_service()

    clear_spreadsheet_range(
        spreadsheet_id=SPREADSHEET_ID,
        range=f'{PANTRY_STOCK_SHEET}!A2:ZZZ',
        spreadsheet_service=spreadsheet_service)

    append_rows_to_spreadsheet(
        spreadsheet_id=SPREADSHEET_ID,
        spreadsheet_range=f'{PANTRY_STOCK_SHEET}!A2:ZZZ',
        rows=new_inventory,
        spreadsheet_service=spreadsheet_service)


def isdigit(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


def get_inventory_data():
    '''
    Fetch inventory data from database.
    '''
    sheet_values = get_spreadsheet_values(
        spreadsheet_id=SPREADSHEET_ID,
        spreadsheet_range=f"{PANTRY_STOCK_SHEET}!A1:ZZZ")

    return (sheet_values[0], sheet_values[1:])


def get_updated_inventory(inv_list):
    '''
    Generate an updated inventory based on the selected items and their quantities.

    Params:
        inv_list (InventoryList): An object representing the inventory list.

    Returns:
        list: A new inventory list with quantities updated for selected items.
    '''
    updated_inventory = []
    for item_tuple in inv_list.full_inventory:
        if item_tuple in inv_list.selected_items: # Item is selected
            updated_item = []

            for attr in item_tuple:
                if isdigit(attr):  # The only attribute we're changing is the qty
                    updated_item.append(inv_list.selected_items[item_tuple])
                else:
                    updated_item.append(attr)

            updated_inventory.append(updated_item)

        else:  # The item wasn't selected; don't change it
            updated_inventory.append(item_tuple)

    return updated_inventory
