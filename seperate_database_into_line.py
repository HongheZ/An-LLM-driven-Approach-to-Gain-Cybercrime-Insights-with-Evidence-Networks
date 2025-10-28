import Preprocess_DataBaseFile
##test, not be used now

def seperate_database_into_line():
    database_data= Preprocess_DataBaseFile.database_To_Txt("/home/hzhou/llama2/llama/example2.db")
    for i, line in enumerate(database_data):
        # print(type(line))
        line_string = str(line)
        print(i)
        print(line_string)
        # return line_string
     

