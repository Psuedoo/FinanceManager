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
def format_log(date, action, amount, job_payment="N", description="N/A"):
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


# Checks/Get cash on hand
def get_cash_on_hand(con):
    cur = con.cursor()
    cur.execute("SELECT cash_on_hand FROM business_money")
    rows = cur.fetchall()
    for row in rows:
        cash_on_hand = row[0]
        break

    return cash_on_hand


# Displays Cash On Hand
def view_cash_on_hand(con):
    if get_cash_on_hand(con):
        cur = con.cursor()
        cur.execute("SELECT cash_on_hand FROM business_money")

        rows = cur.fetchall()

        print("Cash on Hand: ", end="")
        for row in rows:
            print(row[0])
            break
    else:
        print("There is no cash on hand.")


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
            6. Other (Please Specify)
            """
            job_types = {
                1: "plumbing",
                2: "framing/construction",
                3: "painting/finishing",
                4: "floors",
                5: "roofing/siding",
                6: "other: "
            }

            print(job_type_menu)

            while True:
                try:
                    job_selection = int(input("Please select a job type..\n> "))

                    if job_selection == 6:
                        specific_input = "other: " + input("Please specify: ")

                    else:
                        specific_input = job_types[job_selection]
                    break

                except ValueError as error:
                    print(error)

            add_log(con, cur, format_log(datetime.now(tz), "DEPOSITED", deposit_amount, "Y",
                                         specific_input))

        else:
            add_log(con, cur, format_log(datetime.now(tz), "DEPOSITED", deposit_amount))

        print("Money successfully deposited.")


# Withdraws money
def withdraw(con):
    cur = con.cursor()

    amount = get_cash_on_hand(con)

    if amount <= 0:
        print("There's no money to withdraw.")
        return

    with_drawn_amount = int(input("How much would you like to withdraw?\n> "))

    if with_drawn_amount in range(amount):
        update_table(con, cur, "UPDATE business_money SET cash_on_hand = cash_on_hand - ?", (with_drawn_amount,))
        add_log(con, cur, format_log(datetime.now(tz), "WITHDRAW", with_drawn_amount))


# Displays Material Amount
def view_material_amount(con):
    cur = con.cursor()

    cur.execute("SELECT material FROM business_money")

    rows = cur.fetchall()

    for row in rows:
        material = row[0]
        break
    print(f"Material: {material}")


# Displays Unpaid Collections
def view_unpaid_collections(con):
    cur = con.cursor()

    cur.execute("SELECT unpaid_collections FROM business_money")

    rows = cur.fetchall()

    for row in rows:
        unpaid_collections = row[0]
        break
    print(f"Unpaid Collections: {unpaid_collections}")


# Displays Debt
def view_debt(con):
    cur = con.cursor()

    cur.execute("SELECT debt FROM business_money")

    rows = cur.fetchall()

    for row in rows:
        debt = row[0]
        break
    print(f"Debt: {debt}")


# Displays Utilities
def view_utilities(con):
    cur = con.cursor()

    cur.execute("SELECT utilities FROM business_money")

    rows = cur.fetchall()

    for row in rows:
        utilities = row[0]
        break
    print(f"Utilities: {utilities}")


# Quits the program
def quit_program(con):
    print("Thanks for using the business program!")
    con.close()
    quit("Exited")
