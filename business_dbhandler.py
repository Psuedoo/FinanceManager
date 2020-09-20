import os
import sqlite3

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


# Connects to the DB
def db_connect(db_path=DEFAULT_PATH):
    conn = sqlite3.connect(db_path)
    return conn


# Displays Cash On Hand
def view_cash_on_hand(conn):
    cur = conn.cursor()
    cur.execute("SELECT cash_on_hand FROM business_money")

    rows = cur.fetchall()
    print("Cash on Hand: ", end="")
    for row in rows:
        print(row[0])


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