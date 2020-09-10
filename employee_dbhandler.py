import os
import sqlite3
from datetime import datetime
from pytz import timezone

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

tz = timezone('EST')


# Connects to the DB
def db_connect(db_path=DEFAULT_PATH):
    conn = sqlite3.connect(db_path)
    return conn


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
def log_employee_hours(con, cur, id, hours):
    if id == "*":
        cur.execute("SELECT * FROM employees")
        selected_employees = cur.fetchall()

        for employee in selected_employees:
            employee_name = f"{employee[1]} {employee[2]}"

            add_log(con, cur, format_log(datetime.now(tz), employee_name, "WORKED", hours))

            update_table(con, cur, "UPDATE employees SET unpaid_hours = unpaid_hours + %i WHERE id IS %s" % (
                hours, employee[0]))

    else:

        cur.execute("SELECT * FROM employees WHERE id IS %i" % id)
        selected_employee = cur.fetchall()

        for row in selected_employee:
            employee_name = f"{row[1]} {row[2]}"

        add_log(con, cur, format_log(datetime.now(tz), employee_name, "WORKED", hours))

        update_table(con, cur, "UPDATE employees SET unpaid_hours = unpaid_hours + %i WHERE id IS %i" % (hours, id))

    fix_pay(con, cur)


# Edits balance of employee
def pay_employee(con, cur, id, amount_paid):
    cur.execute("SELECT * FROM employees WHERE id IS %i" % id)
    selected_employee = cur.fetchall()

    for row in selected_employee:
        employee_name = f"{row[1]} {row[2]}"

    add_log(con, cur, format_log(datetime.now(tz), employee_name, "PAID", amount_paid))

    update_table(con, cur, "UPDATE employees SET unpaid_amount = unpaid_amount - %i WHERE id IS %i" % (amount_paid, id))

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
def borrow(con, cur, id, borrowed_amount):
    cur.execute("SELECT * FROM employees WHERE id IS %i" % id)
    selected_employee = cur.fetchall()

    for row in selected_employee:
        employee_name = f"{row[1]} {row[2]}"

    add_log(con, cur, format_log(datetime.now(tz), employee_name, "BORROWED", borrowed_amount))

    update_table(con, cur, "UPDATE employees SET unpaid_amount_misc = unpaid_amount_misc + %i WHERE id IS %i" % (
        borrowed_amount, id))


# Use this to loan money to an employee
def loan(con, cur, id, loan_amount):
    cur.execute("SELECT * FROM employees WHERE id IS %i" % id)
    selected_employee = cur.fetchall()

    for row in selected_employee:
        employee_name = f"{row[1]} {row[2]}"

    add_log(con, cur, format_log(datetime.now(tz), employee_name, "LOANED", loan_amount))

    update_table(con, cur, "UPDATE employees SET debt = debt + %i WHERE id IS %i" % (loan_amount, id))


# Use this to pay off employee misc
def pay_employee_misc(con, cur, id, amount_paid):
    cur.execute("SELECT * FROM employees WHERE id IS %i" % id)
    selected_employee = cur.fetchall()

    for row in selected_employee:
        employee_name = f"{row[1]} {row[2]}"

    add_log(con, cur, format_log(datetime.now(tz), employee_name, "PAID", amount_paid))

    update_table(con, cur,
                 "UPDATE employees SET unpaid_amount_misc = unpaid_amount_misc - %i WHERE id IS %i" % (amount_paid, id))


# Use this to take away from employee debt
def employee_paid_debt(con, cur, id, amount_paid):
    cur.execute("SELECT * FROM employees WHERE id IS %i" % id)
    selected_employee = cur.fetchall()

    for row in selected_employee:
        employee_name = f"{row[1]} {row[2]}"

    add_log(con, cur, format_log(datetime.now(tz), employee_name, "RECEIVED", amount_paid))

    update_table(con, cur, "UPDATE employees SET debt = debt - %i WHERE id IS %i" % (amount_paid, id))
