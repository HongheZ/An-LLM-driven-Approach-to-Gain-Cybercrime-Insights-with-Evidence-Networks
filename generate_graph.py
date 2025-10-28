import pandas as pd
import networkx as nx
import csv
import matplotlib.pyplot as plt
from pyvis.network import Network
import langchain_chatgpt
import re
from networkx.algorithms.clique import find_cliques
#Generate SameLine relationship graph

def create_graph_object_sameline(graph,dataframe):
    color_map = {
    "name": "skyblue",
    "address": "green",
    "phone number": "red",
    "email": "yellow",
    "user name": "black",
    "app name": "orange"
    }

    icon_map = {
    "name": "https://i.imgur.com/wo5vKco.png",
    "address": "https://i.imgur.com/el4Ef6u.png",    
    "phone number": "https://i.imgur.com/LNayAZi.png",
    "email": "https://i.imgur.com/B3nPm7v.png",
    "user name": "https://i.imgur.com/NZTWBco.png",
    "app name": "https://i.imgur.com/y03aAG4.png"
    }
    
    #current file's dataframe parameter
    df=dataframe
    df=df.dropna()
    #Get the current graph file
    G= graph
    
    #similar word mapping
    similar_evidence_mapping= langchain_chatgpt.get_group_result_from_txt("/home/hzhou/llama2/llama/experiment_result/result/Apps_in_the_document/group_result.txt")
    print(similar_evidence_mapping)
    ##based on db graph file create node and edge 
    
    evidence_path_record= "/home/hzhou/llama2/llama/experiment_result/result/Apps_in_the_document/evidence_path_record.csv"
    with open(evidence_path_record, mode='a', newline='') as file: #记录成为node的evidence的存储路径
        # 定义CSV文件的列名
        fieldnames = ['node_evidence_number','node_evidence', 'evidence_type', 'table_name', 'row_number','storage_path']        
        # 创建一个DictWriter对象
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # 检查文件是否为空，如果为空，则写入表头
        file_empty = file.tell() == 0
        if file_empty:
            writer.writeheader()      
    
    
        for index, row in df.iterrows():
            
            # 获取节点信息
            node_number= row['node_evidence_number']
            evidence_name = row['node_evidence'].strip()
            evidence_type = row['evidence_type']
            node_color = color_map[evidence_type]
            table_name = row['table_name']
            storage_path =  row['storage_path']
            row_number = row['row_number']
            
                        
            ##evidence validation check(这个先注释掉)
            # if evidence_validate(evidence_name,evidence_type) is False:
            #     continue
                    
            # 将evidence_type信息加入生成的node中
            node_attributes = {'evidence_number':node_number,'evidence_type': evidence_type, "color": node_color}
            # print(f"evidence number: {node_number}")
            # print(evidence_name)
            # try:
            #     evidence_name_lower = evidence_name.lower()  # 记录当前键值的小写  # 这个方法不存在，会引发 AttributeError
            # except AttributeError:
            #     print("AttributeError occurred, skipping this step.")
            #     continue
            
            # 检查节点是否已经存在   
            # node_exists = False
            # for node_name in name_mapping:
            #     if is_similar(evidence_name_lower, node_name):
            #         node_exists = True
            #         break

            # if evidence_name in name_mapping:
            if evidence_type=="user name" and len(evidence_name)>20:
                continue
            if evidence_type=="user name" and re.search(r"[:&=_'<>+\-,]", evidence_name):
                continue
            if evidence_type=="user name" and evidence_name == "DontLike":
                continue
            
            if evidence_type=="phone number":
                # Remove all non-numeric characters
                modified_evidence_name  = re.sub(r"[^\d]", "", evidence_name)
                # Remove leading '1' if it's a US country code
                if modified_evidence_name.startswith("1") and len(modified_evidence_name) > 10:
                    modified_evidence_name = modified_evidence_name[1:]
                similar_evidence_mapping[evidence_name] = modified_evidence_name    
            
            if evidence_type=="name" or evidence_type == "address" or evidence_type == "user name":
                modified_evidence_name = re.sub(r'[^\w]', '', evidence_name.lower()).strip()
                if evidence_name not in similar_evidence_mapping:
                    similar_evidence_mapping[evidence_name] = modified_evidence_name


            ##use group file to map and group evidence
            if evidence_name in similar_evidence_mapping:
                node_name= similar_evidence_mapping[evidence_name]
            else:    
                node_name = evidence_name
     
            if G.has_node(node_name):
                # 合并属性，将新属性添加到节点中
                
                ##
                #使用大小写来合并 
                # original_node_name = name_mapping[evidence_name_lower]  # 使用映射中的实际节点名称来合并属性

                # existing_attrs = G.nodes[original_node_name]   #existing_attrs存储这个已存在节点的attribute信息
                existing_attrs = G.nodes[node_name]   #existing_attrs存储这个已存在节点的attribute信息
                for key, value in node_attributes.items():
                    if key in existing_attrs:
                        # 如果属性已存在，将值合并为列表
                        if(key== "color" or "evidence_type"):     #确保属性中没有相同的值，主要是为了不重复添加颜色
                            continue
                        else:
                            if isinstance(existing_attrs[key], list):
                                existing_attrs[key].append(value)
                            else:
                                existing_attrs[key] = [existing_attrs[key], value]
                    else:
                        existing_attrs[key] = value
                # G.nodes[original_node_name].update(existing_attrs)
                G.nodes[node_name].update(existing_attrs)
            else:
                # 如果节点不存在，直接添加
                G.add_node(node_name, **node_attributes)

            #record the storge path of nodes
            writer.writerow({
                'node_evidence_number':node_number,
                'node_evidence': evidence_name,
                'evidence_type': evidence_type,
                'table_name': table_name,
                'row_number':row_number,
                'storage_path': storage_path
            })  
            
            # print(G.nodes())

    #analyze db edge
    for index, row in df.iterrows():
        evidence_name = row['node_evidence']
        evidence_type = row['evidence_type']
        # if evidence_validate(evidence_name,evidence_type) is False:
        #     continue
        # if evidence_name in name_mapping:
        
        ##use group file to group and map file
        if evidence_name in similar_evidence_mapping:
            node_name= similar_evidence_mapping[evidence_name]
        else:
            node_name = evidence_name
            
        
        ##sameline edge
        # 判断edge_relationship_sameline是否为空
        if not pd.isna(row['edge_relationship_sameline']):
            # 解析edge_relationship_sameline中的数组
            edges_sameline = eval(row['edge_relationship_sameline'])
           
            #添加same line边，并设置为最粗的实线
            for edge in edges_sameline:
                try:
                    actual_from_node_name = df[df['node_evidence_number'] == edge[0]]['node_evidence'].values  #原本的from_node的名字
                    actual_to_node_name = df[df['node_evidence_number'] == edge[1]]['node_evidence'].values #原本的to_node的名字
            
                    #使用大小写来整合edge两端的点
                    # from_node_name= name_mapping[actual_from_node_name[0].lower()]
                    # to_node_name= name_mapping[actual_to_node_name[0].lower()]

                    #使用chatgpt 的结果来group similar word
                    # print(edge) #这里得分开判断 
                    if actual_from_node_name[0] in similar_evidence_mapping:
                        from_node_name= similar_evidence_mapping[actual_from_node_name[0]]  #actual_from_node_name's type is array
                    else:
                        from_node_name = actual_from_node_name[0]

                    if actual_to_node_name[0] in similar_evidence_mapping:
                        to_node_name= similar_evidence_mapping[actual_to_node_name[0]] #actual_to_node_name's type is array
                    else:
                        to_node_name = actual_to_node_name[0]
            
                except (AttributeError, IndexError):
                    # print("AttributeError or IndexError occurred, skipping this step.")
                    continue               
                if not G.has_edge(from_node_name, to_node_name):  # Check if an edge exists between nodes
                    # print("edge information:")
                    # print(from_node_name)
                    # print(to_node_name)
                    if from_node_name!=to_node_name:
                        G.add_edge(from_node_name, to_node_name, style='solid', width=0.5, color='black')
                
    return G, similar_evidence_mapping

