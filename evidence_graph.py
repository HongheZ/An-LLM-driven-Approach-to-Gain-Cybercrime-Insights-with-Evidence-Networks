import os
import csv
import pandas as pd
import sameline_value
import string

##Database file: 
#Step1: seperate the evidences into nodes and get the same line relationship edge
def db_transfer_graph_step1_sameline(input_file, step1_output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as result_file:
        
        result_reader = csv.DictReader(result_file)
        
        # 初始化step1的grapgh的csv文件的字段和数据结构
        fieldnames = ['node_evidence_number','node_evidence', 'evidence_type', 'edge_relationship_sameline','table_name', 'row_number','storage_path']
               
        with open(step1_output_file, 'w', newline='', encoding='utf-8') as graph_file:
            # 使用DictWriter写入新csv文件
            result_writer = csv.DictWriter(graph_file, fieldnames=fieldnames)
            result_writer.writeheader()
            
            # 遍历input_file(langchain生成的csv文件)中的每一行,并分析该行中的所有evidence，并生成点
            for row in result_reader:
                current_line_text_content= row['line_text_content']
                current_line_number=row['line_text_number']
                row_number= row["row_number"]
                storage_path= row['storage_path']
                evidence_name_lines = row['name'].split('\n')
                evidence_address_lines = row['address'].split('\n')
                evidence_phone_number_lines = row['phone_number'].split('\n')
                evidence_email_lines= row['email'].split('\n')
                evidence_username_lines = row['username'].split('\n')
                # evidence_appname_lines = row['appname'].split('\n')                                               
                
                #临时代码，在xml文件中取出的证据的编号前加XML，防止和database的证据编号重复                
                if storage_path.endswith("xml"):
                    current_line_number="XML "+current_line_number
            
                
                # 处理edge_relationship_sameline的值
                number=0 #这个是表示这是一行中第几个evidence的number，之后用来和line_text_number组合
                #生成一个大的list，包含该行内的所有evidence的number，name

                evidence_name_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_name_lines,number,current_line_number,"name")
                evidence_address_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_address_lines,number,current_line_number,"address")
                evidence_phone_number_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_phone_number_lines,number,current_line_number,"phone number")
                evidence_email_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_email_lines,number,current_line_number,"email")
                evidence_username_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_username_lines,number,current_line_number,"user name")
                # evidence_appname_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_appname_lines,number,current_line_number,"app name")
                
                combined_evidence_dictlist = (evidence_name_lines_dictlist + 
                                     evidence_address_lines_dictlist +
                                     evidence_phone_number_lines_dictlist +
                                     evidence_email_lines_dictlist +
                                     evidence_username_lines_dictlist 
                )
                
                #traverse all evidence
                for evidence_item in combined_evidence_dictlist:
                    sameline_values = []  # 用于存储同一行的数据                    
                    
                    ## In the first time analyze, run these code. After check whehther the result exist, can comment these code
                    # if(evidence_item['evidence_content'] not in current_line_text_content):
                    #     if(preprocess_string(evidence_item['evidence_content']) not in preprocess_string(current_line_text_content)):    
                    #         print(f"In this line: {current_line_number}, This evidence {evidence_item['evidence_content']} not exist")
                    #         # print(preprocess_string(evidence_item['evidence_content']))
                    #         # print(preprocess_string(current_line_text_content))
                    #         # print(f"{current_line_text_content}")
                    #         continue
                    # if(evidence_item['evidence_type']=="name" and len(evidence_item['evidence_content']) >= 25) :
                    #     print(f"In this line: {current_line_number}, This evidence {evidence_item['evidence_content']} is too long")
                    #     continue                        
                    
                    #If a piece of evidence is recorded multiple times in a row, skip it
                    # if(name_line_item==previous_name_line_item):
                    #     continue
                    # previous_name_line_item=name_line_item
                    
                    if(evidence_item['evidence_content'].startswith("None")):  #判断该行没有该evidence，为None
                        continue
                    if(not evidence_item['evidence_content']):  #判断字符串为空
                        continue

                    
                    sameline_values= sameline_value.edge_sameline_combine(evidence_item,combined_evidence_dictlist)
                                                                       
                    result_writer.writerow({
                        'node_evidence_number':evidence_item["evidence_number"],
                        'node_evidence': evidence_item["evidence_content"],
                        'evidence_type': evidence_item["evidence_type"],
                        'edge_relationship_sameline': sameline_values,
                        'table_name': row['table_name'],
                        'row_number':row_number,
                        'storage_path': row['storage_path']
                    })
                  
                # #traverse name evidence
                # for name_line_item in evidence_name_lines_dictlist:
                #     sameline_values = []  # 用于存储同一行的数据                    
                #     if(name_line_item['evidence_name'] not in current_line_text_content):
                #         print(f"In this line: {current_line_number}, This evidence {name_line_item['evidence_name']} not exist")
                #         continue
                #     elif len(name_line_item['evidence_name']) >= 25:
                #         print(f"In this line: {current_line_number}, This evidence {name_line_item['evidence_name']} is too long")
                #         continue
                        
                #     # #If a piece of evidence is recorded multiple times in a row, skip it
                #     # if(name_line_item==previous_name_line_item):
                #     #     continue
                #     # previous_name_line_item=name_line_item
                    
                #     if(name_line_item['evidence_name'].startswith("None")):
                #         continue
                #     sameline_values= sameline_value.edge_sameline_combine(name_line_item,evidence_name_lines_dictlist,evidence_address_lines_dictlist,
                #                                                            evidence_phone_number_lines_dictlist, evidence_email_lines_dictlist)
                                                                       
                #     result_writer.writerow({
                #         'node_evidence_number':name_line_item["evidence_number"],
                #         'node_evidence': name_line_item["evidence_name"],
                #         'evidence_type': "name",
                #         'edge_relationship_sameline': sameline_values,
                #         'table_name': row['table_name'],
                #         'row_number':row_number,
                #         'storage_path': row['storage_path']
                #     })                  
                
                # #traverse address evidence
                # for address_line_item in evidence_address_lines_dictlist:
                #     if(address_line_item['evidence_name'] not in current_line_text_content):
                #         print(f"In this line: {current_line_number}, This evidence {address_line_item['evidence_name']} not exist")
                #         continue                                        
                #     sameline_values = []  # 用于存储同一行的数据
                    
                #     # #If a piece of evidence is recorded multiple times in a row, skip it
                #     # if(address_line_item==previous_address_line_item):
                #     #     continue
                #     # previous_address_line_item=address_line_item
                    
                #     if(address_line_item['evidence_name'].startswith("None")):
                #         continue
                #     sameline_values = sameline_value.edge_sameline_combine(address_line_item,evidence_address_lines_dictlist,evidence_name_lines_dictlist,
                #                                                            evidence_phone_number_lines_dictlist, evidence_email_lines_dictlist)
                    
                #     result_writer.writerow({
                #         'node_evidence_number':address_line_item["evidence_number"],
                #         'node_evidence': address_line_item["evidence_name"],
                #         'evidence_type': "address",
                #         'edge_relationship_sameline': sameline_values,
                #         'table_name': row['table_name'],
                #         'row_number':row_number,
                #         'storage_path': row['storage_path']
                #     })  
                
                # #traverse phone number evidence 
                # for phone_number_line_item in evidence_phone_number_lines_dictlist:
                    
                #     if(phone_number_line_item['evidence_name'] not in current_line_text_content):
                #         print(f"In this line: {current_line_number}, This evidence {phone_number_line_item['evidence_name']} not exist")
                #         continue
                    
                #     sameline_values = []  # 用于存储同一行的数据
                    
                #     # #If a piece of evidence is recorded multiple times in a row, skip it
                #     # if(phone_number_line_item==previous_phone_number_line_item):
                #     #     continue
                #     # previous_phone_number_line_item=phone_number_line_item
                    
                #     if(phone_number_line_item['evidence_name'].startswith("None")):
                #         continue
                #     sameline_values = sameline_value.edge_sameline_combine(phone_number_line_item,evidence_phone_number_lines_dictlist,
                #                                                            evidence_name_lines_dictlist,
                #                                                            evidence_address_lines_dictlist,
                #                                                            evidence_email_lines_dictlist)
                    
                #     result_writer.writerow({
                #         'node_evidence_number':phone_number_line_item["evidence_number"],
                #         'node_evidence': phone_number_line_item["evidence_name"],
                #         'evidence_type': "phone number",
                #         'edge_relationship_sameline': sameline_values,
                #         'table_name': row['table_name'],
                #         'row_number':row_number,
                #         'storage_path': row['storage_path']
                #     })
                
                # #traverse email evidence
                
                # for email_line_item in evidence_email_lines_dictlist:
                    
                #     if(email_line_item['evidence_name'] not in current_line_text_content):
                #         print(f"In this line: {current_line_number}, This evidence {email_line_item['evidence_name']} not exist")
                #         continue
                    
                #     sameline_values = []  # 用于存储同一行的数据
                    
                #     # #If a piece of evidence is recorded multiple times in a row, skip it
                #     # if(email_line_item==previous_email_line_item):
                #     #     continue
                #     # previous_email_line_item=email_line_item
                    
                #     if(email_line_item['evidence_name'].startswith("None")):
                #         continue
                #     sameline_values = sameline_value.edge_sameline_combine(email_line_item,evidence_email_lines_dictlist,
                #                                                            evidence_name_lines_dictlist,
                #                                                            evidence_address_lines_dictlist,
                #                                                            evidence_phone_number_lines_dictlist
                #                                                            )
                    
                #     result_writer.writerow({
                #         'node_evidence_number':email_line_item["evidence_number"],
                #         'node_evidence': email_line_item["evidence_name"],
                #         'evidence_type': "email",
                #         'edge_relationship_sameline': sameline_values,
                #         'table_name': row['table_name'],
                #         'row_number':row_number,
                #         'storage_path': row['storage_path']
                #     })
                    

