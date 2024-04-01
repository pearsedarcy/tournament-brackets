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


participants = SHEET.worksheet('participants')

# TODO - Create a function to view a tournament

# Function to create a new tournament
def create_tournament():
    '''
    Create a new tournament
    '''
    print('Enter the name of the Tournament')
    # TODO - Add type checking for the lenght of input
    tournament_title = input().title()
    # Create the ID of the tournament
    # TODO - Add a function to check if the ID already exists
    tournament_id = tournament_title[0:3].upper() + str(random.randint(100, 999))
    create_worksheet(tournament_id)
    print(f'{tournament_title} has been created!\n Please take note of this for future reference')
    print(f'The ID of the tournament is {tournament_id}')

# Introduction and instructions
def intro(choice):
    '''
    Introduction and instructions
    '''
   
    if choice == '1':
        create_tournament()
    elif choice == '2':
        print('Please enter the ID of the Tournament you would like to view')
        tournament_id = input()
        view_tournament(tournament_id)
    elif choice == '3':
        print('Goodbye!')
    

#create a new worksheet
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
    user_choice = input()
    intro(user_choice)


# Call main function
if __name__ == '__main__':
    main()