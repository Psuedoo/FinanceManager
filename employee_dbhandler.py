import json
import os
import sqlite3
import zipfile
from datetime import datetime
from pytz import timezone

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

tz = timezone('EST')


# Connects to the DB
def db_connect(db_path=DEFAULT_PATH):
    conn = sqlite3.connect(db_path)
    return conn


# Initialize DB
def db_init(con):
    cur = con.cursor()

    try:

        create_employee_table = """
            CREATE TABLE "employees" (
            "id"	INTEGER DEFAULT 0 UNIQUE,
            "first_name"	text,
            "last_name"	text,
            "phone_number"	integer,
            "hourly_pay"	integer DEFAULT 0,
            "unpaid_hours"	integer DEFAULT 0,
            "unpaid_amount"	integer DEFAULT 0,
            "debt"	INTEGER NOT NULL DEFAULT 0,
            "unpaid_amount_misc"	INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY("id" AUTOINCREMENT)
        )"""

        cur.execute(create_employee_table)

    except:
        print("Couldn't create table, may already exist.")


# Create directories
def create_directories():
    paths = ["C:\FinanceManager", "C:\FinanceManager\Exports"]

    for path in paths:
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed." % path)
        else:
            print("Successfully created the directory %s" % path)


# Checks if an employee exists
def check_employee(con, id):
    cur = con.cursor()
    cur.execute("SELECT * FROM employees WHERE id IS ?", (id,))
    results = cur.fetchone()

    if results:
        return True
    else:
        return False


# Displays all employees
def view_employees(con):
    cur = con.cursor()

    cur.execute("SELECT * FROM employees")

    rows = cur.fetchall()

    if rows:
        print("Here are the employees: ")
        for row in rows:
            print(f"--------------------------------\n"
                  f"ID:\t\t{row[0]}\n"
                  f"Name:\t\t{row[1]} {row[2]}\n"
                  f"Phone Number:\t{row[3]}\n"
                  f"Hourly Rate:\t{row[4]}\n"
                  f"Unpaid Hours:\t{row[5]}\n"
                  f"Unpaid Amount:\t{row[6]}\n"
                  f"Unpaid Misc:\t{row[8]}\n"
                  f"Debt:\t\t{row[7]}\n"
                  f"--------------------------------")

        return True
    else:
        print("There are no employees.")
        return False


# Views single employee
def view_employee(con, id):
    cur = con.cursor()

    if check_employee(con, id):
        cur.execute("SELECT * FROM employees WHERE id IS ?", (id,))
        employee = cur.fetchall()

        for row in employee:
            employee_id = row[0]
            name = f"{row[1]} {row[2]}"
            phone_number = row[3]
            hourly_rate = row[4]
            unpaid_hours = row[5]
            unpaid_amount = row[6]
            unpaid_misc = row[8]
            debt = row[7]

            print(f"--------------------------------\n"
                  f"ID:\t\t{employee_id}\n"
                  f"Name:\t\t{name}\n"
                  f"Phone Number:\t{phone_number}\n"
                  f"Hourly Rate:\t{hourly_rate}\n"
                  f"Unpaid Hours:\t{unpaid_hours}\n"
                  f"Unpaid Amount:\t{unpaid_amount}\n"
                  f"Unpaid Misc:\t{unpaid_misc}\n"
                  f"Debt:\t\t{debt}\n"
                  f"--------------------------------")

        return {"id": employee_id, "name": name, "phone number": phone_number, "hourly rate": hourly_rate,
                "unpaid hours": unpaid_hours, "unpaid amount": unpaid_amount, "unpaid misc": unpaid_misc, "debt": debt}

    else:
        print("Employee doesn't exist.")


