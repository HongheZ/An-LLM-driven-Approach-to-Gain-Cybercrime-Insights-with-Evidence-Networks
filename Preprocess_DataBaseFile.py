#Transfer a databse file to a text file
import sqlite3

def database_To_Txt(databaseName):
    connection = sqlite3.connect(databaseName) #Connect to the SQLite database file (.db):
    cursor = connection.cursor()        #Create a cursor object to execute SQL queries:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")# Get the list of all tables in the database
    tables = cursor.fetchall()    #Fetch the table names using fetchall()
    all_data = []       #
    # Loop through each table and fetch all data
    for table in tables:
        table_name = table[0]
        print(table_name)
        cursor.execute(f'''SELECT * FROM  "{table_name}"''')
        data = cursor.fetchall()
        all_data.extend(data)       # Append the data to the all_data list

        # print(f"Data from table '{table_name}':")
        # for row in data:
        #     print(row)

    ##Save all data to a single text file
    with open('Line_test_data.txt', 'a+') as txt_file:   ##a+:will add content below the last content. w+:will delte original content
        for row in all_data:
            txt_file.write(', '.join(map(str, row)) + '\n')


    cursor.close()      #Close the cursor
    connection.close()      #Close the database connection
    return all_data


    #
    # with open('output.txt', 'w') as text_file:
    #     for row in data:
    #         text_file.write(' '.join(map(str, row)) + '\n')