def graph_add_app_node(G, graph_file_path,similar_evidence_mapping):
    
    
    df = pd.read_csv(graph_file_path)
    # Columns for the initial graph creation 
    columns_to_use = ['username', 'address', 'name', 'phone_number', 'email']
    app_column = 'appname'   
    
    # Add appname as a node and connect it to existing nodes
    for _, row in df.iterrows():
        app_node = str(row[app_column]) if pd.notna(row[app_column]) else None
        if(app_node.startswith("None")):
           continue       
        if(app_node == "X"):
            app_node="twitter"
        app_node = normalize_name(app_node)

      # Normalize existing nodes from the columns, handling multiple evidence items per cell
        existing_nodes = []
        # Normalize existing nodes using the mapping
        for col in columns_to_use:
            if pd.notna(row[col]):
                # Split the cell content by newline and process each evidence
                evidences = row[col].split('\n')
                for evidence in evidences:
                    evidence = evidence.strip()  # Remove any extra whitespace
                    normalized_evidence = similar_evidence_mapping.get(evidence, evidence)
                    if G.has_node(normalized_evidence):
                        existing_nodes.append(normalized_evidence)            

        if app_node and existing_nodes:
            G.add_node(app_node, evidence_type="app name")
            G.add_edges_from([(app_node, node) for node in existing_nodes])
    
    return G

