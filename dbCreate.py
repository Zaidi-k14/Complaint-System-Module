#Importing our mysql connector to connect with Python interpreter:
import mysql.connector

my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    port=3306
    )


if (my_db.is_connected()):
    print("Congratulations! Your MYSQL connection is established.")

else:
    print("Sorry! No connection set up till now")
    print(my_db.is_connected())  #To check whether the connection of Mysql is established or not.


my_cursor = my_db.cursor()


#Creating our database named 'mycms_db':
my_cursor.execute("CREATE DATABASE mycms_db")


#Viewing our created database:
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)

