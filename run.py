import gspread
from google.oauth2.service_account import Credentials
import random

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPE_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPE_CREDS)
SHEET = GSPREAD_CLIENT.open('tournament_brackets')


def input_participants(tournament_id):
    '''
    Input participants manually
    '''
    print('Enter the participants of the tournament\n')
    print('Please enter the name of each participant and press enter after each name\n')
    print('When you are done, type "Done"')
    participants = []
    while True:
        participant = input()
        if participant.upper().strip() == 'DONE':
            break
        elif len(participant) > 3 and len(participant) < 20:
            participants.append(participant)
        else:
            print('Invalid input. Please enter a name between 4 and 20 characters')
    # TODO - Add additional participants if the number of participants is not a power of 2
    print(f'Please wait, Adding {len(participants)} participants to the tournament...')
    for participant in participants:
        SHEET.worksheet(tournament_id).append_row([participant])
    print('Participants have been added to the tournament')
    view_tournament(tournament_id)


def import_participants(number, tournament_id):
    '''
    Import participants from the sample_participants sheet and add them to the tournament sheet
    '''
    sample_participants_sheet = SHEET.worksheet('sample_participants')
    sample_participants = sample_participants_sheet.get('A1:A' + number)
    sample_participants_list = [participant[0] for participant in sample_participants]
    # TODO - Add additional participants if the number of participants is not a power of 2
    print(f'Please wait, Adding {len(sample_participants_list)} participants to the tournament...')
    for participant in sample_participants_list:
        SHEET.worksheet(tournament_id).append_row([participant])
    print('Participants have been added to the tournament')
    view_tournament(tournament_id)


def choose_participants(tournament_id):
    '''
    Choose whether to enter participants manually or or use sample participants
    '''
    print('Would you like to enter your own participants or use sample participants?')
    print('1. Enter participants')
    print('2. Use sample participants')
    while True:
        choice = input('Please enter 1 or 2\n')
        if choice in ['1', '2']:
            if choice == '1':
                input_participants(tournament_id)
                break
            else:
                # TODO - Add input validation to ensure number of partipants is greater than 2 and less than 33 and that it is an integer
                number_of_participants = input('How many participants would you like?\n')
                import_participants(number_of_participants, tournament_id)
            break
        else:
            print('Invalid input. Please enter 1 or 2')
    return choice


def view_tournament(tournament_id):
    '''
    View a tournament
    '''
    tournament = SHEET.worksheet(tournament_id)
    print(f'Welcome to {tournament.title}')
    # if the tournament has no participants
    # TODO - Fix to precisely check if there are no participants
    if len(tournament.get_all_values()) == 1:
        print('There are no participants in this tournament')
        choose_participants(tournament_id)
    else:
        # TODO - Add options for exisiting tournaments
        print('What would you like to do?')


def create_tournament():
    '''
    Create a new tournament
    '''
    while True:
        # TODO - add confirmation for the title i.e. are you sure you want to use this title?
        tournament_title = input('Enter the name of the Tournament\n').title().strip()
        if len(tournament_title) > 3 and len(tournament_title) < 50:
            break
        else:
            print('Invalid input. Please enter a title between 4 and 50 characters.')
    # Create the ID of the tournament
    tournament_id = tournament_title[0:3].upper() + str(random.randint(100, 999))
    # check if the ID already exists and create a new one if it does
    while True:
        try:
            SHEET.worksheet(tournament_id)
            tournament_id = tournament_title[0:3].upper() + str(random.randint(100, 999))
        except gspread.exceptions.WorksheetNotFound:
            break
    create_worksheet(tournament_id)
    # TODO - Add tournament sheet formatting
    print(f'{tournament_title} has been created!')
    print(f'The ID of the tournament is {tournament_id}\nPlease take note of this for future reference')
    view_tournament(tournament_id)


def intro(choice):
    '''
    Introduction and instructions
    '''

    if choice == '1':
        create_tournament()
    elif choice == '2':
        while True:
            tournament_id = input('Please enter the ID of the Tournament you would like to view\n').upper().strip()
            try:
                if tournament_id == 'EXIT':
                    main()
                    break
                else:
                    SHEET.worksheet(tournament_id)
                break
            except gspread.exceptions.WorksheetNotFound:
                print('Invalid ID. Please enter a valid ID or type "Exit" to go back')
        view_tournament(tournament_id)
    elif choice == '3':
        print('Goodbye!')


def create_worksheet(title):
    '''
    Creates a new worksheet with the given title
    '''
    SHEET.add_worksheet(title, 80, 25)

# Main function


def main():
    '''
    Main function

    '''
    print('Welcome to Tournament Brackets\n')
    print('Create and manage your own Tournament Brackets\n')
    print('What would you like to do?\n')
    print('1. Create a new Tournament')
    print('2. View an existing Tournament?')
    print('3. Exit')
    while True:
        user_choice = input('Please pick from the options above i.e. 1, 2 or 3\n')
        if user_choice in ['1', '2', '3']:
            break
        else:
            print('Invalid input. Please enter a valid option.')
    intro(user_choice)


# Call main function
if __name__ == '__main__':
    main()
