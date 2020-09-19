from employee_dbhandler import *

# Connect to the DB
con = db_connect()
cur = con.cursor()

# Creates Directories
create_directories()

# Setting my variables.
has_normal_access = False
has_admin_access = False
using_program = False
is_logging = False
is_same_employee = False

# Menus
admin_menu = """
        |||| MAIN MENU ||||
        1. View Employees
        2. View Unpaid Employees
        3. Log Employees Hours
        4. Pay Employee
        5. View Logs
        6. Borrow From Employee
        7. Loan Employee
        8. Pay Employee For Misc
        9. Employee Paid Debt
        10. View Total Owed
        11. Export Data
        12. Create Employee
        0. Quit Program"""

main_menu_dict = {
    1: lambda: view_employees(con),
    2: lambda: view_unpaid_employees(con),
    3: lambda: log_employee_hours(con, cur),
    4: lambda: pay_employee(con, cur),
    5: lambda: view_logs(con),
    6: lambda: borrow(con, cur),
    7: lambda: loan(con, cur),
    8: lambda: pay_employee_misc(con, cur),
    9: lambda: employee_paid_debt(con, cur),
    10: lambda: view_amount_owed(con, cur),
    11: lambda: export(con, cur),
    12: lambda: create_employee(con, cur),
    0: lambda: quit_program(using_program, con)
}

# TODO: Add better passwords, maybe encrypted, probably not.
# TODO: Create permissions based on entered password, maybe a username

# Current Passwords, LOL
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
    if has_admin_access or has_normal_access:
        print(admin_menu)

        main_menu_dict[int(input("> "))]()