# Checks for unpaid employees
def check_for_unpaid_employees(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE unpaid_amount IS NOT 0")

    rows = cur.fetchall()
    if not rows:
        return False
    else:
        return True


# Displays unpaid employees
def view_unpaid_employees(conn):
    if check_for_unpaid_employees(conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM employees WHERE unpaid_amount IS NOT 0")

        rows = cur.fetchall()
        print("Here are the employees: ")
        for row in rows:
            print(f"--------------------------------\n"
                  f"ID:\t\t{row[0]}\n"
                  f"Name:\t\t{row[1]} {row[2]}\n"
                  f"Phone Number:\t{row[3]}\n"
                  f"Hourly Rate:\t{row[4]}\n"
                  f"Unpaid Hours:\t{row[5]}\n"
                  f"Unpaid Amount:\t{row[6]}\n"
                  f"Unpaid Misc:\t{row[8]}\n"
                  f"Debt:\t\t{row[7]}\n"
                  f"--------------------------------")

    else:
        print("There are no unpaid employees.")


# Runs sql query and commits
def update_table(conn, cur, query, values: tuple = None):
    if values:
        try:
            cur.execute(query, values)
            conn.commit()
            print("Record Updated Successfully")

        except sqlite3.Error as error:
            print("Failed to update table", error)
    else:
        try:
            cur.execute(query)
            conn.commit()
            print("Record Updated Successfully")

        except sqlite3.Error as error:
            print("Failed to update table", error)


# Calculates unpaid amount based on unpaid hours and hourly pay
def fix_pay(con, cur):
    cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()

    for employee in employees:
        id = employee[0]
        hourly_pay = employee[4]
        unpaid_amount = employee[6]

        carry_over_hours = unpaid_amount % hourly_pay

        if carry_over_hours > 0:
            update_table(con, cur, "UPDATE employees SET unpaid_amount = (unpaid_hours * hourly_pay) + ? WHERE id IS "
                                   "?", (carry_over_hours, id))
        else:
            update_table(con, cur,
                         "UPDATE employees SET unpaid_amount = (unpaid_hours * hourly_pay) WHERE id IS ?", (id,))


# Calculates unpaid hours based on unpaid amount and hourly pay
def fix_hours(con, cur):
    update_table(con, cur, "UPDATE employees SET unpaid_hours = unpaid_amount / hourly_pay")


# Adds unpaid hours to employee
def log_employee_hours(con, cur):
    view_employees(con)

    employee_selection = int(
        input("Please enter the ID of the employee you're wanting to log hours for (TYPE 8 TO INPUT FOR "
              "ALL; TYPE 9 TO QUIT)...\n> "))

    if employee_selection != 8 and employee_selection != 9:
        if check_employee(con, employee_selection):
            cur.execute("SELECT * FROM employees WHERE id IS ?", (employee_selection,))
            current_employee = cur.fetchone()

            hours_input = int(input("Please enter the amount of hours to add that employee...\n> "))

            fix_pay(con, cur)

            cur.execute("SELECT * FROM employees WHERE id IS ?", (employee_selection,))
            selected_employee = cur.fetchall()

            for row in selected_employee:
                id = row[0]
                employee_name = f"{row[1]} {row[2]}"

            add_log(con, cur, format_log(datetime.now(tz), employee_name, "WORKED", hours_input))

            update_table(con, cur,
                         "UPDATE employees SET unpaid_hours = unpaid_hours + ? WHERE id IS ?", (
                             hours_input, id))

    elif employee_selection == 8:
        hours_input = int(
            input("Please enter the amount of hours to add to all employees...\n> "))

        cur.execute("SELECT * FROM employees")
        selected_employees = cur.fetchall()

        for employee in selected_employees:
            employee_name = f"{employee[1]} {employee[2]}"

            add_log(con, cur, format_log(datetime.now(tz), employee_name, "WORKED", hours_input))

            update_table(con, cur,
                         "UPDATE employees SET unpaid_hours = unpaid_hours + ? WHERE id IS ?", (
                             hours_input, employee[0]))
    else:
        print("There are not employees with that ID.")

    fix_pay(con, cur)


# Edits balance of employee
def pay_employee(con, cur):
    if check_for_unpaid_employees(con):
        view_unpaid_employees(con)
        employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))

        if check_employee(con, employee_selection):
            amount_paid = int(input("How much are you wanting to pay that employee?\n> "))

            if amount_paid > 0:

                cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
                selected_employee = cur.fetchall()

                for row in selected_employee:
                    id = row[0]
                    employee_name = f"{row[1]} {row[2]}"

                add_log(con, cur, format_log(datetime.now(tz), employee_name, "PAID", amount_paid))

                update_table(con, cur,
                             "UPDATE employees SET unpaid_amount = unpaid_amount - ? WHERE id IS ?", (amount_paid, id))
            else:
                print("Have to pay more than 0.")

        else:
            print("Employee doesn't exist.")

    else:
        print("There are no unpaid employees.")

    fix_hours(con, cur)


