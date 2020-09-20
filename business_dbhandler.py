import os
import sqlite3
from _datetime import datetime
from pytz import timezone

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

tz = timezone('EST')


# Connects to the DB
def db_connect(db_path=DEFAULT_PATH):
    conn = sqlite3.connect(db_path)
    return conn


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


# Displays logs (CURRENTLY DISPLAYS ALL LOGS)
def view_logs(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM business_logs LIMIT 15")
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
def format_log(date, action, amount, job_payment, description="N/A"):
    log = [date.strftime("%x %X"), action, amount, job_payment, description]
    print(log)
    return log


# Creates a log for DB
def add_log(conn, cur, log):
    date = log[0]
    action = log[1]
    amount = log[2]
    job_payment = log[3]
    description = log[4]

    cur.execute("INSERT INTO business_logs (date, action, amount, job_payment, description) VALUES (?, ?, ?, ?, ?);",
                (date, action,
                 amount,
                 job_payment,
                 description))
    conn.commit()


# Displays Cash On Hand
def view_cash_on_hand(conn):
    cur = conn.cursor()
    cur.execute("SELECT cash_on_hand FROM business_money")

    rows = cur.fetchall()
    print("Cash on Hand: ", end="")
    for row in rows:
        print(row[0])


# Deposits Money
def deposit(con):
    cur = con.cursor()

    deposit_amount = int(input("How much money would you like to deposit?\n> "))

    if deposit_amount > 0:
        update_table(con, cur, "UPDATE business_money SET cash_on_hand = cash_on_hand + ?", (deposit_amount,))

        # Determines if a deposit came from a job
        job_payment = input("Did money come from a job? (Y or N)\n> ")
        if job_payment == "y":
            job_type_menu = """
            1. Plumbing
            2. Framing/Construction
            3. Painting/Finishing
            4. Floors
            5. Roofing/Siding
            """
            job_types = {
                1: "plumbing",
                2: "framing/construction",
                3: "painting/finishing",
                4: "floors",
                5: "roofing/siding"
            }

            print(job_type_menu)

            add_log(con, cur, format_log(datetime.now(tz), "DEPOSITED", deposit_amount, "Y",
                                         job_types[int(input("Please select a job type..\n> "))]))

        else:
            add_log(con, cur, format_log(datetime.now(tz), "DEPOSITED", deposit_amount))

        print("Money successfully deposited.")


# Displays Payroll
def view_payroll(conn):
    return


# Displays Material Amount
def view_material_amount(conn):
    return


# Displays Unpaid Collections
def view_unpaid_collections(conn):
    return


# Displays Debt
def view_debt(conn):
    return


# Displays Utilities
def view_utilities(conn):
    return


# Quits the program
def quit_program(con):
    print("Thanks for using the business program!")
    con.close()
    quit("Exited")
