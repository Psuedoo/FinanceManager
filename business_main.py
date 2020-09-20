from business_dbhandler import *
from employee_dbhandler import *

"""
TODO:
    - Create link between payroll and cash
    - Maybe add "auto budget" for payroll? 30% of cash on hand?   
"""

"""
Attributes of business money:
    - cash_on_hand: How much available spending money
    - payroll: How much available to spend on payroll
    - material: How much available to spend on material
    - unpaid_collections: How much predicted income from jobs
    - debt: How much owed for misc
    - utilities: How much owed for bills
"""


# Connect to the DB
con = db_connect()
cur = con.cursor()

using_program = False
has_access = False

main_menu = """
        |||| MAIN MENU ||||
        1. View Cash On Hand
        2. Deposit
        3. Withdraw
        4. View Payroll
        5. View Material Amount
        6. View Unpaid Collections
        7. View Debt
        8. View Utilities
        9.
        0. Quit Program"""

main_menu_dict = {
    1: lambda: view_cash_on_hand(con),
    2: lambda: deposit(con),
    3: lambda: withdraw(con),
    4: lambda: view_payroll(con),
    5: lambda: view_material_amount(con),
    6: lambda: view_unpaid_collections(con),
    7: lambda: view_debt(con),
    8: lambda: view_utilities(con),
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
        has_access = True
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