# Function to normalize node names
def normalize_name(name):
    return str(name).strip().lower() if pd.notna(name) else None





#Judge whether this evidence is a validate people's name, address, phone number or email
def evidence_validate(evidence,evidence_type):                
    if(evidence_type)=="name":
        name_posibility= is_possible_name(evidence)
        if name_posibility >= 0.7:
            return True
        else:
            return False
    if(evidence_type)=="address":
        if(is_possible_address(evidence)=="Yes"):
            return True
        else:
            return False    
    if(evidence_type)=="phone number":
        if(is_possible_phone_number(evidence)=="Yes"):
            return True
        else:
            return False        
    if(evidence_type)=="email":
        if(is_possible_email(evidence)=="Yes"):
            return True
        else:
            return False



# Patterns and heuristics to determine probability of being a name or username
def is_possible_name(item):
    # Heuristics for names
    if re.search(r"^[A-Z][a-z]+(?:\s[A-Z][a-z]+)*$", item):
        return 0.9
    if re.search(r"^[A-Z][a-z]+(?:\s[A-Za-z]+)*$", item):
        return 0.75
    if re.search(r"\b[A-Z][a-z]+\b", item) and not re.search(r"\d", item):
        return 0.7
    return 0.3

def is_possible_username(item):
    # Heuristics for usernames
    if re.search(r"^[a-zA-Z0-9_]+$", item):
        return 0.8
    if re.search(r"^[a-zA-Z]+[a-zA-Z0-9_]+$", item):
        return 0.7
    if re.search(r"[a-zA-Z]+", item) and re.search(r"[_\d]", item):
        return 0.6
    return 0.2

def name_posibility(items):
    # Analysis
    name_probabilities = []

    for item in items:
        name_probability = is_possible_name(item)
        username_probability = is_possible_username(item)

        # if name_probability > username_probability:
        #     probability = name_probability
        # else:
        #     probability = username_probability
        # if name_probability>0.75:
        name_probabilities.append({
            "name": item,
            "name_probability": name_probability,
            "username_probability": username_probability
        })

    return name_probability

def is_possible_address(item):
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
    # Heuristics for names
    pattern_address = re.compile(r'(?<!\w)(?:' + '|'.join((re.escape(kw)) for kw in keywords) + r')(?!\w)')
    if re.search(pattern_address, item):
        return "Yes"
    return "No"

def count_digits_in_string(item):
    return sum(c.isdigit() for c in item)

