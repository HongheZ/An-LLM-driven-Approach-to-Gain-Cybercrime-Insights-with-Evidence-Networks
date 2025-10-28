# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

#My code(test)
from typing import Optional

import fire
# import my_argumentparser
import traverse_directory
import time

from llama import Llama

import Preprocess_DataBaseFile
import json
import re
def main(
    ckpt_dir: str= "llama-2-13b-chat/" ,
    tokenizer_path: str= "tokenizer.model",
    temperature: float = 0.1,
    top_p: float = 0.9,
    max_seq_len: int = 8192,
    max_batch_size: int = 1,
    # max_gen_len: Optional[int] = None,
    max_gen_len: int = 4096,
    
    
):
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
        
    )
    #################
    ##################
    # # Get the command-line arguments and store in the "args" variable
    # args = my_argumentparser.parse_arguments()

    # # Get the directory from user input
    # input_directory = args.input_path
    # input_directory = "./Test_Data/Database_Files/com.enflick.android.TextNow"
    input_directory = "./Test_Data"
    
    
    #Get the data of all db file
    db_data= traverse_directory.traverse_directory(input_directory)


    for db_file in db_data:
        # for key, value in db_file.items():
        #     print(f"Key: {key}, Value: {value}")    ##The db_file value is a dictionary
#######################
#######################
        print(db_file["file_path"])
        database_data= Preprocess_DataBaseFile.database_To_Txt(db_file["file_path"])
        # print("This db files' data: ")
        # print(database_data)
       
        ##Define a regular expression pattern to match JSON objects
        pattern = r'\{(?:[^{}]|(?R))*\}'   
        
        ##Data Base file analyse 
        for i, line in enumerate(database_data[0:10]):
            input_string = str(line)
            # result_string = "\n".join(map(str, database_data))
            # print(len(result_string))
            print("This is "+str(i)+" line of the text of this database")
            print("The input text is: "+input_string)


            dialogs = [                      
                [
                    {
                        "role": "system",
                        "content": """\
                                You are a good text analyzer. Please analyze every input line of text step by step. Please enter a complete answer. At the end of your answer, output: <END>""",
                    },
                    
                    
                    {"role": "user", "content": 
                    """\ 
                    You will get a line of text. Your task is analyzing this text and identify whether there is a country name included in this line. 
                    Using the following steps to analyze this line of text:
                    Step1: Separate the text into different tokens. In this step, you are a Tokenizer and process the text into different tokens.
                    Step2: Analyze one by one whether the token you get is the name of a certain country. If so, record this country name.  Need to analyze all tokens, since there may be several city name in the line.
                    Step3: Output a JSON object containing the following keys: text_content, country_name. The value of text_content is the line of the text I provide to you. The value of country_name includes all the country name you exact from this line of text. If you did not extract any country name in this line, the value is “None”

                    Here are two examples: 
                    Example1: 
                    If the input line text is "(16, ,Austria, 30102722651, '+19842032223', 2, '+1(984) 203-2223', 1, 1, 'Hi there!', 1, 1581192046000, 0, '', 0, 0, China)",
                    Analyze:
                    Step1: This line of text includes 31 tokens: 
                    1.	"("
                    2.	"16"
                    3.	","
                    4.	"Austria"
                    5.	","
                    6.	"30102722651"
                    7.	","
                    8.	"'+19842032223'"
                    9.	","
                    10.	"2"
                    11.	","
                    12.	"'+1(984) 203-2223'"
                    13.	","
                    14.	"1"
                    15.	","
                    16.	"1"
                    17.	","
                    18.	"'Hi there!'"
                    19.	","
                    20.	"1"
                    21.	","
                    22.	"1581192046000"
                    23.	","
                    24.	"0"
                    25.	","
                    26.	"''"
                    27.	","
                    28.	"0"
                    29.	","
                    30.	"0"
                    31.	")"
                    32. "China"

                    Step2: Analyze all the tokens got in the last step. We can find two country name: “Austria” and "China".

                    Step3: Output a Json object: {"text_content": "(16, ,Austria, 30102722651, '+19842032223', 2, '+1(984) 203-2223', 1, 1, 'Hi there!', 1, 1581192046000, 0, '', 0, 0)", " country name ": ["Austria","China"]}

                    Example2:
                    If the input line text is "(19, 30102756233, '+19842032223', 2, '+1(984) 203-2223', 1, 1, 'Yep!  Have to keep generating data.', USA, 1581192186000, 0, '', 0, 0)",
                    Analyze:
                    Step1: This line of text includes 30 tokens: 
                    1.	"("
                    2.	"19"
                    3.	","
                    4.	"30102756233"
                    5.	","
                    6.	"'+19842032223'"
                    7.	","
                    8.	"2"
                    9.	","
                    10.	"'+1(984) 203-2223'"
                    11.	","
                    12.	"1"
                    13.	","
                    14.	"1"
                    15.	","
                    16.	"'Yep! Have to keep generating data.'"
                    17.	","
                    18.	"USA"
                    19.	","
                    20.	"1581192186000"
                    21.	","
                    22.	"0"
                    23.	","
                    24.	"''"
                    25.	","
                    26.	"0"
                    27.	","
                    28.	"0"
                    29.	","
                    30.	")"

                    Step2: Analyze all the tokens got in the last step. We can find one country name: “USA”.

                    Step3: Output a Json object: {"text_content": "(19, 30102756233, '+19842032223', 2, '+1(984) 203-2223', 1, 1, 'Yep!  Have to keep generating data.', USA&Canada, 1581192186000, 0, '', 0, 0)", " country name ": “USA”}

                    Now, please analyze this input line text:"""+input_string,},
                

            ],

                
            ]
            results = generator.chat_completion(
                dialogs,  # type: ignore
                max_gen_len=max_gen_len,
                temperature=temperature,
                top_p=top_p,
            )
            
           
            for dialog, result in zip(dialogs, results):
                
                print(f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}")
                json_objects = re.findall(pattern, result['generation']['content'])
                
                print("The detection result of this text is:")
                
                print(json_objects)
                
                print("\n==================================\n")
                
            


if __name__ == "__main__":
    main()
