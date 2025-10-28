import os
import magic
import csv

def is_xml_file(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return file_type == 'application/xml' or file_type == 'text/xml'

def extract_xml_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def traverse_and_save_xml(folder_path, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['line_text_number', 'line_text_content', 'row_number','table_name','storage_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        line_text_number = 1
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_xml_file(file_path):
                    xml_content = extract_xml_content(file_path)
                    writer.writerow({
                        'line_text_number': "XML "+line_text_number,
                        'line_text_content': xml_content,
                        
                        'row_number':"This line content comes from xml file, does not have row_number",
                        'table_name':"This line content comes from xml file, does not have table_name",
                        'storage_path': file_path

                    })
                    line_text_number += 1