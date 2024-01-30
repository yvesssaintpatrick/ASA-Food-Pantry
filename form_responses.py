from constants import *
from spreadsheets import get_spreadsheet_values

import json
def is_food_question(question):
    '''
    Checks if the question is purely related to food.
    I.E: How many jars of jam do you want?

    ** Edit logic here as needed to filter out food-only questions
    '''
    return '[' in question and ']' in question


def food_question_str(raw_question_str):
    '''
    Once a question has been confirmed to be purely food related,
    this function will clean the question body to a more readable form,
    containing only the food related portion(s).
    '''
    open_bracket_i = raw_question_str.find('[')
    close_bracket_i = raw_question_str.find(']')

    return raw_question_str[open_bracket_i + 1 : close_bracket_i]


def is_included_personal_question(question):
    '''
    Checks if the question contains personal info that should be excluded
    from any generated forms, lists, etc. I.E: Home address, phone number.

    ** Edit logic here as needed to filter out included non-food questions.
    '''
    for keyword in FORM_KW_WHITELIST:
        if keyword in question.lower():
            return True
    return False


def get_responses_dict():
    '''
    Fetches the raw responses from the raw form spreadsheet and converts the
    responses into JSON lists of the schema:

    [
        {
            "personal": [
                {
                    "question": <personal_question>,
                    "response": <personal_response>
                },
                ...
            ],
            "food":  [
                {
                    "question": <cleaned_food_question>,
                    "raw_question": <raw_food_question>,
                    "response": <food_response>
                },
                ...
            ]
        },
        ...
    ]
    '''
    all_responses = []
    raw_form_values = get_spreadsheet_values(
        spreadsheet_id=SPREADSHEET_ID,
        spreadsheet_range=RAW_SHEET_RANGE)
    
    # Assumes that raw  spreadsheet will always begin with the form questions
    # (Default output of Google Forms)
    form_questions, form_responses = raw_form_values[0], raw_form_values[1:]

    for student_response in form_responses:
        if not student_response:
            # It is possible for a response row in the spreadsheet
            # to be empty. In this case, simply move to the next
            continue

        response = { 'personal': [], 'food': [] }

        # TODO: Fair to assume the number of form responses and 
        #       questions should always match?
        assert len(student_response) == len(form_questions), 'Form/Response conflict: check spreadsheet.'

        for question_i in range(len(form_questions)):
            current_question = form_questions[question_i]
            current_answer = student_response[question_i]
            
            # ** Add/edit information in objects here as needed **
            if is_food_question(current_question):
                response['food'].append({
                    'question': food_question_str(current_question),
                    'raw_question': current_question,
                    'response': current_answer
                })

            elif is_included_personal_question(current_question):
                response['personal'].append({
                    'question': current_question,
                    'response': current_answer,
                    # TODO: Clean personal response to hide them
                })
        all_responses.append(response)
    return all_responses


    

