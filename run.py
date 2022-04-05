from app import app


if (__name__ == '__main__'):  #To tell the program to execute app.py file.
    app.run(debug=True, port=5050)  #It is specified so that on saving the data, it gets automatically saved over the server.
    #While in Production mode, it is turned False.