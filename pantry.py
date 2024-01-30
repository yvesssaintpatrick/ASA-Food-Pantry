from constants import SCOPES
from constants import SPREADSHEET_ID
from spreadsheets import get_spreadsheet_values
from spreadsheets import clear_spreadsheet_range
from spreadsheets import get_spreadsheet_service
from inventory import inventory_window

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import textwrap
from PIL import Image, ImageTk
import os
import google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from reportlab.pdfgen.canvas import Canvas


window = tk.Tk()
window.title("ASA FOOD PANTRY")
window.geometry('1500x1000')
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

window.tk.call('source', 'Azure/azure.tcl')
window.tk.call('set_theme', 'light')


def wrap(content, leng=80):
    """
    Wrap text content to fit within specified line length.
    """
    wrapped_text = []
    if not isinstance(content, list):
        content = [content]
        wrapped_text = textwrap.wrap(str(content), leng)
    else:
        wrapped_text = textwrap.wrap(str(content), leng)
    return '\n'.join('\n'.join(line.split('\n'+'\n')) for line in wrapped_text)


def configure_treeview(columns, col_widths=None, col_anchor=None):
    """
    Configure the columns of a Treeview widget with specified names, widths, and anchor points.
    """

    for col_name in view.get_children():
        view.delete(col_name)

    view["columns"] = columns
    for col_name, width, anchor in zip(columns, col_widths, col_anchor):
        view.heading(col_name, text=col_name)
        view.column(col_name, anchor=anchor, width=width)


def main():
    """
    Fetches data from the 'ShoppingList' sheet of the Google Sheets document
    and populates a Treeview widget with the retrieved data.
    """
    columns = ("ITEMS", "QTY TOTAL", "NONE", "VEGETARIAN",
               "VEGAN", "PESCATARIAN", "HALAL", "GLUTEN-FREE", "OTHER")
    col_widths = [170, 90, 90, 100, 100, 90, 90, 90, 55]
    col_anchor = ["center", "center", "center",
                  "center", "center", "center", "center", "center", "center"]
    configure_treeview(columns, col_widths, col_anchor)

    values = get_spreadsheet_values(
        spreadsheet_id=SPREADSHEET_ID, spreadsheet_range="ShoppingList!A1:I200")

    """
    For Loop that goes through values (Food Items) and removes the first and last character in the string if it finds a bracket.
    This will get rid of the brackets on the String as the information in Values should be formated such as = [food Items]
    """
    for i in range(len(values)):
        for j in range(len(values[i])):
            if values[i][j][0] == "[":
                values[i][j] = values[i][j][1:-1]

    for item in view.get_children():
        view.delete(item)

    if values:
        for col_name in values[0]:
            view.heading(col_name, text=col_name)

        for row in values[1:]:
            view.insert("", "end", values=row)


def removeSquareBrackets(content):
    """
    Mostly uses the first if statement - Goes through the input "Content" and checks the first and last character, if it is a bracket
    the string is changed to remove the bracket
    """
    temp = ""
    if isinstance(content, str):
        for i in range(len(content)):
            if content[i] == "[":
                temp = content[i+1:]
        content = temp
        for i in range(len(content)):
            if content[i] == "]":
                temp = content[:i]
        return temp
    else:
        for i in range(len(content)):
            for j in range(len(content[i])):
                if content[i][j][0] == "[":
                    temp = content[i][j][1:-1]
        return temp


