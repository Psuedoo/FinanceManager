from employee_dbhandler import *

# TODO: Add loop while paying employees
# TODO: Add logs to DB when paying or logging hours for employees
# TODO: Add Employee object to make for easier handling. Less DB updates possibly?
# TODO: Fix unpaid_amount goes "NULL" when logging hours


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
        0. Quit Program"""

# TODO: Add better passwords, maybe encrypted, probably not.
# TODO: Create permissions based on entered password, maybe a username

# Current Passwords, LOL
passwords = ["password", "pass"]

guessing_pw = True
guess_count = 0
max_guesses = 3


while guessing_pw:
    print("Welcome to the employees program! Please type in your password to gain access....")
    pw_input = input("> ")

    if pw_input in passwords:
        print("You've gained access! Redirecting to the main menu now...")
        has_admin_access = True
        using_program = True
        guessing_pw = False
    else:
        print("Sorry, I don't recognize you.")
        guess_count += 1
        if guess_count >= max_guesses:
            guessing_pw = False
            print("You're out of guesses, good try!")

# Main Loop
while using_program:
    if has_admin_access or has_normal_access:
        print(admin_menu)
        user_selection = int(input("> "))

        # View Employees
        if user_selection == 1:
            view_employees(con)

        # View Unpaid Employees
        elif user_selection == 2:
            view_unpaid_employees(con)

        # Log Employee Hours
        elif user_selection == 3:
            is_logging = True
            while is_logging:
                view_employees(con)
                employee_selection = int(
                    input("Please enter the ID of the employee you're wanting to log hours for (TYPE 8 TO INPUT FOR "
                          "ALL, TYPE 9 TO QUIT)...\n> "))
                if employee_selection:
                    is_same_employee = True
                    while is_same_employee:
                        if employee_selection != 8 and employee_selection != 9:

                            cur.execute("SELECT * FROM employees WHERE id IS %s" % employee_selection)
                            current_employee = cur.fetchall()

                            hours_input = int(input("Please enter the amount of hours to add that employee... (TYPE 0 "
                                                    "WHEN DONE WITH EMPLOYEE)\n> "))

                            if hours_input == 0:
                                fix_pay(con, cur)
                                is_same_employee = False
                            else:
                                log_employee_hours(con, cur, employee_selection, hours_input)

                        elif employee_selection == 8:
                            hours_input = int(
                                input("Please enter the amount of hours to add to all employees... (TYPE 0 WHEN "
                                      "DONE WITH ALL EMPLOYEES)\n> "))
                            if hours_input == 0:
                                fix_pay(con, cur)
                                is_same_employee = False
                            else:
                                log_employee_hours(con, cur, "*", hours_input)
                                fix_pay(con, cur)

                        elif employee_selection == 9:
                            is_same_employee = False
                            is_logging = False
                    else:
                        print("There are not employees with that ID.")

        # Pay Employee
        elif user_selection == 4:
            if check_for_unpaid_employees(con):
                view_unpaid_employees(con)
                employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))
                amount_paid = int(input("How much are you wanting to pay that employee? \n> "))
                pay_employee(con, cur, employee_selection, amount_paid)
            else:
                print("There are no unpaid employees.")

        # View Logs
        elif user_selection == 5:
            view_logs(con)

        # Borrow From Employee
        elif user_selection == 6:
            employee_selection = int(
                input("Please enter the ID of the employee you're wanting to borrow money from...\n> "))
            cur.execute("SELECT * FROM employees WHERE id IS %s" % employee_selection)
            current_employee = cur.fetchall()
            if current_employee:
                borrow_amount = int(input("Please enter the amount to borrow from that employee...\n> "))
                borrow(con, cur, employee_selection, borrow_amount)
            else:
                print("There are no employees with that ID.")

        # Loan Employee
        elif user_selection == 7:
            employee_selection = int(
                input("Please enter the ID of the employee you're wanting to loan money to...\n> "))
            cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
            current_employee = cur.fetchall()
            if current_employee:
                loan_amount = int(input("Please enter the amount to loan that employee...\n> "))
                loan(con, cur, employee_selection, loan_amount)

            else:
                print("There are no employees with that ID.")

        # Pay Employee For Misc
        elif user_selection == 8:
            employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))
            cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
            current_employee = cur.fetchall()
            if current_employee:
                amount_paid = int(input("Please enter the amount to pay off employee's misc...\n> "))
                pay_employee_misc(con, cur, employee_selection, amount_paid)
            else:
                print("There are no employees with that ID.")

        # Employee Paid Debt
        elif user_selection == 9:
            employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))
            cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
            current_employee = cur.fetchall()
            if current_employee:
                amount_paid = int(input("Please enter the amount employee paid off their debt...\n> "))
                employee_paid_debt(con, cur, employee_selection, amount_paid)
            else:
                print("There are no employees with that ID")

        # View Total Owed
        elif user_selection == 10:
            cur.execute("SELECT * FROM employees")
            employees = cur.fetchall()
            total_amount_owed = 0

            for employee in employees:
                unpaid_amount = employee[6]
                unpaid_misc = employee[8]
                total_amount_owed += unpaid_amount + unpaid_misc

            print(f"Total Amount Owed:\t{total_amount_owed}")

        # Export Data
        elif user_selection == 11:
            export(con, cur)

        # Quit Program
        elif user_selection == 0:
            print("Thanks for using the employee program!")
            using_program = False
            con.close()
