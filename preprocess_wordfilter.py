#输入一个文件夹，列出文件夹所有文件，若是csv文件，进行逐行分析，用regular expression判断后，将取出的行整合为一个新的csv文件
import re
import os
import csv
# csv.field_size_limit(500 * 1024 * 1024)


def csv_extract_lines_with_keywords(input_folder, csv_output_file):   ##Use regular expression to filter text file
    keywords = [
    #Common words in addresses
    "Street", "Avenue", "Road", "Lane", "Boulevard", "Drive", "Court", "Place", "Circle", "Terrace",
    "Way", "Crescent", "Alley", "Highway", "Manor", "Square", "Close", "Loop", "Cove", "Gate",
    "Gardens", "Ridge", "Park", "Heights", "Trace", "Trail", "Path", "Pathway", "Crossroad", "Plaza", "Post Office Box"
    "Station", "House", "Apartment", "Unit", "Suite", "Building", "Condo", "Front", "Back", 
    "North", "South", "East", "West", "Northeast", "Northwest", "Southeast", "Southwest",
    #Common words in addresses(abbreviation)
    "St.", "Ave.", "Blvd.", "Rd.", "Dr.", "Ln.", "Ct.", "Pl.", "Sq.", "Hwy.",
    "PO Box", "Apt.", "Ste.", "No.", "N.", "S.", "E.", "W.", "NE", "NW", "SE", "SW",
    #State names
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida',
    'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
    'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska',
    'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
    'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming',
    #State names(abbreviation)
    # "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", 
    # "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", 
    # "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ] 
    
    
    
    # Construct a regular expression pattern to ensure that there are only spaces or symbols before and after keywords
    # pattern = re.compile(r'(?:^|\s|[^\w])' + '|'.join((re.escape(kw)).lower() for kw in keywords) + r'(?:$|\s|[^\w])')
    # pattern_address = re.compile(r'(?<!\w)(?:' + '|'.join((re.escape(kw)).lower() for kw in keywords) + r')(?!\w)')
    pattern_address = re.compile(r'(?<!\w)(?:' + '|'.join((re.escape(kw)) for kw in keywords) + r')(?!\w)')
    pattern_name = re.compile(r"[A-Z][a-z]+,?\s+(?:[A-Z][a-z]*\.?\s*)?[A-Z][a-z]+")
    pattern_us_phone = re.compile(r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    pattern_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b') 
    with open(csv_output_file, 'w', encoding='utf-8') as csvfile:
        fieldnames = ['line_text_number','line_text_content', 'row_number','table_name','storage_path', 'match_keywords', 'preprocess_evidence_type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        line_number=0
        max_length = 20000
        for root, dirs, files in os.walk(input_folder):
            for filename in files:
                if filename.endswith(".csv"):
                    print(filename)
                    with open(os.path.join(root, filename), 'r', newline='', encoding='utf-8') as file:
                        path=os.path.join(root, filename)
                        print("path:"+path)
                        # database_name = os.path.basename(os.path.dirname(path))
                        csv_reader = csv.reader(line.replace('\0', '') for line in file)
                        for index, row in enumerate(csv_reader):
                            line = ','.join(row)
                            # # 检查 line 长度，如果超过 30000 字符，进行分割
                            # if len(line) > max_length:
                            #     substrings = [line[i:i + max_length] for i in range(0, len(line), max_length)]
                            # else:
                            #     substrings = [line]
                            #Check if the US phone number is in the row
                            # for substring in substrings:
                            if re.search(pattern_us_phone, line):
                                print(line)
                                # keywords_found = [kw for kw in keywords if re.search(re.escape(kw), line)]
                                keywords_found = re.search(pattern_us_phone, line)
                                # keywords_found = keywords_found.group()
                                print("keyword: "+keywords_found.group())
                                # Get the index of the end of the matched substring
                                end_index = keywords_found.end()
                                # Retrieve the next character
                                if(starts_with_area_code(keywords_found.group()))== False:
                                    continue

                                # #如果电话号码的下一个字符还是数字，该substring很可能不是电话号码，则跳过
                                # next_character = line[end_index:end_index + 1]
                                # if next_character.isdigit():
                                #     continue
                                                                
                                writer.writerow({
                                    'line_text_number': line_number,
                                    'line_text_content': line,
                                    'row_number': index+1,
                                    'table_name': filename,
                                    'storage_path': path,
                                    # 'match_keywords': ', '.join(keywords_found),
                                    'match_keywords': keywords_found.group(),
                                    'preprocess_evidence_type': "phone_number"
                                })
                                line_number=line_number+1
                            #Check if the email address is in the row
                            elif re.search(pattern_email, line):
                                print(line)
                                # keywords_found = [kw for kw in keywords if re.search(re.escape(kw), line)]
                                keywords_found = re.search(pattern_email, line).group()
                                print("keyword: "+keywords_found)
                                writer.writerow({
                                    'line_text_number': line_number,
                                    'line_text_content': line,
                                    'row_number': index+1,
                                    'table_name': filename,
                                    'storage_path': path,
                                    # 'match_keywords': ', '.join(keywords_found),
                                    'match_keywords': keywords_found,
                                    'preprocess_evidence_type': "email"
                                })
                                line_number=line_number+1
                            #Check if the address is in the row
                            elif re.search(pattern_address, line):
                                print(line)
                                # keywords_found = [kw for kw in keywords if re.search(re.escape(kw), line)]
                                keywords_found = re.search(pattern_address, line).group()
                                print("keyword: "+keywords_found)
                                # if check_strings_contain_more_than_two_uppercase(keywords_found):   #防止一个取到的词中有两个upper case，这种情况一般不会是地名
                                #     continue                                

                                writer.writerow({
                                    'line_text_number': line_number,
                                    'line_text_content': line,
                                    'row_number': index+1,
                                    'table_name': filename,
                                    'storage_path': path,
                                    
                                    'match_keywords': keywords_found,
                                    'preprocess_evidence_type': "address"
                                })
                                line_number=line_number+1
                            #Check if the person's name is in the row, name check should be put at last, because we will second check it
                            elif re.search(pattern_name, line):
                                print(line)
                                # keywords_found = [kw for kw in keywords if re.search(re.escape(kw), line)]
                                keywords_found = re.search(pattern_name, line).group()
                                print("keyword: "+keywords_found)
                                writer.writerow({
                                    'line_text_number': line_number,
                                    'line_text_content': line,
                                    'row_number': index+1,
                                    'table_name': filename,
                                    'storage_path': path,
                                    # 'match_keywords': ', '.join(keywords_found),
                                    'match_keywords': keywords_found,
                                    'preprocess_evidence_type': "name"
                                })
                                line_number=line_number+1




file_path = "/home/hzhou/llama2/llama/Line_test_data.txt"

input_folder = "/home/hzhou/llama2/llama/Database_to_CSV"
output_path="/home/hzhou/llama2/llama/after_filter/after_filter2.csv"
# csv_extract_lines_with_keywords(input_folder,output_path) 


#check whether uppercase
def check_uppercase(word):
    count_uppercase = 0
    for char in word:
        if char.isupper():
            count_uppercase += 1
            if count_uppercase > 2:
                return True
    return False


# 遍历每个单词并检查大写字母数
def check_strings_contain_more_than_two_uppercase(string):
    if len(string.split()) == 1:  #check whether only one word
        if check_uppercase(string):
            return True 
    
    else:
        for input_string in string:
            # 将字符串按单词分开
            words = input_string.split()

            # 遍历每个单词并检查大写字母数
            for word in words:
                if check_uppercase(word):
                    print(f'This word "{word}" contains more than two uppercase letters.')
                    return True
                # else:
                    # print(f'This word "{word}" does not contain more than two uppercase letters.')
        
    return False


#test
def starts_with_area_code(phone_number: str) -> bool:    
    # List of all area codes
    area_codes = [
    "205", "251", "256", "334", "938", "907", "480", "520", "602", "623", "928", "479", "501", "870", 
    "209", "213", "279", "310", "323", "341", "408", "415", "424", "442", "510", "530", "559", "562", 
    "619", "626", "628", "650", "657", "661", "669", "707", "714", "747", "752", "760", "805", "818", 
    "820", "831", "858", "909", "916", "925", "949", "951", "303", "719", "720", "970", "203", "475", 
    "860", "959", "302", "202", "239", "305", "321", "352", "386", "407", "561", "689", "727", "754", 
    "772", "786", "813", "850", "863", "904", "941", "954", "229", "404", "470", "478", "678", "706", 
    "762", "770", "912", "808", "208", "986", "217", "224", "309", "312", "331", "618", "630", "708", 
    "773", "779", "815", "847", "872", "219", "260", "317", "463", "574", "765", "812", "930", "319", 
    "515", "563", "641", "712", "316", "620", "785", "913", "270", "364", "502", "606", "859", "225", 
    "318", "337", "504", "985", "207", "240", "301", "410", "443", "667", "339", "351", "413", "508", 
    "617", "774", "781", "857", "978", "231", "248", "269", "313", "517", "586", "616", "734", "810", 
    "906", "947", "989", "218", "320", "507", "612", "651", "763", "952", "228", "601", "662", "769", 
    "314", "417", "557", "573", "636", "660", "816", "406", "308", "402", "531", "702", "725", "775", 
    "603", "201", "551", "609", "640", "732", "848", "856", "862", "908", "973", "505", "575", "212", 
    "315", "332", "347", "516", "518", "585", "607", "631", "646", "716", "718", "838", "845", "914", 
    "917", "929", "934", "252", "336", "704", "743", "828", "910", "919", "980", "701", "216", "220", 
    "234", "283", "326", "330", "380", "419", "440", "513", "567", "614", "740", "937", "405", "539", 
    "572", "580", "918", "458", "503", "541", "971", "215", "223", "267", "272", "412", "445", "484", 
    "570", "582", "610", "717", "724", "814", "835", "878", "401", "803", "839", "843", "854", "864", 
    "605", "423", "615", "629", "731", "865", "901", "931", "210", "214", "254", "281", "325", "346", 
    "361", "409", "430", "432", "469", "512", "682", "713", "726", "737", "806", "817", "830", "832", 
    "903", "915", "936", "940", "945", "956", "972", "979", "385", "435", "801", "802", "276", "434", 
    "540", "571", "703", "757", "804", "206", "253", "360", "425", "509", "564", "304", "681", "262", 
    "274", "414", "534", "608", "715", "920", "307"
]
    # Convert list to set for fast lookup
    area_codes_set = set(area_codes)
    
    
    # List of prefixes to remove
    prefixes = ["+1", "+1 ", "+1(", "+1 ("]
    
    # Check if phone_number starts with any of the prefixes and remove them
    for prefix in prefixes:
        if phone_number.startswith(prefix):
            phone_number = phone_number[len(prefix):]
            break
    
    # Remove any remaining formatting characters
    cleaned_number = phone_number.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
    
    # Extract the first 3 digits from the cleaned phone number
    area_code = cleaned_number[:3]
    
    # Check if the area code is in the set of valid area codes
    return area_code in area_codes_set

# Test the function
test_number_1 = "+1 919-512-1037"  # Should return True (Alabama area code)
test_number_2 = "+1 (205) 123-4567"  # Should return True (Alabama area code)
test_number_3 = "+1 (919) 579-4674"  # Should return False (Invalid area code)

print(starts_with_area_code(test_number_1))  # Output: True
print(starts_with_area_code(test_number_2))  # Output: True
print(starts_with_area_code(test_number_3))  # Output: False





##xml file wordfilter





  

 
                
