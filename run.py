import gspread
from google.oauth2.service_account import Credentials
import random

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPE_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPE_CREDS)
SHEET = GSPREAD_CLIENT.open("tournament_brackets")


def run_tournament(tournament_id):
    tournament_sheet = SHEET.worksheet(tournament_id)
    participants = [participant[0] for participant in tournament_sheet.get("B2:B17")]
    rounds = []
    print("\nGenerating Matches...\n")
    participants_copy = participants.copy()
    while len(participants_copy) > 1:
        rounds.append(participants_copy)
        print(f"Round {len(rounds)}")
        print("---------\n")
        column = chr(67 + len(rounds))  # Columns starting from D (68 in ASCII)
        for i, participant in enumerate(participants_copy, start=2):
            SHEET.worksheet(tournament_id).batch_update(
                [{"range": f"{column}{i}", "values": [[participant]]}]
            )
        participants_copy = run_matchups(participants_copy)
    winner = participants_copy[0]
    SHEET.worksheet(tournament_id).batch_update([{"range": "J2", "values": [[winner]]}])
    print("The winner of the tournament is:", winner)
    print("\n1. Return to Tournament Menu \n")
    print("2. Exit\n")
    choice = input("Your Choice: ").strip().lower()
    while choice not in ["1", "2"]:
        print("\nInvalid input. Please enter '1' or '2'\n")
        choice = input("Your Choice: ").strip()
    if choice == "1":
        view_tournament(tournament_id, SHEET.worksheet(tournament_id).title)
    else:
        main()


def run_matchups(participants):
    return [
        run_match(participants[i], participants[i + 1])
        for i in range(0, len(participants), 2)
    ]


def run_match(participant1, participant2):
    print(f"Match between {participant1} and {participant2}:\n")
    print(f"Enter the name of the winning participant\n")
    winner = input(f"Winner: ").strip().title()
    while winner not in (participant1, participant2):
        print(
            "Invalid input. Please enter the name of the winning participant correctly.\n"
        )
        winner = input(f"Winner: ").strip().title()
    print(f"\nThe winner of the match is: {winner}\n")
    return winner


# Delete tournament function
def delete_tournament(tournament_id):
    """
    Delete a tournament
    """
    SHEET.del_worksheet(SHEET.worksheet(tournament_id))
    print(f"\nTournament {tournament_id} has been deleted\n")
    main()


def input_participants(tournament_id, tournament_title, size):
    """
    Input participants manually
    """
    print("\nType the name of each participant, separated by a comma\n")
    print("For example: John, Jane, Doe, Smith\n")
    while True:
        participants = input("Participants:  ").split(",")
        participants = [participant.strip().title() for participant in participants]
        if len(participants) != int(size):
            print(
                f"\nInvalid number of participants. Please enter {size} participants\n"
            )
            continue
        if len(participants) != len(set(participants)):
            print("\nInvalid input. Participants cannot have the same name\n")
            continue
        if "" in participants:
            print("\nInvalid input. Please enter the name of each participant\n")
            continue
        break
    print(
        f"\nPlease wait, Adding {len(participants)} participants to the tournament...\n"
    )
    for i, participant in enumerate(participants, start=2):
        SHEET.worksheet(tournament_id).batch_update(
            [{"range": f"B{i}", "values": [[participant]]}]
        )
    print("\nParticipants have been added to the tournament\n")
    view_tournament(tournament_id, tournament_title)


def import_participants(tournament_id, tournament_title, size):
    """
    Import participants from the sample_participants sheet and add them to the tournament sheet
    """
    sample_participants_sheet = SHEET.worksheet("sample_participants")
    sample_participants = sample_participants_sheet.get("B1:B" + size)
    sample_participants_list = [participant[0] for participant in sample_participants]
    print(
        f"\nPlease wait, Adding {len(sample_participants_list)} participants to the tournament...\n"
    )
    for i, participant in enumerate(sample_participants_list, start=2):
        SHEET.worksheet(tournament_id).batch_update(
            [{"range": f"B{i}", "values": [[participant]]}]
        )
    print("Participants have been added to the tournament\n")
    view_tournament(tournament_id, tournament_title)


def view_tournament(tournament_id, tournament_title):
    """
    View a tournament
    """
    tournament = SHEET.worksheet(tournament_id)
    print(f"\nWelcome to {tournament_title}\n")
    print("What would you like to do?\n")
    print("1. Run the tournament")
    print("2. Delete Tournament")
    print("3. Exit\n")
    print("Please enter the number of the option you would like to choose\n")
    while True:
        choice = input("Your Choice:  ").strip().lower()
        if choice in ["1", "2", "3", "exit"]:
            if choice.lower() == "exit":
                view_tournament(tournament_id, tournament_title)
            elif choice == "1":
                run_tournament(tournament_id)
            elif choice == "2":
                delete_tournament(tournament_id)
            elif choice == "3":
                main()
            break
        else:
            print(
                '\nInvalid input. Please enter a valid option or type "Exit" to go back.\n'
            )


