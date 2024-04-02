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


def import_participants(number):
    '''
    Import participants from the sample_participants sheet
    '''
    participants_sheet = SHEET.worksheet('sample_participants')
    participants = participants_sheet.get('A1:A' + number)
    sample_participants_list = [participant[0] for participant in participants]
    print(f'{len(participants_list)} participants have been added to the tournament')
    return sample_participants_list
    

def choose_participants():
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
                input_participants()
                break
            else:
                number_of_participants = input('How many participants would you like?')
                import_participants(number_of_participants)
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
    if len(tournament.get_all_values()) == 1:
        print('There are no participants in this tournament')
        choice = choose_participants()
    else:
        # TODO - Add options for exisiting tournaments
        print('What would you like to do?')
    
    

def create_tournament():
    '''
    Create a new tournament
    '''
    while True:
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
                if tournament_id== 'EXIT':
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