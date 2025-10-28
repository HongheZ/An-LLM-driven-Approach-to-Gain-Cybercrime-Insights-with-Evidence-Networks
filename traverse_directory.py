import os
import json
import my_argumentparser

#My code

##Get the command-line arguments and store in the "args" variable
# args = my_argumentparser.parse_arguments()

##Get the directory from user input
# input_directory = args.input_path
# print(input_directory)

def traverse_directory(directory_path):
    # Initialize an empty list to store file information
    all_file_info_list = []
    db_file_info_list = []
    # Traverse the directory
    #root : Prints out directories  what you specified.
    #dirs : Prints out sub-directories from root.
    #files : Prints out all files from root and directories.
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)


            # file_extension = os.path.splitext(file)[-1]  # Get the file extension

            # Get the file name and extension
            file_name, file_extension = os.path.splitext(file)
            # Create a dictionary with file information
            file_info = {
                "file_name": file_name,
                "file_path": file_path,
                "file_extension": file_extension
            }

            # Append all file information to the list
            all_file_info_list.append(file_info)

            # Append db files information to the list
            if file_extension == ".db":
                db_file_info_list.append(file_info)


    # Convert the list to a JSON object
    # json_data = json.dumps(db_file_info_list, indent=4)
    return  db_file_info_list
# Print or save the JSON data


# json_data=traverse_directory(input_directory)
# print(json_data)