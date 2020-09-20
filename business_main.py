from business_dbhandler import *

# Connect to the DB
con = db_connect()
cur = con.cursor()

using_program = False
has_access = False

main_menu = """
        |||| MAIN MENU ||||
        1. View Cash On Hand
        2. 
        3.
        4.
        5.
        6.
        7.
        8.
        9.
        0. Quit Program"""

main_menu_dict = {
    1: lambda: view_cash_on_hand(con),
    0: lambda: quit_program(con),
}

passwords = ["password", "pass"]

guessing_pw = True
guess_count = 0
max_guesses = 3

while guess_count < max_guesses:
    print("Welcome to the employees program! Please type in your password to gain access....")
    pw_input = input("> ")

    if pw_input in passwords:
        print("You've gained access! Redirecting to the main menu now....")
        has_admin_access = True
        using_program = True
        break
    else:
        print("Sorry, I don't recognize you.")
        guess_count += 1

if guess_count >= max_guesses:
    print("You're out of guesses, good try!")
    quit_program(using_program, con)

# Main Loop
while using_program:
    if has_access:
        print(main_menu)

        try:
            main_menu_dict[int(input("> "))]()
        except ValueError as error:
            print(error)