#Step2: Get the same table (same file() relationship edge and the same folder relationship edge

def db_transfer_graph_step2_sametable_samedatabase(input_file, step2_output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as result_file:
        reader = csv.DictReader(result_file)
        # 初始化step2的grapgh的csv文件的字段和数据结构
        fieldnames = ['node_evidence_number','node_evidence', 'evidence_type','row_number','table_name', 'storage_path','edge_relationship_sameline', 'edge_relationship_sametable', 'edge_relationship_samedatabase']
        
        with open(step2_output_file, 'w', newline='', encoding='utf-8') as graph_file:
            # 使用DictWriter写入新csv文件
            result_writer = csv.DictWriter(graph_file, fieldnames=fieldnames)
            result_writer.writeheader()
            
        # 遍历input_file中的每一行,这里的输入是step1的output的csv文件    
            for current_index, current_row in enumerate(reader):
                sametable_values = []  # 用于存储同一文件的数据
                samedatabase_values = [] # 用于存储同一文件夹的数据
                current_table_name = current_row['table_name']
                current_evidence_number=current_row['node_evidence_number']
                current_evidence_name = current_row['node_evidence']
                current_storage_path_name = current_row['storage_path'] 
                current_folder_name = os.path.dirname(current_storage_path_name)
                # 从头遍历文件寻找file name一样的行，以及寻找folder一样的行(从storage_path中找)
                current_row_number = current_row['row_number']
                with open(input_file, 'r', newline='', encoding='utf-8') as second_loop:   ##注意：嵌套遍历循环要再次打开csv文件并设置新的读取器对象reader2
                    reader2 = csv.DictReader(second_loop)
                    for next_index, next_row in enumerate(reader2):
                        next_table_name = next_row['table_name']
                        next_evidence_number=next_row['node_evidence_number']
                        next_evidence_name = next_row['node_evidence']
                        next_storage_path_name = next_row['storage_path'] 
                        next_folder_name = os.path.dirname(next_storage_path_name)
                        
                        #如果遍历到的是和当前的同一行，则跳过
                        if(next_index==current_index):
                            continue                
                        # 如果遍历到的行的file_name与当前行相同，则添加关系数据sametable
                        if (next_table_name == current_table_name):
                            sametable_values.append((current_evidence_number, next_evidence_number))
                        # 如果遍历到的行的storage folder与当前行相同，则添加关系数据samedatabase
                        if (next_folder_name == current_folder_name):
                            samedatabase_values.append((current_evidence_number, next_evidence_number))
                    result_writer.writerow({
                        'node_evidence_number':current_evidence_number,
                        'node_evidence': current_row['node_evidence'],
                        'evidence_type': current_row['evidence_type'],
                        'row_number': current_row_number,
                        'table_name':current_table_name,
                        'storage_path':current_storage_path_name,
                        'edge_relationship_sameline': current_row['edge_relationship_sameline'],
                        'edge_relationship_sametable': sametable_values,
                        'edge_relationship_samedatabase': samedatabase_values

                    })


##Xml file:
#Step1: seperate the evidences into nodes and get the same line relationship edge
def xml_transfer_graph_step1_sameline(input_file, step1_output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as result_file:
        
        result_reader = csv.DictReader(result_file)
        
        # 初始化step1的grapgh的csv文件的字段和数据结构
        fieldnames = ['node_evidence_number','node_evidence', 'evidence_type', 'edge_relationship_samefile','table_name', 'row_number','storage_path']
               
        with open(step1_output_file, 'w', newline='', encoding='utf-8') as graph_file:
            # 使用DictWriter写入新csv文件
            result_writer = csv.DictWriter(graph_file, fieldnames=fieldnames)
            result_writer.writeheader()
            
            # 遍历input_file(langchain生成的csv文件)中的每一行,并分析该行中的所有evidence，并生成点
            for row in result_reader:
                evidence_name_lines = row['evidence_name'].split('\n')
                current_line_text_content= row['line_text_content']
                evidence_address_lines = row['evidence_address'].split('\n')
                evidence_phone_number_lines = row['evidence_phone_number'].split('\n')
                evidence_email_lines= row['evidence_email'].split('\n') 
                current_line_number=row['line_text_number']
                row_number= row["row_number"]
                # 处理edge_relationship_sameline的值
                number=0 #这个是表示这是一行中第几个evidence的number，之后用来和line_text_number组合
                #生成一个大的list，包含该行内的所有evidence的number，name

                evidence_name_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_name_lines,number,current_line_number)
                evidence_address_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_address_lines,number,current_line_number)
                evidence_phone_number_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_phone_number_lines,number,current_line_number)
                evidence_email_lines_dictlist,number = sameline_value.create_this_row_evidence_list(evidence_email_lines,number,current_line_number)


                #traverse name evidence
                for name_line_item in evidence_name_lines_dictlist:
                    
                    if(name_line_item['evidence_name'] not in current_line_text_content):
                        print(f"In this line: {current_line_number}, This evidence {name_line_item['evidence_name']} not exist")
                        continue
                    elif len(name_line_item['evidence_name']) >= 25:
                        print(f"In this line: {current_line_number}, This evidence {name_line_item['evidence_name']} is too long")
                        continue
                    
                    
                    sameline_values = []  # 用于存储同一行的数据
                    
                    # #If a piece of evidence is recorded multiple times in a row, skip it
                    # if(name_line_item==previous_name_line_item):
                    #     continue
                    # previous_name_line_item=name_line_item
                    
                    if(name_line_item['evidence_name'].startswith("None")):
                        continue
                    sameline_values= sameline_value.edge_sameline_combine(name_line_item,evidence_name_lines_dictlist,evidence_address_lines_dictlist,
                                                                           evidence_phone_number_lines_dictlist, evidence_email_lines_dictlist)

              
                    
                    
                    result_writer.writerow({
                        'node_evidence_number':name_line_item["evidence_number"],
                        'node_evidence': name_line_item["evidence_name"],
                        'evidence_type': "name",
                        'edge_relationship_samefile': sameline_values,
                        'table_name': row['table_name'],
                        'row_number':row_number,
                        'storage_path': row['storage_path']
                    })                  
                
                #traverse address evidence
                for address_line_item in evidence_address_lines_dictlist:
                    if(address_line_item['evidence_name'] not in current_line_text_content):
                        print(f"In this line: {current_line_number}, This evidence {address_line_item['evidence_name']} not exist")
                        continue
                    
                    sameline_values = []  # 用于存储同一行的数据
                    
                    # #If a piece of evidence is recorded multiple times in a row, skip it
                    # if(address_line_item==previous_address_line_item):
                    #     continue
                    # previous_address_line_item=address_line_item
                    
                    if(address_line_item['evidence_name'].startswith("None")):
                        continue
                    sameline_values = sameline_value.edge_sameline_combine(address_line_item,evidence_address_lines_dictlist,evidence_name_lines_dictlist,
                                                                           evidence_phone_number_lines_dictlist, evidence_email_lines_dictlist)
                    
                    result_writer.writerow({
                        'node_evidence_number':address_line_item["evidence_number"],
                        'node_evidence': address_line_item["evidence_name"],
                        'evidence_type': "address",
                        'edge_relationship_samefile': sameline_values,
                        'table_name': row['table_name'],
                        'row_number':row_number,
                        'storage_path': row['storage_path']
                    })  
                
                #traverse phone number evidence 
                for phone_number_line_item in evidence_phone_number_lines_dictlist:
                    if(phone_number_line_item['evidence_name'] not in current_line_text_content):
                        print(f"In this line: {current_line_number}, This evidence {phone_number_line_item['evidence_name']} not exist")
                        continue 
                    
                    sameline_values = []  # 用于存储同一行的数据
                    
                    # #If a piece of evidence is recorded multiple times in a row, skip it
                    # if(phone_number_line_item==previous_phone_number_line_item):
                    #     continue
                    # previous_phone_number_line_item=phone_number_line_item
                    
                    if(phone_number_line_item['evidence_name'].startswith("None")):
                        continue
                    sameline_values = sameline_value.edge_sameline_combine(phone_number_line_item,evidence_phone_number_lines_dictlist,
                                                                           evidence_name_lines_dictlist,
                                                                           evidence_address_lines_dictlist,
                                                                           evidence_email_lines_dictlist)
                    
                    result_writer.writerow({
                        'node_evidence_number':phone_number_line_item["evidence_number"],
                        'node_evidence': phone_number_line_item["evidence_name"],
                        'evidence_type': "phone number",
                        'edge_relationship_samefile': sameline_values,
                        'table_name': row['table_name'],
                        'row_number':row_number,
                        'storage_path': row['storage_path']
                    })
                
                #traverse email evidence
                
                for email_line_item in evidence_email_lines_dictlist:
                    if(email_line_item['evidence_name'] not in current_line_text_content):
                        print(f"In this line: {current_line_number}, This evidence {email_line_item['evidence_name']} not exist")
                        continue
                    
                    sameline_values = []  # 用于存储同一行的数据
                    
                    # #If a piece of evidence is recorded multiple times in a row, skip it
                    # if(email_line_item==previous_email_line_item):
                    #     continue
                    # previous_email_line_item=email_line_item
                    
                    if(email_line_item['evidence_name'].startswith("None")):
                        continue
                    sameline_values = sameline_value.edge_sameline_combine(email_line_item,evidence_email_lines_dictlist,
                                                                           evidence_name_lines_dictlist,
                                                                           evidence_address_lines_dictlist,
                                                                           evidence_phone_number_lines_dictlist
                                                                           )
                    
                    result_writer.writerow({
                        'node_evidence_number':email_line_item["evidence_number"],
                        'node_evidence': email_line_item["evidence_name"],
                        'evidence_type': "email",
                        'edge_relationship_samefile': sameline_values,
                        'table_name': row['table_name'],
                        'row_number':row_number,
                        'storage_path': row['storage_path']
                    })

def preprocess_string(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation + ' '))
    return text