def dietry():
    """
    Fetches data from the 'ImportantIndividualOrderShoppingLists' sheet of the Google Sheets document,
    organizes the data, and populates a Treeview widget with the retrieved information.
    """
    columns = ("FULL NAME", "ALLERGY + DIET", "FOOD", "QTY")
    col_widths = [150, 600, 250, 100]
    col_anchor = ["center", "center", "center", "center"]
    configure_treeview(columns, col_widths, col_anchor)

    values = get_spreadsheet_values(
        spreadsheet_id=SPREADSHEET_ID, spreadsheet_range="ImportantIndividualOrderShoppingLists!A1:DN200")

    first_name_array = values[0][1:]
    last_name_array = values[1][1:]
    allergy_name_array = values[2][1:]
    diet_name_array = values[3][1:]
    food_data_array = values[4:]
    num = len(food_data_array)
    list = len(food_data_array[0])
    Output = []
    for i in range(list - 1):
        temp = []
        for j in range(num):
            if str(food_data_array[j][i + 1]) != '0':
                temp.append(
                    f'{food_data_array[j][0]} {food_data_array[j][i + 1]}')
        Output.append(temp)

    counter = 0
    for first_name, last_name, allergy, diet, food in zip(first_name_array, last_name_array, allergy_name_array, diet_name_array, Output):
        full_name = f"{first_name}{last_name[0]}"
        allergy_diet = f"{allergy} - {diet}"
        temp = view.insert("", "end", values=(
            full_name, wrap(allergy_diet), "", ""))
        """
        For Loop to make drop down format on Dietary page, also prepares information to be inserted into the row
        """
        counter2 = 0
        for items in range(len(Output[counter])):
            food_and_qty = str(Output[counter][counter2]).split(" ")
            foodString = ""
            qty = 0
            for word in range(len(food_and_qty)-1):
                foodString = foodString + " " + food_and_qty[word]
                qty = food_and_qty[-1]
            view.insert(parent=temp, index=tk.END, values=(
                "", wrap(allergy_diet), removeSquareBrackets(foodString), qty))
            counter2 = counter2 + 1
        counter = counter + 1


s = ttk.Style()
s.configure('Treeview', rowheight=62)


def AllIndividualOrders():
    columns = ("FULL NAME", "ALLERGY + DIET", "FOOD", "QTY")
    col_widths = [150, 600, 250, 100]
    col_anchor = ["center", "center", "center", "center"]
    configure_treeview(columns, col_widths, col_anchor)

    values = get_spreadsheet_values(
        spreadsheet_id=SPREADSHEET_ID,
        spreadsheet_range="AllIndividualOrders!A1:Z200")

    first_name_array = values[0][1:]
    last_name_array = values[1][1:]
    allergy_name_array = values[2][1:]
    diet_name_array = values[3][1:]
    food_data_array = values[4:]
    num = len(food_data_array)
    list = len(food_data_array[0])
    Output = []
    for i in range(1, list):
        temp = []
        for j in range(num):
            if str(food_data_array[j][i]) != '0':
                temp.append(
                    f'{food_data_array[j][0]} {food_data_array[j][i]}')
        if temp:
            Output.append(temp)

    counter = 0
    for first_name, last_name, allergy, diet, food in zip(first_name_array, last_name_array, allergy_name_array, diet_name_array, Output):
        full_name = f"{first_name}{last_name[0]}"
        allergy_diet = f"{allergy} - {diet}"
        temp = view.insert("", "end", values=(
            full_name, wrap(allergy_diet), "", ""))
        """
        For Loop to make drop down format on All Individual Orders page, also prepares information to be inserted into the row
        """
        counter2 = 0
        for items in range(len(Output[counter])):
            food_and_qty = str(Output[counter][counter2]).split(" ")
            foodString = ""
            qty = 0
            for word in range(len(food_and_qty)-1):
                foodString = foodString + " " + food_and_qty[word]
                qty = food_and_qty[-1]
            view.insert(parent=temp, index=tk.END, values=(
                "", wrap(allergy_diet), removeSquareBrackets(foodString), qty))
            counter2 = counter2 + 1
        counter = counter + 1


def clear_sheet():
    """
    Clears data in the 'RawFormResponsesTemp' sheet of the Google Sheets document and inserts a new row.
    """
    clear_spreadsheet_range(
        spreadsheet_id=SPREADSHEET_ID,
        range="RawFormResponsesTemp!A2:BS200")


def change_theme():
    """
    Switches between light and dark themes in the Tkinter application.
    """
    if window.tk.call("ttk::style", "theme", "use") == "azure-dark":
        window.tk.call("set_theme", "light")
        asa_logo_label.config(image=asa_logo_img)
        s.configure('Treeview', rowheight=62)
    else:
        window.tk.call("set_theme", "dark")
        asa_logo_label.config(image=asa_logo_img_dark)
        s.configure('Treeview', rowheight=62)


