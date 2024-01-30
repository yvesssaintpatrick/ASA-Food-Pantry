from os import path
import logging

from constants import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_oauth_credentials():
    """
    Retrieves OAuth credentials for accessing Google APIs.

    This function checks if a file named "token.json" exists in the current
    directory. If it does, it attempts to load credentials from that file.
    If the credentials are not valid or do not exist, it initiates the OAuth
    authentication flow using the "credentials.json" file.

    The function ensures that valid credentials are obtained before returning.
    If credentials need to be refreshed, it performs the refresh.

    Note:
    - Make sure to have the "credentials.json" file containing your client
      secrets in the same directory as this script.
    - The "token.json" file is used to store and retrieve the obtained
      credentials.

    Returns:
    - credentials (google.oauth2.credentials.Credentials): The obtained or
      refreshed OAuth credentials.

    Raises:
    - AssertionError: If the credentials are not obtained successfully.
    """
    credentials = None
    if path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file(
            "token.json", SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
    
    assert credentials is not None
    return credentials


def get_spreadsheet_service():
    """
    Retrieves the Google Sheets API service for accessing spreadsheets.

    Returns:
    - googleapiclient.discovery.Resource: The Google Sheets API service for
      accessing spreadsheets.

    Raises:
    - HttpError: If an error occurs while getting the spreadsheet service.
      The error details are logged using the Python logging module.
    """
    try:
        credentials = get_oauth_credentials()
        return build("sheets", "v4", credentials=credentials).spreadsheets()
    except HttpError as e:
        logging.error(f"Error getting spreadsheet service: {e}")


def get_spreadsheet_values(spreadsheet_id, spreadsheet_range, spreadsheet_service=None):
    """
    Retrieves values from a specified range in a Google Spreadsheet.

    Args:
    - spreadsheet_id (str): The ID of the target Google Spreadsheet.
    - spreadsheet_range (str): The range in A1 notation from which to retrieve values.
    - spreadsheet_service (googleapiclient.discovery.Resource, optional): The Google Sheets API service.
      If not provided, the function will attempt to obtain it using `get_spreadsheet_service()`.

    Returns:
    - list: A list of lists representing the values retrieved from the spreadsheet.

    Note:
    - If the specified range is empty, an empty list is returned.
    """
    if not spreadsheet_service:
        spreadsheet_service = get_spreadsheet_service()
    query_result = spreadsheet_service.values().get(
        spreadsheetId=spreadsheet_id,
        range=spreadsheet_range).execute()

    return query_result.get("values", [])

def clear_spreadsheet_range(spreadsheet_id, range, spreadsheet_service=None):
    """
    Clears the values from a specified range in a Google Spreadsheet.

    Args:
    - spreadsheet_id (str): The ID of the target Google Spreadsheet.
    - spreadsheet_range (str): The range in A1 notation to be cleared.
    - spreadsheet_service (googleapiclient.discovery.Resource, optional): The Google Sheets API service.
      If not provided, the function will attempt to obtain it using `get_spreadsheet_service()`.

    Returns:
    - dict: The result of the clear operation.
    """
    if not spreadsheet_service:
        spreadsheet_service = get_spreadsheet_service()
    values_api = spreadsheet_service.values()
    return values_api.clear(
                    spreadsheetId=spreadsheet_id,
                    body={"range": range},
                    range=range).execute()

def update_spreadsheet_values(spreadsheet_id, spreadsheet_range, values, spreadsheet_service=None):
    """
    Updates values in a specified range in a Google Spreadsheet.

    Args:
    - spreadsheet_id (str): The ID of the target Google Spreadsheet.
    - spreadsheet_range (str): The range in A1 notation to be updated.
    - values (list): The new values to be written to the spreadsheet.
    - spreadsheet_service (googleapiclient.discovery.Resource, optional): The Google Sheets API service.
      If not provided, the function will attempt to obtain it using `get_spreadsheet_service()`.

    Returns:
    - dict: The result of the update operation.
    """
    if not spreadsheet_service:
        spreadsheet_service = get_spreadsheet_service()
    values_api = spreadsheet_service.values()
    return values_api.update(
                spreadsheetId=spreadsheet_id,
                range=spreadsheet_range,
                body={"values": values, "range": spreadsheet_range},
                valueInputOption="RAW").execute()

def append_rows_to_spreadsheet(spreadsheet_id, spreadsheet_range, rows, spreadsheet_service=None):
    """
    Appends rows to a specified range in a Google Spreadsheet.

    Args:
    - spreadsheet_id (str): The ID of the target Google Spreadsheet.
    - spreadsheet_range (str): The range in A1 notation to which rows should be appended.
    - rows (list): The rows of values to be appended to the spreadsheet.
    - spreadsheet_service (googleapiclient.discovery.Resource, optional): The Google Sheets API service.
      If not provided, the function will attempt to obtain it using `get_spreadsheet_service()`.

    Returns:
    - dict: The result of the append operation.
    """
    if not spreadsheet_service:
        spreadsheet_service = get_spreadsheet_service()
    values_api = spreadsheet_service.values()
    return values_api.append(
                spreadsheetId=spreadsheet_id,
                range=spreadsheet_range,
                body={"values": rows, "range": spreadsheet_range},
                valueInputOption="RAW").execute()
    
    

