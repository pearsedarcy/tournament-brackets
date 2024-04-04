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


# Delete tournament function
def delete_tournament(tournament_id):
    '''
    Delete a tournament
    '''
    SHEET.del_worksheet(SHEET.worksheet(tournament_id))
    print(f'\nTournament {tournament_id} has been deleted\n')
    main()


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
    for i, participant in enumerate(participants, start=2):
        SHEET.worksheet(tournament_id).batch_update([{ 'range': f'A{i}', 'values': [[participant]] }])
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
    for i, participant in enumerate(sample_participants_list, start=2):
        SHEET.worksheet(tournament_id).batch_update([{ 'range': f'A{i}', 'values': [[participant]] }])
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


def view_tournament(tournament_id, tournament_title):
    '''
    View a tournament
    '''
    tournament = SHEET.worksheet(tournament_id)
    print(f'Welcome to {tournament_title}\n')
    # if the tournament has no participants
    if tournament.get('A2') == [[]]:
        print('There are no participants in this tournament\n')
        choose_participants(tournament_id)
    else:
        print('What would you like to do?\n')
        print('1. Run the tournament')
        print('2. Edit Participants')
        print('3. Delete Tournament')
        print('4. Exit\n')
        print('Please enter the number of the option you would like to choose\n')
        while True:
            choice = input('Your input:  ')
            if choice.strip() in ['1', '2', '3', '4', 'exit']:
                if choice.lower().strip()  == 'exit':
                    view_tournament(tournament_id)
                elif choice.strip() == '1':
                    run_tournament(tournament_id)
                elif choice.strip() == '2':
                    edit_participants(tournament_id)
                elif choice.strip() == '3':
                    delete_tournament(tournament_id)
                elif choice.strip() == '4':
                    main()
                break
            else:
                print('\nInvalid input. Please enter a valid option or type "Exit" to go back.\n')
                


def create_tournament():
    '''
    Create a new tournament
    - Enter the title of the tournament and create a new sheet
    - Generate a unique ID for the tournament
    '''
    print('\nWhat would you like to call your tournament?\n')
    while True:
        tournament_title = input('Tournament Title:  ').title().strip()
        if len(tournament_title) > 3 and len(tournament_title) < 50:
            print(f'\nAre you sure you want to use "{tournament_title}" as the title?\nYou will not be able to change this in the future (yes/no)\n')
            confirmation = input('Your Choice:  ')
            while confirmation.lower().strip() not in ['yes', 'y', 'no', 'n']:
                print('\nInvalid input. Please enter "Yes" or "No"\n')
                confirmation = input('Your Choice:  ')
            if confirmation.lower().strip() == 'yes' or confirmation.lower().strip() == 'y':
                break
            else:
                print('\nPlease enter a new title\n')
        else:
            print('\nInvalid input. Please enter a title between 4 and 50 characters.\n')
    # Create the ID of the tournament
    tournament_id = tournament_title[0:3].upper() + str(random.randint(100, 999))
    # check if the ID already exists and create a new one if it does
    while True:
        try:
            SHEET.worksheet(tournament_id)
            tournament_id = tournament_title[0:3].upper() + str(random.randint(100, 999))
        except gspread.exceptions.WorksheetNotFound:
            break
    # Create the tournament sheet
    SHEET.duplicate_sheet(source_sheet_id=1391351056, new_sheet_name=f'{tournament_id}')
    print(f'\n{tournament_title} has been created!\n')
    print(f'The ID of the tournament is {tournament_id}\nPlease take note of this for future reference\n')
    view_tournament(tournament_id, tournament_title)


def main_menu(choice):
    '''
    Allows the user to choose what they would like to do
    from the main menu
    '''

    if choice == '1':
        create_tournament()
    elif choice == '2':
        print('\nPlease enter the ID of the Tournament you would like to view\n')
        while True:
            tournament_id = input('Your Choice:  ').upper().strip()
            try:
                if tournament_id == 'EXIT':
                    main()
                    break
                else:
                    SHEET.worksheet(tournament_id)
                break
            except gspread.exceptions.WorksheetNotFound:
                print('\nInvalid ID. Please enter a valid ID or type "Exit" to go back\n')
        view_tournament(tournament_id)
    elif choice == '3':
        print('\nThank you for using Tournament Brackets\n')
        print('If you would like to use the app again, please click the refresh button below\n')


def main():
    '''
    Main function to run the program
    Acts as a menu for the user to choose what they would like to do
    '''

    print('\nWhat would you like to do?\n')
    print('1. Create a new Tournament')
    print('2. View an existing Tournament?')
    print('3. Exit\n')
    print('Please enter the number of the option you would like to choose\n')
    while True:
        user_choice = input('Your Choice:  ')
        if user_choice.strip() in ['1', '2', '3']:
            break
        else:
            print('\nInvalid input. Please enter a valid option (1, 2 or 3)\n')
    main_menu(user_choice)


# Call main function
if __name__ == '__main__':
    main()