# Displays logs (CURRENTLY DISPLAYS ALL LOGS)
def view_logs(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs LIMIT 15")
    rows = cur.fetchall()

    print("Here are the logs:")
    for row in rows:
        print(f"--------------------------------\n"
              f"[{row[0]}]\n"
              f"[{row[2]}]\t[{row[1]}]\n"
              f"[{row[3]}]\n"
              f"[{row[4]}]\n"
              f"--------------------------------\n")


# Formats the log
def format_log(date, name, action, amount):
    log = [date.strftime("%x %X"), name, action, amount]
    print(log)
    return log


# Creates a log for DB
def add_log(conn, cur, log):
    date = log[0]
    name = log[1]
    action = log[2]
    amount = log[3]

    cur.execute("INSERT INTO logs (date, name, action, amount) VALUES (?, ?, ?, ?);", (date, name, action, amount))
    conn.commit()


# Borrows money from an employee
def borrow(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to borrow money from...\n> "))

    if check_employee(con, employee_selection):

        cur.execute("SELECT * FROM employees WHERE id IS ?", (employee_selection,))
        selected_employee = cur.fetchall()

        if selected_employee:
            borrow_amount = int(input("Please enter the amount to borrow from that employee...\n> "))
            for row in selected_employee:
                id = row[0]
                employee_name = f"{row[1]} {row[2]}"

            add_log(con, cur, format_log(datetime.now(tz), employee_name, "BORROWED", borrow_amount))

            update_table(con, cur, "UPDATE employees SET unpaid_amount_misc = unpaid_amount_misc + ? WHERE id IS ?", (
                borrow_amount, id))
    else:
        print("There are no employees with that ID.")


# Loans money to an employee
def loan(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to loan money to...\n> "))

    if check_employee(con, employee_selection):

        cur.execute("SELECT * FROM employees WHERE id IS ?", (employee_selection,))
        selected_employee = cur.fetchall()
        if selected_employee:
            loan_amount = int(input("Please enter the amount to loan that employee...\n> "))

            for row in selected_employee:
                id = row[0]
                employee_name = f"{row[1]} {row[2]}"

            add_log(con, cur, format_log(datetime.now(tz), employee_name, "LOANED", loan_amount))

            update_table(con, cur, "UPDATE employees SET debt = debt + ? WHERE id IS ?", (loan_amount, id))
    else:
        print("There are no employees with that ID.")


# Pays off employee misc
def pay_employee_misc(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))

    if check_employee(con, employee_selection):

        cur.execute("SELECT * FROM employees WHERE id IS ?", (employee_selection,))
        selected_employee = cur.fetchall()

        if selected_employee:
            for row in selected_employee:
                id = row[0]
                employee_name = f"{row[1]} {row[2]}"

            amount_paid = int(input("Please enter the amount to pay off employee's misc...\n> "))

            add_log(con, cur, format_log(datetime.now(tz), employee_name, "PAID", amount_paid))

            update_table(con, cur,
                         "UPDATE employees SET unpaid_amount_misc = unpaid_amount_misc - ? WHERE id IS ?", (
                             amount_paid, id))
    else:
        print("There are no employees with that ID.")


# Takes away from employee debt
def employee_paid_debt(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))

    if check_employee(con, employee_selection):

        cur.execute("SELECT * FROM employees WHERE id IS ?", (employee_selection,))
        selected_employee = cur.fetchall()

        if selected_employee:
            for row in selected_employee:
                id = row[0]
                employee_name = f"{row[1]} {row[2]}"
            amount_paid = int(input("Please enter the amount employee paid off their debt...\n> "))

            add_log(con, cur, format_log(datetime.now(tz), employee_name, "RECEIVED", id))

            update_table(con, cur,
                         "UPDATE employees SET debt = debt - ? WHERE id IS ?", (amount_paid, id))
    else:
        print("There are no employees with that ID.")


# Views total amount owed
def view_amount_owed(cur):
    cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    total_amount_owed = 0

    for employee in employees:
        unpaid_amount = employee[6]
        unpaid_misc = employee[8]
        total_amount_owed += unpaid_amount + unpaid_misc

    print(f"Total Amount Owed:\t{total_amount_owed}")


# Exports employee data
def export_employee_info(cur):
    def employees_to_json(cur):
        cur.execute("SELECT * FROM employees")
        employees = cur.fetchall()

        employees_list = []

        for employee in employees:
            employee_dict = {
                "id": employee[0],
                "name": f"{employee[1]} {employee[2]}",
                "phone number": employee[3],
                "hourly rate": employee[4],
                "unpaid hours": employee[5],
                "unpaid amount": employee[6],
                "unpaid misc": employee[8],
                "debt": employee[7]
            }

            employees_list.append(employee_dict)

        return json.dumps(employees_list, indent=4)

    date = datetime.now(tz)
    date_formatted = date.strftime('%m_%d_%y')

    file_location = f"C:\FinanceManager\Exports\{date_formatted}"
    file_name = f"{file_location}\employee_information_{date_formatted}.json"

    log_file = open(f"{file_name}", "w")
    log_file.write(employees_to_json(cur))
    log_file.close()


# Exports log data
def export_logs(con, cur):
    def logs_to_json(cur):
        cur.execute("SELECT * FROM logs")
        logs = cur.fetchall()

        logs_list = []

        for log in logs:
            log_dict = {
                "id": log[0],
                "date": log[1],
                "name": log[2],
                "action": log[3],
                "amount": log[4]
            }
            logs_list.append(log_dict)

        return json.dumps(logs_list, indent=4)

    date = datetime.now(tz)
    date_formatted = date.strftime('%m_%d_%y')

    file_location = f"C:\FinanceManager\Exports\{date_formatted}"
    file_name = f"{file_location}\log_{date_formatted}.json"

    log_file = open(f"{file_name}", "w")
    log_file.write(logs_to_json(cur))
    log_file.close()

    update_table(con, cur, "DELETE FROM logs")


# Exports all employee and log data
def export(con, cur):
    date = datetime.now(tz)

    path = f"C:\FinanceManager\Exports\{date.strftime('%m_%d_%y')}"

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s" % path)

    export_employee_info(cur)
    print("Employee information exported!")
    export_logs(con, cur)
    print("Log information exported!")


# Creates a new employee
def create_employee(con, cur):
    print("Employee creation started. Type 0 in any of the fields to stop creation and return to the main menu.")

    # Collecting employee information
    first_name = input("Enter a first name:\n> ")
    last_name = input("Enter a last name:\n> ")
    phone_number = int(input("Enter a phone number:\n> "))
    hourly_pay = int(input("Enter an hourly pay:\n> "))
    unpaid_hours = 0
    unpaid_amount = 0
    debt = 0
    unpaid_amount_misc = 0

    print(f"New Employee Information:\n"
          f"Name: {first_name} {last_name}\n"
          f"Phone Number: {phone_number}\n"
          f"Hourly Pay: {hourly_pay}\n")

    confirmation = input("Do you confirm these details? (Y or N)\n")

    if confirmation.lower() == "y":
        employee_information = (
            first_name, last_name, phone_number, hourly_pay, unpaid_hours, unpaid_amount, debt, unpaid_amount_misc)
        update_table(con, cur, "INSERT INTO employees(first_name, last_name, phone_number, hourly_pay, "
                               "unpaid_hours, unpaid_amount, debt, unpaid_amount_misc) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ",
                     employee_information)

        add_log(con, cur, format_log(datetime.now(tz), f"{first_name} {last_name}", "CREATED", phone_number))

    elif confirmation.lower() == "n":
        print("Sending back to main menu...")
    else:
        print("I don't understand your input. Sending back to main menu...")


# Deletes an employee
def delete_employee(con, cur):
    view_employees(con)
    employee_selection = int(input("Please enter the id of the employee you're wanting to delete...\n> "))

    if check_employee(con, employee_selection):
        employee_information = view_employee(con, employee_selection)
        confirmation = input("Do you confirm this is the employee you're wanting to delete (Y or N)?\n> ")

        if confirmation.lower() == "y":
            add_log(con, cur, format_log(datetime.now(tz), employee_information["name"], "DELETED",
                                         employee_information["phone number"]))
            update_table(con, cur, "DELETE FROM employees WHERE id IS ?", (employee_selection,))
            print("Employee deleted!")

        elif confirmation.lower() == "n":
            print("Sending back to main menu...")

        else:
            print("I don't understand your input. Sending back to main menu...")


# Quits the program
def quit_program(con):
    print("Thanks for using the employee program!")
    con.close()
    quit("Exited")