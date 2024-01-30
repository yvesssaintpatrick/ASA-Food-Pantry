
ASA Food Pantry Management System

This Python application serves as the ASA Food Pantry Management System. 
It utilizes Google Sheets for data storage and retrieval, providing functionalities such as managing shopping lists,
individual dietary preferences, and overall inventory.

Features

1. Shopping List
* View the shopping list with categorized dietary preferences.
* Organize items based on dietary categories such as NONE, VEGETARIAN, VEGAN, PESCATARIAN, HALAL, GLUTEN-FREE, and OTHER.
* Clear the shopping list after purchase.


2. Individual Orders
* Access individual orders with detailed information.
* Display full names, allergies, dietary preferences, ordered food items, and quantities.
* Differentiate between important individual orders and all individual orders.
* Download individual order information.

3. Dietary List
* View a comprehensive dietary list.
* Organize information by full name, allergies, dietary preferences, and specific food items ordered with quantities.
* Easily navigate and explore dietary preferences.

4. Inventory Management
* Check the current stocks of food items in the pantry.
* Access a user-friendly interface to manage inventory efficiently.

5. Theme Switching
* Switch between light and dark modes for a personalized viewing experience.

6. Clear Spreadsheet
* Clear responses from the RawFormResponsesTemp sheet at the end of the month.

Prerequisites
* Google Sheets API credentials with appropriate access.
* Python environment with necessary libraries installed.
* Tkinter, customtkinter, and PIL for the GUI.
* Google API client library for Sheets API integration.
* ReportLab for PDF generation.
