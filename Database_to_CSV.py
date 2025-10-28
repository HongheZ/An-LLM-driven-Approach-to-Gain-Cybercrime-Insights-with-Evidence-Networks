import sqlite3
import csv
import os

def export_database_to_csv(database_path,output_folder):
    # Create a folder with the database name if it doesn't exist
    
    database_name = os.path.basename(database_path)
    database_storage_folder_name = os.path.dirname(database_path)
    database_storage_parent_folder_name = os.path.basename(os.path.dirname(database_storage_folder_name))  #package name
    counter = 1
    folder_name = output_folder+"/DatabaseToCSV__"+database_storage_parent_folder_name+"__"+database_name.replace('/', '_') 
    #if folder_name exist, add a number after the file name 
    counter = 1
    while os.path.exists(folder_name):
        # Create a new folder name by appending the counter
        folder_name = folder_name+str(counter)
        counter += 1

    csv_database_information="/home/hzhou/llama2/llama/experiment_result/database_information.csv"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"This is folder name:{folder_name}")

    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    
    cursor = conn.cursor()

    # Get table names from the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(tables)
    for table in tables:
        conn.text_factory = str
        table_name = table[0]
        csv_filename = f"{folder_name}/{table_name}.csv"
        print(f"csv name is : {csv_filename}")
        # Fetch data from the table
        try:
            sql=f"""SELECT * FROM \"{table_name}\";"""
            cursor.execute(sql)
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            # 如果捕捉到 OperationalError，则执行以下代码块
            try:
                conn.text_factory = bytes
                cursor.execute(f"SELECT * FROM \"{table_name}\";")
                rows = cursor.fetchall()
            except sqlite3.OperationalError as e:
                print(f"Error: {e}")
                continue
        except sqlite3.DatabaseError:
            continue
        # rows = cursor.fetchall()

        # Write data to a CSV file
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cursor.description])  # Write column headers
            csv_writer.writerows(rows)

        print(f"Table '{table_name}' exported to '{csv_filename}'")
    #record the database name and its orginal storage path
    with open(csv_database_information, 'a+', encoding='utf-8') as csvfile:
        fieldnames = ['database_name','original_storage_path', 'after_transfer_folder_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader() 
        writer.writerow({
            'database_name': database_name,
            'original_storage_path': database_path,
    
            'after_transfer_folder_name': folder_name,

        })        



    # Close the database connection
    conn.close()


    