def choose_participants(tournament_id, tournament_title, size):
    """
    Choose how to enter participants

    """
    print("Would you like to enter your own participants or use sample participants?\n")
    print("1. Enter participants manually")
    print("2. Use sample participants\n")
    print("Please enter the number of the option you would like to choose\n")
    while True:
        choice = input("Your Choice:  ").strip()
        if choice in ["1", "2"]:
            if choice == "1":
                input_participants(tournament_id, tournament_title, size)
                break
            else:
                import_participants(tournament_id, tournament_title, size)
                break
        else:
            print("\nInvalid input. Please enter a valid option (1 or 2)\n")


def create_tournament():
    """
    Create a new tournament
    - Enter the title of the tournament and create a new sheet
    - Generate a unique ID for the tournament
    """
    print("\nWhat would you like to call your tournament?\n")
    while True:
        tournament_title = input("Tournament Title:  ").title().strip()
        if len(tournament_title) > 3 and len(tournament_title) < 50:
            print(
                f'\nAre you sure you want to use "{tournament_title}" as the title?\nYou will not be able to change this in the future (yes/no)\n'
            )
            confirmation = input("Your Choice:  ").lower().strip()
            while confirmation.lower() not in ["yes", "y", "no", "n"]:
                print('\nInvalid input. Please enter "Yes" or "No"\n')
                confirmation = input("Your Choice:  ").lower().strip()
            if confirmation == "yes" or confirmation == "y":
                break
            else:
                print("\nPlease enter a new title\n")
        else:
            print(
                "\nInvalid input. Please enter a title between 4 and 50 characters.\n"
            )
    # Create the ID of the tournament
    tournament_id = tournament_title[0:3].upper() + str(random.randint(100, 999))
    # check if the ID already exists and create a new one if it does
    while True:
        try:
            SHEET.worksheet(tournament_id)
            tournament_id = tournament_title[0:3].upper() + str(
                random.randint(100, 999)
            )
        except gspread.exceptions.WorksheetNotFound:
            break
    print("\nHow many participants will be in the tournament? (4, 8 or 16)\n")
    size = input("Your Choice: ").strip()
    while size not in ["4", "8", "16"]:
        print("\nInvalid input. Please enter a valid number (4, 8 or 16)\n")
        size = input("Your Choice:  ").strip()
    # Create the tournament sheet
    create_tournament_sheet(int(size), tournament_id)
    print(f"\n{tournament_title} has been created!\n")
    print(
        f"The ID of the tournament is {tournament_id}\nPlease take note of this for future reference\n"
    )
    choose_participants(tournament_id, tournament_title, size)


def create_tournament_sheet(
    size,
    tournament_id,
):
    """
    Create a new tournament sheet
    """
    if size == 4:
        SHEET.duplicate_sheet(
            source_sheet_id=1499309545, new_sheet_name=f"{tournament_id}"
        )
    elif size == 8:
        SHEET.duplicate_sheet(
            source_sheet_id=1664735445, new_sheet_name=f"{tournament_id}"
        )
    elif size == 16:
        SHEET.duplicate_sheet(
            source_sheet_id=1310633722, new_sheet_name=f"{tournament_id}"
        )


def main_menu(choice):
    """
    Allows the user to choose what they would like to do
    from the main menu
    """

    if choice == "1":
        create_tournament()
    elif choice == "2":
        print("\nPlease enter the ID of the Tournament you would like to view\n")
        while True:
            tournament_id = input("Your Choice:  ").upper().strip()
            try:
                if tournament_id == "EXIT":
                    main()
                    break
                else:
                    SHEET.worksheet(tournament_id)
                break
            except gspread.exceptions.WorksheetNotFound:
                print(
                    '\nInvalid ID. Please enter a valid ID or type "Exit" to go back\n'
                )
        view_tournament(tournament_id, SHEET.worksheet(tournament_id).title)
    elif choice == "3":
        print("\nThank you for using Tournament Brackets\n")
        print(
            "If you would like to use the app again, please click the refresh button below\n"
        )


def main():
    """
    Main function to run the program
    Acts as a menu for the user to choose what they would like to do
    """

    print("\nWhat would you like to do?\n")
    print("1. Create a new Tournament")
    print("2. View an existing Tournament?")
    print("3. Exit\n")
    print("Please enter the number of the option you would like to choose\n")
    while True:
        user_choice = input("Your Choice:  ").strip()
        if user_choice in ["1", "2", "3"]:
            break
        else:
            print("\nInvalid input. Please enter a valid option (1, 2 or 3)\n")
    main_menu(user_choice)


# Call main function
if __name__ == "__main__":
    main()
