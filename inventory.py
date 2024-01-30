from spreadsheets import get_spreadsheet_values
from spreadsheets import update_spreadsheet_values
from constants import SPREADSHEET_ID, PANTRY_STOCK_SHEET
from inventory_utils import *
from add_inventory_item import open_add_stock_window

import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk

from functools import partial
from tkinter.messagebox import askyesno


def handle_add_item_modal(inv_list):
    modal_window = open_add_stock_window(inv_list.headers)
    inv_list.wait_window(modal_window)
    refresh_inventory_list(inv_list)


def refresh_inventory_list(inv_list):
    inv_headers, inv_items = get_inventory_data()
    inv_list.headers = inv_headers
    inv_list.full_inventory = [tuple(item) for item in inv_items]
    append_inventory_list(inv_list, inv_headers, inv_items)


def on_item_click(event, inv_list, quantity_spinbox):
    """
    Handle the click event on an item in the inventory list.
    """

    selected_item = inv_list.view.selection()

    if selected_item:
        item_id = selected_item[0]
        item_data = inv_list.view.item(item_id, 'values')

        quantity_spinbox.delete(0, tk.END)
        quantity_spinbox.insert(
            0, item_data[inv_list.headers.index("Quantity")])


def display_search_results(search_sv, inventory_list):
    '''
    Filter items in the current inventory list based on entry in search bar.
    Search is not case-sensitive and filters based on any of the available
    attributes.

    Params
        search_sv (tk.StringVar): StringVar object connected to search bar
        inventory_list (tk.Frame): An object representing the inventory list
    '''
    filter = search_sv.get().lower()
    filtered_list = []

    if filter:
        for item_tuple in inventory_list.full_inventory:
            for item_attr in item_tuple:
                if filter in item_attr.lower():
                    filtered_list.append(item_tuple)
                    continue
    else:  # Use unfiltered list
        filtered_list = inventory_list.full_inventory

    append_inventory_list(
        inventory_list, inventory_list.headers, filtered_list)


def get_item_tuple_qty(item_tuple):
    '''
    Get the quantity of an item given it's attribute tuple.

    *Assumes that the only number in an item's attributes will
    always represent the quantity.
    '''
    for item_attr in item_tuple:
        if isdigit(item_attr):
            return int(item_attr)
    return 0  # Why did we get here?


def decrease_selected_qty(item_tuple, quantity_spinbox):
    '''
    Decrease the selected quantity of an item's quantity spinbox.
    '''
    current_value = int(quantity_spinbox.get())
    new_value = max(0, current_value - 1)
    quantity_spinbox.delete(0, tk.END)
    quantity_spinbox.insert(0, new_value)


def increase_selected_qty(item_tuple, quantity_spinbox):
    '''
    Increase the selected quantity of an item's quantity spinbox.
    '''
    current_value = int(quantity_spinbox.get())
    new_value = current_value + 1
    quantity_spinbox.delete(0, tk.END)
    quantity_spinbox.insert(0, new_value)


def update_view_tree(inv_list, quantity_spinbox):
    """
    Update the quantity of a selected item in the view tree and synchronize
    the changes with the underlying data and Google Sheets.
    """
    selected_item = inv_list.view.selection()

    if selected_item:
        item_id = selected_item[0]
        item_data = inv_list.view.item(item_id, 'values')
        new_quantity = int(quantity_spinbox.get())

        inv_list.view.item(item_id, values=(
            item_data[0], new_quantity, item_data[2]))

        for item_tuple in inv_list.full_inventory:
            if item_data[0] == item_tuple[0]:
                if len(item_tuple) == 3 and item_tuple[2] != item_data[2]:
                    # If it has a dietary restriction that does not match
                    continue

                # Found the correct tuple, update it
                inv_list.selected_items[item_tuple] = new_quantity
                break

        commit_inventory_update(get_updated_inventory(inv_list), inv_list)


def remove_inventory_item(inv_list):
    '''
    Fetches the currently selected inventory item and removes it from
    the database and subsequently refreshes the list to display the
    updated inventory.
    '''
    selected_item = inv_list.view.selection()

    item_id = selected_item[0]
    item_data = inv_list.view.item(item_id, 'values')

    for item_tuple in inv_list.full_inventory:
        if item_tuple[0] == item_data[0]:
            if len(item_tuple) == 3 and item_tuple[2] != item_data[2]:
                # If it has a dietary restriction that does not match
                continue
            inv_list.full_inventory.remove(item_tuple)
            break
    commit_inventory_update(inv_list.full_inventory, inv_list)
    refresh_inventory_list(inv_list)


