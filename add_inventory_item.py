from spreadsheets import append_rows_to_spreadsheet
from constants import SPREADSHEET_ID, PANTRY_STOCK_SHEET
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import askyesno

from functools import partial


def build_add_stock_toplevel():
    add_stock_window = tk.Toplevel()
    add_stock_window.title("Add Item")
    add_stock_window.attributes('-topmost', True)

    return add_stock_window

def add_new_item_entry(item):
    append_rows_to_spreadsheet(spreadsheet_id=SPREADSHEET_ID, spreadsheet_range=f"{PANTRY_STOCK_SHEET}", rows=[item])

def submit_add_item_form(root):
    form_entries = root.form_entries
    form_fields = root.form_fields

    new_item = []
    for field in form_fields:
        new_item.append(form_entries[field].get())

    user_confirm = askyesno("Add New Item?", 
                            message=f"Add item: {new_item} to stock?",
                            parent=root)
    if user_confirm:
        add_new_item_entry(new_item)

    root.destroy()

def append_item_form(root, headers):
    form_entries = {}
    for field in headers:
        label = tk.Label(root, text=field)
        label.pack(side=tk.TOP, padx=10)

        entry = tk.Entry(root)
        entry.pack(side=tk.TOP, padx=10)

        form_entries[field] = entry

    root.form_entries = form_entries
    root.form_fields = headers
    
    submit_btn = tk.Button(root, text="Submit", 
            command=partial(submit_add_item_form, root))
    submit_btn.pack(padx=20, pady=20, side=tk.BOTTOM)

    
def open_add_stock_window(fields):
    window = build_add_stock_toplevel()
    append_item_form(window, fields)
    return window