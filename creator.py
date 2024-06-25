import sqlite3


con = sqlite3.connect("database.db")


cursor = con.cursor()


#table name= users

cursor.execute("""CREATE TABLE users
    (name text,
    password text)
    



""")
