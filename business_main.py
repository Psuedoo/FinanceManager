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

passwords = ["password", "pass"]

guessing_pw = True
guess_count = 0
max_guesses = 3

while guessing_pw:
    print("Welcome to the business program! Please type in your password to gain access....")
    pw_input = input("> ")

    if pw_input in passwords:
        print("You've gained access! Redirecting to the main menu...")
        using_program = True
        has_access = True
        guessing_pw = False
    else:
        print("Sorry, I don't recognize you.")
        guess_count += 1
        if guess_count >= max_guesses:
            guessing_pw = False
            print("You're out of guess, good try!")

while using_program:
    if has_access:
        print(main_menu)
        user_selection = int(input("> "))

        # View Cash On Hand
        if user_selection == 1:
            view_cash_on_hand(con)
