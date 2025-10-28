#Use chatgpt and Langchain to analyze the csv file(after preprocess)

import warnings
warnings.filterwarnings('ignore')
import ast
import os
import re
import pandas as pd
from google_play_scraper import app
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
# os.environ["OPENAI_API_KEY"] = ""

# account for deprecation of LLM model
import datetime
import time
# Get the current date
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
import csv
import tiktoken
from langchain.text_splitter import TokenTextSplitter

from openai import OpenAI
import openai

import json
import re
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import AzureChatOpenAI
import os

# Set up the environment variables for your Azure OpenAI credentials
os.environ['AZURE_OPENAI_API_KEY'] = '*************'
# os.environ['OPENAI_API_TYPE'] = 'azure'
os.environ['OPENAI_API_VERSION'] = '2023-03-15-preview'
os.environ['AZURE_OPENAI_ENDPOINT'] = "*************"
os.environ["AZURE_OPENAI_CHATGPT_DEPLOYMENT"] = '*************'

AZURE_OPENAI_CHATGPT_DEPLOYMENT1= '*************'

OPENAI_API_KEY= '*************'

def Langchain_chatgpt_analyze(request_chain):

    # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
    # llm = ChatOpenAI(temperature=0, model="gpt-4o")
    llm = AzureChatOpenAI(deployment_name=AZURE_OPENAI_CHATGPT_DEPLOYMENT1, temperature=0)

    class Prompt:
        def __init__(self, prompt_content, chain):
            self.prompt_content = prompt_content
            self.chain = chain
    

    ###prompt template
    ## prompt template 1: extract people's real names
    #The people's names here includes people's real name or people's user name
    prompt_name = ChatPromptTemplate.from_template(
        """You are an expert text analyzer specializing in extracting real people's full names from text.
        You should only extract real names and ignore usernames, nicknames, or other non-real names.
        Preserve the original format of the names exactly as they appear in the input, including underscores or other characters.
        If you find any real people's names, output each one you found line by line.
        If you can't find any real people's names in the text, only output "None".
        Before outputting, ensure that each name is a real person's name and not a username or nickname.
        Here is the text line:
        {input}"""
    )

    # chain 1: input= input text line and output= real_name
    chain_name = LLMChain(llm=llm, prompt=prompt_name, 
                        output_key="name"
                        )
    
    name=Prompt(prompt_name,chain_name)
    ## prompt template 2: extract addresses
    # address_prompt = ChatPromptTemplate.from_template(
    #     """ You are a good text analyzer. \
    # You are great at extracting addreses or locations from the text\
    # If you find addreses or locations in the text\
    # Only output each address or location you found line by line\
    # The address or location here is physical address or geographic location, not not a web address\
    # If you can't find any address or location in the text\
    # only output "None"\
    # Before output, check it again\
    # Here is the text line:
    # {input}"""
    # )
    prompt_address = ChatPromptTemplate.from_template(
    """You are an expert text analyzer specializing in extracting physical addresses or geographic locations from text.
    Only extract full addresses or detailed locations, such as street addresses, building names, or landmarks with additional context (e.g., city and street).
    Do not extract single city names, country names, or any incomplete addresses that do not provide specific location details.
    If you find any complete physical addresses or detailed locations, output each one you found line by line.
    If you can't find any valid address or location in the text, only output "None".
    Before outputting, ensure that each entry is a complete and valid address or location, not a web address or an isolated city or country name.
    Here is the text line:
    {input}"""
    )


    # chain 2: input= input= input (text line) and output= address
    chain_address = LLMChain(llm=llm, prompt=prompt_address, 
                        output_key="address"
                        )
    address=Prompt(prompt_address,chain_address)

    ## prompt template 3: extract phone number
    # phone_prompt = ChatPromptTemplate.from_template(
    #     """ You are a good text analyzer. \
    # You are great at extracting United States phone number from the text\
    # If you find United States phone number in the text\
    # Only output each United States phone number you found line by line\
    # If you can't find any United States phone number in the text\
    # only output "None"\
    # Before output, check it again\
    # Here is the text line:
    # {input}"""
    # )
    prompt_phone = ChatPromptTemplate.from_template(
        """You are an expert text analyzer specializing in extracting United States phone numbers from text.
        Only extract complete and valid United States phone numbers, which typically follow formats like (123) 456-7890, 123-456-7890, +11234567890, +1 (123) 456-7890 or +1 123-456-7890.
        Retain the exact formatting of the phone number as it appears in the input, including any parentheses, dashes, or spaces.
        Do not extract partial numbers or segments from longer numeric strings.
        Ensure the extracted phone number has exactly 10 digits (excluding country code and special characters) and is formatted correctly as a U.S. phone number.
        If you find any valid U.S. phone numbers, output each one you found line by line.
        If you can't find any valid U.S. phone numbers in the text, only output "None".
        Before outputting, verify that each number is a complete U.S. phone number and not an unrelated numeric string or partial number.
        Here is the text line:
        {input}"""
    )


    # chain 3: input= input= input (text line) and output= phone_number
    chain_phone = LLMChain(llm=llm, prompt=prompt_phone, 
                        output_key="phone_number"
                        )
    phone=Prompt(prompt_phone,chain_phone)
    
    ## prompt template 4: extract email 
    # email_prompt = ChatPromptTemplate.from_template(
    #     """ You are a good text analyzer. \
    # You are great at extracting email addresses from the text\
    # If you find email addresses in the text\
    # Only output each email address you found line by line\
    # If you can't find any email addresses in the text\
    # only output "None"\
    # Before output, check it again\
    # Here is the text line:
    # {input}"""
    # )
    prompt_email = ChatPromptTemplate.from_template(
        """You are an expert text analyzer specializing in extracting standard email addresses from text.
        Only extract valid email addresses that are typically used for communication (e.g., user@example.com).
        Do not extract app-specific identifiers or addresses associated with messaging platforms, such as those ending in domains like "@talk.kik.com" or "@s.whatsapp.net".
        Ensure that the domain names are commonly used for communication (e.g., gmail.com, yahoo.com, company domains) and not associated with automated services or apps.
        If you find any valid email addresses, output each one you found line by line.
        If you can't find any valid email addresses in the text, only output "None".
        Before outputting, ensure that each email address is not an app-specific identifier and adheres to standard email address formats.
        Here is the text line:
        {input}"""
    )


    # chain 4: input= input= input (text line) and output= email
    chain_email = LLMChain(llm=llm, prompt=prompt_email, 
                        output_key="email"
                        )
    
    email=Prompt(prompt_email,chain_email)


    #prompt template 5: extract peolpe's account name
    prompt_username = ChatPromptTemplate.from_template(
        """You are an expert text analyzer specializing in extracting usernames from text.
        A username here is defined as a nickname or alias, often consisting of letters or a combination of letters and numbers.
        Do not extract real people's names. Focus only on identifiers that are typically used as usernames or online aliases.
        Retain the exact format of the usernames as they appear in the input, and do not add any extra symbols, such as quotation marks or special characters.
        Avoid extracting random strings of letters and numbers; only include those that are likely to be usernames.
        If you find any usernames, output each one you found line by line.
        If you can't find any usernames in the text, only output "None".
        Before outputting, verify that each entry is a probable username or alias, not a real name or unrelated string.
        Here is the text line:
        {input}"""
    )

    # # chain 5: input= input text line and output= account_name
    chain_username = LLMChain(llm=llm, prompt=prompt_username, 
                        output_key="username"
                        )
    
    username=Prompt(prompt_username,chain_username)
    
    #prompt template 6: analyze which app the evidence come from
    prompt_appname = ChatPromptTemplate.from_template(
        """Analyze the following Android app package name and provide the name of the app associated with this package from the Google Play Store or other relevant sources.
        Then, output this app name.
        Only output the app name, and verify that the result corresponds to a real app. 
        If it cannot be determined or verified, output "None". 
        Do not include any explanation or additional text in the output.
        Here is the file path:
        {input}"""
    )

    # # chain 6: input= file path and output= app name
    chain_appname = LLMChain(llm=llm, prompt=prompt_appname, 
                        output_key="appname"
                        )
    
    appname=Prompt(prompt_appname,chain_appname) 
    
    
    
    
    # Dictionary to map request_chain values to their corresponding chain and output variables
    chain_map = {
        "name": {"chain": chain_name, "output_variable": "name"},
        "address": {"chain": chain_address, "output_variable": "address"},
        "phone_number": {"chain": chain_phone, "output_variable": "phone_number"},
        "email": {"chain": chain_email, "output_variable": "email"},
        "username": {"chain": chain_username, "output_variable": "username"},
        "appname": {"chain": chain_appname, "output_variable": "appname"}
    
    }  

    # Check if the request_chain exists in the chain_map
    if request_chain in chain_map:
        # Retrieve the corresponding chain and output variable
        selected_chain = chain_map[request_chain]["chain"]
        output_variable = chain_map[request_chain]["output_variable"]
        
        # Create the SequentialChain using the selected chain and output variable
        overall_chain = SequentialChain(
            chains=[selected_chain],
            input_variables=["input"],
            output_variables=[output_variable],
            verbose=True
        )
    else:
        # Return an error if the request_chain does not match any known chain
        raise ValueError("There is no corresponding chain")

    return overall_chain


