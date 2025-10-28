import magic

def file_type_identify(file_path):
    # 使用 magic number 来检查文件类型
    
    
    try:                  
        file_type = magic.from_file(file_path, mime=True)
        # 这里假设数据库文件的 magic number 为 "SQLite database"
        if("sqlite3" in str(file_type)):
            return "SQLite database"
        else:
            return "It is not a database file"
    except FileNotFoundError:
        print(f"No such file or directory, skip {file_path}")

    try:                  
        file_type = magic.from_file(file_path, mime=True)
        # 这里假设数据库文件的 magic number 为 "SQLite database"
        if("text/xml" in str(file_type)):
            return "xml"
        else:
            return "It is not a xml file"
    except FileNotFoundError:
        print(f"No such file or directory, skip {file_path}")