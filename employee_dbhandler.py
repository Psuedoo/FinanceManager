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


# Create directories
def create_directories():
    date = datetime.now(tz)

    paths = ["C:\FinanceManager", "C:\FinanceManager\Exports"]

    for path in paths:
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)


# Displays all employees
def view_employees(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees")

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


# Use to run SQL query to table
def update_table(conn, cur, query):
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
        # unpaid_hours = employee[5]
        unpaid_amount = employee[6]

        carry_over_hours = unpaid_amount % hourly_pay

        if carry_over_hours > 0:
            update_table(con, cur, "UPDATE employees SET unpaid_amount = (unpaid_hours * hourly_pay) + %i WHERE id IS "
                                   "%i" % (carry_over_hours, id))
        else:
            update_table(con, cur,
                         "UPDATE employees SET unpaid_amount = (unpaid_hours * hourly_pay) WHERE id IS %i" % id)


# Calculates unpaid hours based on unpaid amount and hourly pay
def fix_hours(con, cur):
    update_table(con, cur, "UPDATE employees SET unpaid_hours = unpaid_amount / hourly_pay")


# Adds unpaid hours to employee
def log_employee_hours(con, cur):
    is_logging = True
    while is_logging:
        view_employees(con)
        employee_selection = int(
            input("Please enter the ID of the employee you're wanting to log hours for (TYPE 8 TO INPUT FOR "
                  "ALL; TYPE 9 TO QUIT)...\n> "))

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
                        cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
                        selected_employee = cur.fetchall()

                        for row in selected_employee:
                            id = row[0]
                            employee_name = f"{row[1]} {row[2]}"

                        add_log(con, cur, format_log(datetime.now(tz), employee_name, "WORKED", hours_input))

                        update_table(con, cur,
                                     "UPDATE employees SET unpaid_hours = unpaid_hours + %i WHERE id IS %i" % (
                                         hours_input, id))

                elif employee_selection == 8:
                    hours_input = int(
                        input("Please enter the amount of hours to add to all employees... (TYPE 0 WHEN "
                              "DONE WITH ALL EMPLOYEES)\n> "))
                    if hours_input == 0:
                        is_same_employee = False
                    else:
                        cur.execute("SELECT * FROM employees")
                        selected_employees = cur.fetchall()

                        for employee in selected_employees:
                            employee_name = f"{employee[1]} {employee[2]}"

                            add_log(con, cur, format_log(datetime.now(tz), employee_name, "WORKED", hours_input))

                            update_table(con, cur,
                                         "UPDATE employees SET unpaid_hours = unpaid_hours + %i WHERE id IS %s" % (
                                             hours_input, employee[0]))

                elif employee_selection == 9:
                    is_same_employee = False
                    is_logging = False
                else:
                    print("There are not employees with that ID.")

    fix_pay(con, cur)


# Edits balance of employee
def pay_employee(con, cur):
    if check_for_unpaid_employees(con):
        view_unpaid_employees(con)
        employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))
        amount_paid = int(input("How much are you wanting to pay that employee?\n> "))

        cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
        selected_employee = cur.fetchall()

        for row in selected_employee:
            id = row[0]
            employee_name = f"{row[1]} {row[2]}"

        add_log(con, cur, format_log(datetime.now(tz), employee_name, "PAID", amount_paid))

        update_table(con, cur,
                     "UPDATE employees SET unpaid_amount = unpaid_amount - %i WHERE id IS %i" % (amount_paid, id))
    else:
        print("There are no unpaid employees.")

    fix_hours(con, cur)


# Displays logs (CURRENTLY DISPLAYS ALL LOGS)
def view_logs(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs")
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


# Use this to create a log for DB
def add_log(conn, cur, log):
    date = log[0]
    name = log[1]
    action = log[2]
    amount = log[3]

    cur.execute("INSERT INTO logs (date, name, action, amount) VALUES (?, ?, ?, ?);", (date, name, action, amount))
    conn.commit()


# Use this to borrow money from an employee
def borrow(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to borrow money from...\n> "))
    cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
    selected_employee = cur.fetchall()

    if selected_employee:
        borrow_amount = int(input("Please enter the amount to borrow from that employee...\n> "))
        for row in selected_employee:
            id = row[0]
            employee_name = f"{row[1]} {row[2]}"

        add_log(con, cur, format_log(datetime.now(tz), employee_name, "BORROWED", borrow_amount))

        update_table(con, cur, "UPDATE employees SET unpaid_amount_misc = unpaid_amount_misc + %i WHERE id IS %i" % (
            borrow_amount, id))
    else:
        print("There are no employees with that ID.")


# Use this to loan money to an employee
def loan(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to loan money to...\n> "))
    cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
    selected_employee = cur.fetchall()
    if selected_employee:
        loan_amount = int(input("Please enter the amount to loan that employee...\n> "))

        for row in selected_employee:
            id = row[0]
            employee_name = f"{row[1]} {row[2]}"

        add_log(con, cur, format_log(datetime.now(tz), employee_name, "LOANED", loan_amount))

        update_table(con, cur, "UPDATE employees SET debt = debt + %i WHERE id IS %i" % (loan_amount, id))
    else:
        print("There are no employees with that ID.")


# Use this to pay off employee misc
def pay_employee_misc(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))
    cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
    selected_employee = cur.fetchall()

    if selected_employee:
        for row in selected_employee:
            id = row[0]
            employee_name = f"{row[1]} {row[2]}"

        amount_paid = int(input("Please enter the amount to pay off employee's misc...\n> "))

        add_log(con, cur, format_log(datetime.now(tz), employee_name, "PAID", amount_paid))

        update_table(con, cur,
                     "UPDATE employees SET unpaid_amount_misc = unpaid_amount_misc - %i WHERE id IS %i" % (
                         amount_paid, id))
    else:
        print("There are no employees with that ID.")


# Use this to take away from employee debt
def employee_paid_debt(con, cur):
    employee_selection = int(input("Please enter the ID of the employee you're wanting to pay...\n> "))
    cur.execute("SELECT * FROM employees WHERE id IS %i" % employee_selection)
    selected_employee = cur.fetchall()

    if selected_employee:
        for row in selected_employee:
            id = row[0]
            employee_name = f"{row[1]} {row[2]}"
        amount_paid = int(input("Please enter the amount employee paid off their debt...\n> "))

        add_log(con, cur, format_log(datetime.now(tz), employee_name, "RECEIVED", id))

        update_table(con, cur,
                     "UPDATE employees SET debt = debt - %i WHERE id IS %i" % (amount_paid, id))


# Use this to view total amount owed
def view_amount_owed(con, cur):
    cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    total_amount_owed = 0

    for employee in employees:
        unpaid_amount = employee[6]
        unpaid_misc = employee[8]
        total_amount_owed += unpaid_amount + unpaid_misc

    print(f"Total Amount Owed:\t{total_amount_owed}")


# Use this to export employee data
def export_employee_info(con, cur):
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


# Use this to export log data
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


# Use this to export all employee and log data
def export(con, cur):
    date = datetime.now(tz)

    path = f"C:\FinanceManager\Exports\{date.strftime('%m_%d_%y')}"

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s" % path)

    export_employee_info(con, cur)
    print("Employee information exported!")
    export_logs(con, cur)
    print("Log information exported!")


# Use this to quit the program
def quit_program(using_program, con):
    print("Thanks for using hte employee program!")
    using_program = False
    con.close()