def analyze_csv_file(input_file_db, csv_output_file,overall_chain):    
    request_evidence_type=overall_chain.output_variables[0] #get the evidence type in this overall_chain, such as "name","address" or "phone number"
    with open(csv_output_file, 'w', encoding='utf-8') as csvfile:
        # fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path','evidence_name','evidence_address','evidence_phone_number','evidence_email']
        fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path', request_evidence_type]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        #tracer the input file(after preprocess) line by line
        with open(input_file_db, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for index,row in enumerate(csv_reader):
                #only analyze some lines
                # if(index<1000):  
                #     continue
                
                # line = f"""{row["line_text_content"]}"""
                line = row["line_text_content"]
                line_number = row["line_text_number"]
                row_number= row["row_number"]
                #得到这一行语句的token数，判断是否会超过chatgpt3.5的范围
                token_number=num_tokens_from_string(str(line), "gpt-4-turbo")
                if(token_number>10000):
                    split_lines=split_string_based_on_token_number("gpt-4-turbo",10000,str(line))
                    number=0
                    comebine_result=""
                    for index, subline in enumerate(split_lines):

                        subline_number=str(line_number)+"."+str(number)
                        number=number+1
                        
                        try:
                            subline_analyze_result = ""
                            result=overall_chain(subline)
                            print(result)
                            subline_analyze_result = result.get(str(request_evidence_type),"None")

                            # writer.writerow({
                            #     'line_text_number': subline_number,
                            #     'line_text_content': subline,
                            #     'row_number': row_number,
                            #     'table_name': row['table_name'],
                            #     'storage_path': row['storage_path'],
                            #     str(request_evidence_type): result.get(str(request_evidence_type),"None")    #Get the evidence from the dictionary type result from the LLM
                            #     # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                            #     # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                            #     # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                            #     # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                            # })
                        
                        except BaseException as e:   
                            if 'content_filter' in str(e):
                                print(f"Skipping row due to content filter error: {subline_number}")
                                # writer.writerow({
                                #     'line_text_number': subline_number,
                                #     'line_text_content': subline,
                                #     'row_number': row_number,
                                #     'table_name': row['table_name'],
                                #     'storage_path': row['storage_path'],
                                #     str(request_evidence_type): "None(Content filter error)"  # Specific error message for content filtering
                                # })                  

                        #If the result not is "None", combine the answer from chatgpt to the array    
                        if(subline_analyze_result != "None"):
                            comebine_result = comebine_result + "\n" + subline_analyze_result
                    
                    if(comebine_result == ""):
                        comebine_result = "None"
                    subline_number=str(line_number)
                    #After all the subline analyze finish, write the result to the csv file together
                    writer.writerow({
                        'line_text_number': subline_number,
                        'line_text_content': line,
                        'row_number': row_number,
                        'table_name': row['table_name'],
                        'storage_path': row['storage_path'],
                        str(request_evidence_type): comebine_result     #Get the evidence from the dictionary type result from the LLM

                    })    
                        
                                         
                else:                        
                    number=0
                    # subline_number=str(line_number)+"."+str(number)  #为了后面格式好分辨，即使没有分行，也在line_number后加上".0"
                    subline_number=str(line_number)
                    try:
                        result=overall_chain(line)
                        print(result)
                        # 输出的结果是用\n分隔的
                        writer.writerow({
                            'line_text_number': subline_number,
                            'line_text_content': line,
                            'row_number': row_number,
                            'table_name': row['table_name'],
                            'storage_path': row['storage_path'],
                            str(request_evidence_type): result.get(str(request_evidence_type),"None")    #Get the evidence from the dictionary type result from the LLM
                            # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                            # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                            # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                            # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                        })
                    except BaseException as e:   
                            if 'content_filter' in str(e):
                                print(f"Skipping row due to content filter error: {subline_number}")
                                writer.writerow({
                                    'line_text_number': subline_number,
                                    'line_text_content': line,
                                    'row_number': row_number,
                                    'table_name': row['table_name'],
                                    'storage_path': row['storage_path'],
                                    str(request_evidence_type): "None(Content filter error)"  # Specific error message for content filtering
                                })  

#analyze the line has already be detected other evidence, this function used for evidence "username"
def analyze_csv_file_condtion_username(input_file_db, csv_output_file,overall_chain):    
    request_evidence_type=overall_chain.output_variables[0] #get the evidence type in this overall_chain, such as "name","address" or "phone number"
    with open(csv_output_file, 'w', encoding='utf-8') as csvfile:
        # fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path','evidence_name','evidence_address','evidence_phone_number','evidence_email']
        fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path', request_evidence_type]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        #tracer the input file(after preprocess) line by line
        with open(input_file_db, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for index,row in enumerate(csv_reader):
                line = row["line_text_content"]
                line_number = row["line_text_number"]
                row_number = row["row_number"]
                name_evidence = row["name"]
                phone_number_evidence = row["phone_number"]
                address_evidence = row["address"]
                email_evidence = row["email"]
                if(name_evidence == "None" and phone_number_evidence == "None" and 
                   address_evidence == "None" and email_evidence == "None"):
                    writer.writerow({
                        'line_text_number': line_number,
                        'line_text_content': line,
                        'row_number': row_number,
                        'table_name': row['table_name'],
                        'storage_path': row['storage_path'],
                        str(request_evidence_type): "None"    #Get the evidence from the dictionary type result from the LLM
                        # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                        # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                        # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                        # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                    })

                else:                        
                    #得到这一行语句的token数，判断是否会超过chatgpt的范围
                    token_number=num_tokens_from_string(str(line), "gpt-4")
                    if(token_number>10000):
                        split_lines=split_string_based_on_token_number("gpt-4",10000,str(line))
                        number=0
                        comebine_result=""
                        for index, subline in enumerate(split_lines):

                            subline_number=str(line_number)+"."+str(number)
                            number=number+1
                            
                            try:
                                subline_analyze_result = ""
                                result=overall_chain(subline)
                                print(result)
                                subline_analyze_result = result.get(str(request_evidence_type),"None")
  
                            except BaseException as e:   
                                if 'content_filter' in str(e):
                                    print(f"Skipping row due to content filter error: {subline_number}")
                                    # writer.writerow({
                                    #     'line_text_number': subline_number,
                                    #     'line_text_content': subline,
                                    #     'row_number': row_number,
                                    #     'table_name': row['table_name'],
                                    #     'storage_path': row['storage_path'],
                                    #     str(request_evidence_type): "None(Content filter error)"  # Specific error message for content filtering
                                    # })                  

                            #If the result not is "None", combine the answer from chatgpt to the array    
                            if(subline_analyze_result != "None"):
                                comebine_result = comebine_result + "\n" + subline_analyze_result
                        
                        if(comebine_result == ""):
                            comebine_result = "None"
                        subline_number=str(line_number)
                        #After all the subline analyze finish, write the result to the csv file together
                        writer.writerow({
                            'line_text_number': subline_number,
                            'line_text_content': line,
                            'row_number': row_number,
                            'table_name': row['table_name'],
                            'storage_path': row['storage_path'],
                            str(request_evidence_type): comebine_result     #Get the evidence from the dictionary type result from the LLM

                        })    

                    else:                        
                        number=0
                        # subline_number=str(line_number)+"."+str(number)  #为了后面格式好分辨，即使没有分行，也在line_number后加上".0"
                        subline_number=str(line_number)
                        try:
                            result=overall_chain(line)
                            print(result)
                            # 输出的结果是用\n分隔的
                            writer.writerow({
                                'line_text_number': subline_number,
                                'line_text_content': line,
                                'row_number': row_number,
                                'table_name': row['table_name'],
                                'storage_path': row['storage_path'],
                                str(request_evidence_type): result.get(str(request_evidence_type),"None")    #Get the evidence from the dictionary type result from the LLM
                                # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                                # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                                # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                                # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                            })
                        except BaseException as e:   
                                if 'content_filter' in str(e):
                                    print(f"Skipping row due to content filter error: {subline_number}")
                                    writer.writerow({
                                        'line_text_number': subline_number,
                                        'line_text_content': line,
                                        'row_number': row_number,
                                        'table_name': row['table_name'],
                                        'storage_path': row['storage_path'],
                                        str(request_evidence_type): "None(Content filter error)"  # Specific error message for content filtering
                                    })
                    # result=overall_chain(line)
                    # print(result)
                    # number=0
                    # # 输出的结果是用\n分隔的
                    # writer.writerow({
                    #     'line_text_number': line_number,
                    #     'line_text_content': line,
                    #     'row_number': row_number,
                    #     'table_name': row['table_name'],
                    #     'storage_path': row['storage_path'],
                    #     str(request_evidence_type): result.get(str(request_evidence_type),"None")    #Get the evidence from the dictionary type result from the LLM
                    #     # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                    #     # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                    #     # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                    #     # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                    # })

#analyze the app name basedon chatgpt, this function used for evidence "appname"
def analyze_csv_file_gpt_appname(input_file_db, csv_output_file,overall_chain):    
    request_evidence_type=overall_chain.output_variables[0] #get the evidence type in this overall_chain, such as "name","address" or "phone number"
    pattern = r'__([a-zA-Z0-9.]+)__|/([a-zA-Z0-9]+\.[a-zA-Z0-9.]+)/'
    with open(csv_output_file, 'w', encoding='utf-8') as csvfile:
        # fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path','evidence_name','evidence_address','evidence_phone_number','evidence_email']
        fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path', request_evidence_type]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        #tracer the input file(after preprocess) line by line
        with open(input_file_db, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for index,row in enumerate(csv_reader):
                line = row["line_text_content"]
                line_number = row["line_text_number"]
                storage_path = row["storage_path"]
                row_number = row["row_number"]
                name_evidence = row["name"]
                phone_number_evidence = row["phone_number"]
                address_evidence = row["address"]
                email_evidence = row["email"]
                if(name_evidence == "None" and phone_number_evidence == "None" and 
                   address_evidence == "None" and email_evidence == "None"):
                    writer.writerow({
                        'line_text_number': line_number,
                        'line_text_content': line,
                        'row_number': row_number,
                        'table_name': row['table_name'],
                        'storage_path': row['storage_path'],
                        str(request_evidence_type): "None"    #Get the evidence from the dictionary type result from the LLM
                        # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                        # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                        # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                        # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                    })

                else:                                             
                    # subline_number=str(line_number)+"."+str(number)  #为了后面格式好分辨，即使没有分行，也在line_number后加上".0"
                    subline_number=str(line_number)
                    match = re.search(pattern, storage_path)
                    if match:
                        # Return the captured group (the app package name)
                        package_name=match.group(1) or match.group(2)
                    else:
                        package_name="None"
                        print(f"This stroage path does not has the regular package name {storage_path}, its line number is {line_number}")
                        
                    
                    try:
                        result=overall_chain(package_name)
                        print(result)
                        # 输出的结果是用\n分隔的
                        writer.writerow({
                            'line_text_number': subline_number,
                            'line_text_content': line,
                            'row_number': row_number,
                            'table_name': row['table_name'],
                            'storage_path': row['storage_path'],
                            str(request_evidence_type): result.get(str(request_evidence_type),"None")    #Get the evidence from the dictionary type result from the LLM
                            # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                            # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                            # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                            # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                        })
                    except BaseException as e:   
                            if 'content_filter' in str(e):
                                print(f"Skipping row due to content filter error: {subline_number}")
                                writer.writerow({
                                    'line_text_number': subline_number,
                                    'line_text_content': line,
                                    'row_number': row_number,
                                    'table_name': row['table_name'],
                                    'storage_path': row['storage_path'],
                                    str(request_evidence_type): "None(Content filter error)"  # Specific error message for content filtering
                                })


#use regular expression to analyze the storage_path to get which app this row come from
def analyze_csv_file_regular_expression_appname(input_file_db, csv_output_file):    
     #get the evidence type in this overall_chain, such as "name","address" or "phone number"
    pattern = r'__([a-zA-Z0-9.]+)__|/([a-zA-Z0-9]+\.[a-zA-Z0-9.]+)/'
    
    with open(csv_output_file, 'w', encoding='utf-8') as csvfile:
        # fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path','evidence_name','evidence_address','evidence_phone_number','evidence_email']
        fieldnames = ['line_text_number','line_text_content','row_number','table_name', 'storage_path', 'app_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        #tracer the input file(after preprocess) line by line
        with open(input_file_db, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for index,row in enumerate(csv_reader):
                line = row["line_text_content"]
                line_number = row["line_text_number"]
                row_number = row["row_number"]
                storage_path = row["storage_path"]
                name_evidence = row["name"]
                phone_number_evidence = row["phone_number"]
                address_evidence = row["address"]
                email_evidence = row["email"]
                if(name_evidence == "None" and phone_number_evidence == "None" and 
                   address_evidence == "None" and email_evidence == "None"):
                    writer.writerow({
                        'line_text_number': line_number,
                        'line_text_content': line,
                        'row_number': row_number,
                        'table_name': row['table_name'],
                        'storage_path': row['storage_path'],
                        'app_name': "None"    #Get the evidence from the dictionary type result from the LLM
                        # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                        # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                        # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                        # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                    })

                else:                                                         
                    number=0
                    # subline_number=str(line_number)+"."+str(number)  #为了后面格式好分辨，即使没有分行，也在line_number后加上".0"
                    subline_number=str(line_number)
                    match = re.search(pattern, storage_path)
                    if match:
                        # Return the captured group (the app package name)
                        package_name=match.group(1) or match.group(2)
                    else:
                        package_name="None"
                        print(f"This stroage path does not has the regular package name {storage_path}, its line number is {line_number}")
                        
                    try:
                        app_information = app(package_name)
                        app_name=app_information.get("title", "Unknown App")

                    except Exception as e:
                        print(f"This app not found: {package_name}, its line number is {line_number}")
                        app_name = "None"
                    
                            
                    # 输出的结果是用\n分隔的
                    writer.writerow({
                        'line_text_number': subline_number,
                        'line_text_content': line,
                        'row_number': row_number,
                        'table_name': row['table_name'],
                        'storage_path': row['storage_path'],
                        'app_name': app_name   #Get the evidence from the dictionary type result from the LLM
                        # 'evidence_name': result.get('name',"None"),  #从chatgpt的输出的dictionary type的result中得到name的value，如果该值不存在，则返回"none"
                        # 'evidence_address': result.get('address',"None"),  #从chatgpt的输出的dictionary type的result中得到address的value
                        # 'evidence_phone_number': result.get('phone_number',"None"),#从chatgpt的输出的dictionary type的result中得到phone number的value
                        # 'evidence_email':result.get('email',"None")   ##从chatgpt的输出的dictionary type的result中得到email的value
                    })

           






def analyze_csv_file_check_name(csv_input_file, csv_output_file):
    current_date = datetime.datetime.now().date()
    # Define the date after which the model should be set to "gpt-3.5-turbo"
    target_date = datetime.date(2024, 6, 12)
    llm = ChatOpenAI(temperature=0, model="gpt-4-turbo")
    ###prompt template
    ## prompt template 1: extract personal names
    second_check_name_prompt = ChatPromptTemplate.from_template(
        """You are a good text analyzer. \
    Please check the text line below whether is people's name \
    If it is peoples's names, only output "Yes"\
    If not, only output "No"\
    Here is the text line:
    {input}"""
    )
    # chain 1: input= input text line and output= name
    chain_one = LLMChain(llm=llm, prompt=second_check_name_prompt, 
                        output_key="whether_name"
                        )
    second_check_name_chain = SequentialChain(
    chains=[chain_one],
    input_variables=["input"],
    output_variables=["whether_name"],
    verbose=True
    )
 
    with open(csv_output_file, 'w', encoding='utf-8') as csvfile:
        fieldnames = fieldnames = ['line_text_number','line_text_content','row_number', 'table_name','storage_path', 'match_keywords', 'preprocess_evidence_type',"check_whether_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        with open(csv_input_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for index,row in enumerate(csv_reader):
                
                # line = f"""{row["line_text_content"]}"""
                type = row["preprocess_evidence_type"]
                row_number= row["row_number"]
                if(type=="name"):
                    match_word=row["match_keywords"]
                    result=second_check_name_chain(match_word)
                    print(result)
                    writer.writerow({
                        'line_text_number': row["line_text_number"],
                        'line_text_content': row["line_text_content"],
                        'row_number': row_number,
                        'table_name': row["table_name"],
                        'storage_path': row["storage_path"],
                        'match_keywords': row["match_keywords"],
                        'preprocess_evidence_type': row["preprocess_evidence_type"],
                        'check_whether_name': result.get('whether_name',"None")
                    })
                else:
                    writer.writerow({
                        'line_text_number': row["line_text_number"],
                        'line_text_content': row["line_text_content"],
                        'row_number': row_number,
                        'table_name': row["table_name"],
                        'storage_path': row["storage_path"],
                        'match_keywords': row["match_keywords"],
                        'preprocess_evidence_type': row["preprocess_evidence_type"],
                        'check_whether_name': "None"
                    })

                
#Analyze after_second_check csv file, if the evidence is name and second check is "Yes", combine them into a new csv file
def combine_into_csv_file(csv_input_file, csv_output_file):  
    with open(csv_output_file, 'w', encoding='utf-8') as csvfile:
        fieldnames = fieldnames = ['line_text_number','line_text_content', 'row_number','table_name','storage_path', 'match_keywords', 'preprocess_evidence_type',"check_whether_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        with open(csv_input_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for index,row in enumerate(csv_reader):    
                # line = f"""{row["line_text_content"]}"""
                type = row["preprocess_evidence_type"]
                row_number= row["row_number"]
                check_name= row["check_whether_name"]
                if(type=="name"):
                    if(check_name=="Yes"):
                        writer.writerow({
                            'line_text_number': row["line_text_number"],
                            'line_text_content': row["line_text_content"],
                            'row_number': row_number,
                            'table_name': row["table_name"],
                            'storage_path': row["storage_path"],
                            'match_keywords': row["match_keywords"],
                            'preprocess_evidence_type': row["preprocess_evidence_type"],
                            'check_whether_name': check_name
                        }) 
                    else:
                        continue                                       
                else:
                    writer.writerow({
                        'line_text_number': row["line_text_number"],
                        'line_text_content': row["line_text_content"],
                        'row_number': row_number,
                        'table_name': row["table_name"],
                        'storage_path': row["storage_path"],
                        'match_keywords': row["match_keywords"],
                        'preprocess_evidence_type': row["preprocess_evidence_type"],
                        'check_whether_name': check_name
                    }) 




def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def split_string_based_on_token_number(model_name,token_number,string): #chunk size表示分出来的一块里面包含了多少个token
    text_splitter = TokenTextSplitter(model_name=model_name,chunk_size=token_number, chunk_overlap=0)
    texts = text_splitter.split_text(string)
    return texts


def evidence_array_summary(file_path):
    # Initialize lists to store the data
    evidence_types = set()
    evidence_dict = {}

    # Read the CSV file using csv package
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        #analyze the csv file line by line
        for row in reader:
            evidence_type = row['evidence_type']
            node_evidence = row['node_evidence']
            
            # Add evidence type to the set
            evidence_types.add(evidence_type)
            
            # Initialize the set for the evidence type if not already present
            if evidence_type not in evidence_dict:
                evidence_dict[evidence_type] = set()
            
            # Add node_evidence directly if it's not empty
            if node_evidence:
                evidence_dict[evidence_type].add(node_evidence)
    
    # Convert sets to lists to remove duplicates and make them JSON serializable
    evidence_dict = {etype: list(evidences) for etype, evidences in evidence_dict.items()}
    return  evidence_dict


def chatgpt_group_evidence(input_array):
  client = OpenAI()
  input_array=str(input_array)
  response = client.chat.completions.create(
    model="gpt-4-turbo",
    response_format={ "type": "json_object" },
    messages=[
      {"role": "system", "content": "You are a good text analyzer. Please output final answer in JSON format."},
      {"role": "user", "content": 
      """You are great at grouping evidence entities\
      Please analyze following text line by line and group similar name entities\
      Use the most representative word as the key for each group and each group of words as the value\
      Attention: 1. If two evidence entities are email, they may contain the same suffix,but different contents in front.. In this case, you need divide them into two different groups\
                 2. If two evidence entities are address, they may have the same city or region, but different specific streets. In this case, you need divide them into two different groups\
                 
      Before output, check it again\ 
            Example:
      Input: ["Josh Hickman","+19195790479","Josh","hickman","9195790479","josh hickman","joshuahickman1_ulc@talk.kik.com","quiztest_2iz@talk.kik.com"]
      Output: 
        {
        "Josh Hickman": [
          "Josh Hickman","Josh","hickman","josh hickman"
        ],
        "+19195790479": [
          "+19195790479","9195790479"
        ],
        "joshuahickman1_ulc@talk.kik.com": [
          "joshuahickman1_ulc@talk.kik.com"
        ],
        "quiztest_2iz@talk.kik.com":[
          "quiztest_2iz@talk.kik.com"
        ]

        }

      
      Here is the text line:""" + input_array
      }
    ]
  )  
  return(response)


# 从文本文件中读取group result:
def get_group_result_from_txt(txt_file_path):
    with open(txt_file_path, 'r') as file:
        group_result = file.read()

    group_result=json.loads(group_result)
    
    # 用于存储 key-value 映射
    key_value_map = {}
    # 遍历所有键值对
    for key, value in group_result.items():
        # print(f"Key: {key}")
        # if(key=="email"):
        #     continue
        control_chars = re.compile(r'[\x00-\x1f\x7f-\x9f]')
        value = control_chars.sub('', value)
        value= json.loads(value)
        # print(value)
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                # print(f"  Sub Key: {sub_key}")
                for item in sub_value:
                    key_value_map[item] = sub_key
                    # print(f"    Item: {item}")
        # else:
        #     # print(f"  Value: {value}")

    #打印 key-value 映射，每行一个键值对
    # for k, v in key_value_map.items():
    #     print(f'"{k}": "{v}"')
    
    return(key_value_map)



def transfer_result_to_file_for_analyze(input_file,output_file):
    # Read the CSV file
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)  # assuming tab-separated file
        # Prepare the fieldnames for output
        fieldnames = reader.fieldnames
        
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()  # Write header
            
            # Store node evidence as dictionary for quick lookup
            node_evidence_dict = {}
            
            # First pass through the file to build the node_evidence dictionary
            rows = list(reader)
            for row in rows:
                node_evidence_dict[row['node_evidence_number']] = row['node_evidence']
            
            # Second pass to process edge_relationship_sameline and write to output
            for row in rows:
                edge_relationship = row['edge_relationship_sameline']
                print(row)
                # Skip rows where edge_relationship_sameline is empty "[]"
                if edge_relationship == "[]":
                    continue
                   
                # Convert the string representation of the tuple to an actual Python tuple
                try:
                    edge_tuple = ast.literal_eval(edge_relationship)
                except (ValueError, SyntaxError):
                    # If the edge_relationship_sameline is malformed, skip this row
                    continue
                
                # Replace node_evidence_number in the tuple with corresponding node_evidence
                new_edge_tuple = []
                for pair in edge_tuple:
                    node1, node2 = pair
                    node1_evidence = node_evidence_dict.get(str(node1), None)
                    node2_evidence = node_evidence_dict.get(str(node2), None)
                    if node1_evidence and node2_evidence:
                        new_edge_tuple.append((node1_evidence, node2_evidence))
                
                # Update the row with the modified tuple as string
                row['edge_relationship_sameline'] = str(new_edge_tuple)
                
                # Write the updated row to the output file
                writer.writerow(row)