def is_possible_phone_number(item):
    us_area_codes = [
        "205", "251", "256", "334", "907", "480", "520", "602", "623", "928", "479",
        "501", "870", "209", "213", "310", "323", "408", "415", "424", "510", "530",
        "559", "562", "619", "626", "650", "661", "707", "714", "760", "805", "818",
        "831", "858", "909", "916", "925", "949", "951", "303", "719", "720", "970",
        "203", "860", "302", "202", "689", "239", "305", "321", "352", "386", "407",
        "561", "727", "754", "772", "786", "813", "850", "863", "904", "941", "954",
        "762", "229", "404", "478", "678", "706", "770", "912", "808", "208", "730",
        "779", "217", "224", "309", "312", "447", "618", "630", "708", "773", "815",
        "847", "219", "260", "317", "574", "765", "812", "319", "515", "563", "641",
        "712", "316", "620", "785", "913", "270", "502", "606", "859", "225", "318",
        "337", "504", "985", "207", "240", "301", "410", "443", "339", "351", "413",
        "508", "617", "774", "781", "857", "978", "231", "248", "269", "313", "517",
        "586", "616", "734", "810", "906", "947", "989", "218", "320", "507", "612",
        "651", "763", "952", "228", "601", "662", "769", "314", "417", "573", "636",
        "660", "816", "406", "308", "402", "702", "775", "603", "201", "551", "609",
        "732", "848", "856", "862", "908", "973", "505", "575", "212", "315", "347",
        "516", "518", "585", "607", "631", "646", "716", "718", "845", "914", "917",
        "252", "336", "704", "828", "910", "919", "980", "701", "216", "234", "330",
        "419", "440", "513", "567", "614", "740", "937", "405", "580", "918", "503",
        "541", "971", "215", "267", "412", "484", "570", "610", "717", "724", "814",
        "878", "401", "803", "843", "864", "605", "423", "615", "731", "865", "901",
        "931", "210", "214", "254", "281", "325", "361", "409", "430", "432", "469",
        "512", "682", "713", "806", "817", "830", "832", "903", "915", "936", "940",
        "956", "972", "979", "435", "801", "802", "276", "434", "540", "571", "703",
        "757", "804", "206", "253", "360", "425", "509", "681", "304", "262", "414",
        "608", "715", "920", "307"
    ]

    # Regular expression patterns for American phone numbers
    patterns = [
        r'^\(\d{3}\) \d{3}-\d{4}$',           # (123) 456-7890
        r'^\+\d{1}\d{10}$',                   # +11234567890
        r'^\d{10}$',                          # 1234567890
        r'^\+\d{1} \d{3}-\d{3}-\d{4}$',       # +1 123-456-7890
        r'^\d{3}-\d{3}-\d{4}$',               # 123-456-7890
        r'^\+\d{1} \(\d{3}\) \d{3}-\d{4}$'    # +1 (123) 456-7890
    ]

    # Extract phone numbers that match the patterns and have valid area codes

    for pattern in patterns:
        if re.match(pattern, item):
            # Extract the area code
            phone_number_length=count_digits_in_string(item)
            if(phone_number_length==10):
                area_code = re.findall(r'\d{3}', item)[0]
            elif(phone_number_length==11):
                area_code = re.findall(r'\d{3}', item)[1]
            else:
                break
            if area_code in us_area_codes:
                return "Yes"
                break    
    return "No"

def is_possible_email(item):
    pattern_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b') 

    # Extract phone numbers that match the patterns and have valid area codes
    if re.match(pattern_email, item):
        return "Yes"
    else:
        return "No"
            

# 定义完全图(subgraph中所有node两两相连)着色逻辑
def remove_complete_subgraphs(G):
    # # 检测图中的所有完全子图（最大cliques）
    # cliques = list(find_cliques(G))
    # print("检测到的完全子图:", cliques)

    # # 找到独立的完全子图（大于1个节点的clique）
    # cliques_to_remove = [clique for clique in cliques if len(clique) > 20]

    # # 删除这些完全子图中的所有节点
    # nodes_to_remove = {node for clique in cliques_to_remove for node in clique}
    # G.remove_nodes_from(nodes_to_remove)
# 筛选出独立的完全子图（独立：子图的节点和图中其他节点无连接）
    # 找到所有完全子图
    cliques = list(find_cliques(G))
    independent_cliques = []
    for clique in cliques:
        # 判断该子图是否与其他节点有连接
        is_independent = True
        for node in clique:
            neighbors = set(G.neighbors(node))
            other_nodes = set(G.nodes()) - set(clique)
            if neighbors & other_nodes:  # 如果有与子图外部的连接
                is_independent = False
                break
        if is_independent:
            independent_cliques.append(clique)
    
    # 打印独立的完全子图
    print("独立的完全子图:", independent_cliques)    
    # 删除这些独立的完全子图
    nodes_to_remove = {node for clique in independent_cliques for node in clique}
    G.remove_nodes_from(nodes_to_remove)