def destroy_frame_children(frame):
    '''
    Destroy all children within a frame, does not destroy
    the frame itself.
    '''
    for child in frame.winfo_children():
        child.destroy()


def append_inventory_list(inv_list, inv_headers, inv_items):
    '''
    Create table of item's given the list of headers and item tuples.
    Note: item attribute lists must be of type tuple. They are hashed 
          into dictionary keys and therefore must be immutable. 

    headers: ["Item", "Quantity", ...]
    items: list of tuples [("apple", "vegetarian"), ...]
    '''
    destroy_frame_children(inv_list)
    inv_list.view = ttk.Treeview(
        inv_list, columns=inv_headers, show="headings", height=20)
    inv_list.view.pack(fill='both', expand=True)

    for header in inv_headers:
        inv_list.view.heading(header, text=header)
        inv_list.view.column(header, anchor="center", width=100)

    for item_tuple in inv_items:
        inv_list.view.insert("", "end", values=item_tuple)


def build_inventory_toplevel():
    inv_window = tk.Toplevel()
    inv_window.title("Manage Inventory")
    inv_window.geometry('610x400')
    inv_frame = ttk.Frame(inv_window)
    inv_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
    inv_window.grid_rowconfigure(0, weight=1)
    inv_window.grid_columnconfigure(0, weight=1)

    inv_frame.grid_rowconfigure(0, weight=1)
    inv_frame.grid_columnconfigure(0, weight=1)

    return inv_window


def build_inventory_search_bar(root, inventory_list):
    nav_frame = tk.Frame(root)
    nav_frame.grid(row=0, sticky='nw', padx=20, pady=0)

    search_sv = tk.StringVar()
    search_bar = tk.Entry(nav_frame, width=20, textvariable=search_sv)
    search_bar.pack(side=tk.RIGHT)

    search_text = tk.Label(nav_frame, text="Search")
    search_text.pack(side=tk.RIGHT)

    search_sv.trace("w", callback=lambda name, index, mode, sv=search_sv,
                    ls=inventory_list: display_search_results(sv, ls))

    return search_bar


def build_inventory_list(inv_frame):
    inv_headers, inv_items = get_inventory_data()
    inv_list = ttk.Frame(inv_frame, padding=5)

    inv_list.headers = inv_headers
    inv_list.full_inventory = [tuple(item) for item in inv_items]
    inv_list.selected_items = {}

    inv_list.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

    append_inventory_list(inv_list, inv_headers, inv_items)

    return inv_list


def build_inventory_manage_buttons(inv_frame, inv_list):
    btn_frame = ttk.LabelFrame(inv_frame, padding=20)
    btn_frame.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)

    quantity_spinbox = ttk.Spinbox(btn_frame, from_=0, to=100)
    quantity_spinbox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    update_button = ttk.Button(
        btn_frame, text="Update", command=lambda: update_view_tree(inv_list, quantity_spinbox))
    update_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    separator = ttk.Separator(btn_frame, orient='horizontal')
    separator.grid(row=3, column=0, pady=35, sticky="ew")

    new_item_button = ctk.CTkButton(btn_frame, text="ADD NEW ITEM", text_color="#b50404",
                                    fg_color="white", border_color="#b50404", border_width=4, hover=False,
                                    command=partial(handle_add_item_modal, inv_list))

    new_item_button.grid(row=4, column=0, padx=5, pady=7, sticky="ew")

    inv_list.view.bind(
        '<ButtonRelease-1>', lambda event: on_item_click(event, inv_list, quantity_spinbox))

    remove_item_button = ctk.CTkButton(btn_frame, text="REMOVE ITEM", text_color="#b50404",
                                       fg_color="white", border_color="#b50404", border_width=4, hover=False,
                                       command=partial(remove_inventory_item, inv_list))

    remove_item_button.grid(row=5, column=0, padx=5, pady=7, sticky="ew")

    return btn_frame


# Opening and Closing of Inventory Window in main application
inv_window = None


def inventory_window_open():
    return inv_window and inv_window.winfo_exists()


def close_inventory_window():
    global inv_window
    if inventory_window_open():
        inv_window.destroy()
        inv_window = None


def open_inventory_window():
    global inv_window
    if inventory_window_open():
        return

    inv_window = build_inventory_toplevel()
    inv_list = build_inventory_list(inv_window, )
    search_bar = build_inventory_search_bar(inv_window, inv_list)
    button_frame = build_inventory_manage_buttons(inv_window, inv_list)
    inv_window.protocol("WM_DELETE_WINDOW", close_inventory_window)


def inventory_window():
    if not inventory_window_open():
        open_inventory_window()
    else:
        inv_window.lift()
        inv_window.focus_force()