# def generate_PDF():
#     """
#     Generates a PDF document and prints 'Hello, World!' on it. Cut feature.
#     """
#     print("Hello")
#     canvas = Canvas("hello.pdf")
#     canvas.drawString(72, 72, "Hello, World!")
#     canvas.save()


asa_logo_path = "picture.PNG"
asa_logo_img = Image.open(asa_logo_path)
asa_logo_img = asa_logo_img.resize((150, 150))
asa_logo_img = ImageTk.PhotoImage(asa_logo_img)

asa_logo_path_dark = "picture2.PNG"
asa_logo_img_dark = Image.open(asa_logo_path_dark)
asa_logo_img_dark = asa_logo_img_dark.resize((150, 150))
asa_logo_img_dark = ImageTk.PhotoImage(asa_logo_img_dark)

asa_logo_label = tk.Label(window, image=asa_logo_img)
asa_logo_label.grid(row=0, sticky='n', padx=0, pady=0)

window.grid_rowconfigure(0, weight=0)
window.grid_columnconfigure(0, weight=1)

main_frame = ttk.Frame(window)
main_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

frame1 = ttk.Frame(main_frame)
frame1.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
frame1.grid_rowconfigure(0, weight=1)
frame1.grid_columnconfigure(0, weight=1)

scroll = ttk.Scrollbar(frame1)
scroll.pack(side="right", fill="y", pady=(0, 5))
scroll_x = ttk.Scrollbar(frame1, orient="horizontal")
scroll_x.pack(side="bottom", fill="x", pady=(0, 5))

cols = ("ITEMS", "QTY TOTAL",  "")
view = ttk.Treeview(frame1, show="headings",
                    yscrollcommand=scroll.set, xscrollcommand=scroll_x.set, columns=cols, height=8)
view.pack(fill='both', expand=True)
scroll_x.config(command=view.xview)
scroll.config(command=view.yview)

frame2 = ttk.LabelFrame(main_frame, padding=80)
frame2.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)


def open_popup_win():
    """
    Opens a pop up window that is used to clear the data from the sheet at the end of the month.
    """
    out = tk.messagebox.askquestion(
        'Prompt', 'WARNING! Are you sure you wish to clear the responses currently saved in the database?')
    if out == 'yes':
        clear_sheet()
    else:
        print("do nothing")


shoppingList_button = ctk.CTkButton(
    frame2, text="SHOPPING LIST", command=main, fg_color="#b50404", text_color=("black", "white"), hover=False)
shoppingList_button.grid(row=0, column=0, ipadx=50, pady=10, sticky="ew")

AllIndividualOrders_button = ttk.Button(
    frame2, text="ALL INDIVIDUAL LIST", command=AllIndividualOrders)
AllIndividualOrders_button.grid(
    row=1, column=0, ipadx=50, pady=10, sticky="ew")

dietry_button = ttk.Button(frame2, text="DIETARY LIST", command=dietry)
dietry_button.grid(row=2, column=0, ipadx=10, pady=10, sticky="ew")

separator = ttk.Separator(frame2, orient='horizontal')
separator.grid(row=3, column=0, pady=30, sticky="ew")

stock_button = ctk.CTkButton(frame2, text="STOCKS", text_color="#b50404",
                             fg_color="white", border_color="#b50404", border_width=4, hover=False,
                             command=inventory_window)

stock_button.grid(row=4, column=0, ipadx=50, ipady=10, sticky="ew")

# generate_pdf = ttk.Button(frame2, text="DOWNLOAD", command=generate_PDF)
# generate_pdf.grid(row=5, column=0, ipadx=10, pady=10, sticky="ew")
#cut pdf feature

theme_switch = ttk.Checkbutton(
    frame2, text="Mode", command=change_theme)
theme_switch.grid(row=6, column=0, padx=10, pady=15, sticky="nsew")

generate_popup_button = ctk.CTkButton(
    frame2, text="CLEAR SPREADSHEET", command=open_popup_win, fg_color="#b50404", text_color=("black", "white"), hover=False)
generate_popup_button.grid(row=7, column=0, ipadx=50, pady=10, sticky="ew")

window.mainloop()
