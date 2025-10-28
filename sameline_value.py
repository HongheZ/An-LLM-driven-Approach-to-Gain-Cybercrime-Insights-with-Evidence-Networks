
def edge_sameline_combine(current_evidence_item,combined_evidence_dictlist):
    #改到这里，先要在之前的csv文件中给line_text添加上序号。先拼接多个列表，然后里面的所有evidence分别分配一个序号，之后和line——text的序号组合，比如1.1, 1.2

    sameline_values=[]  # 用于存储同一行的数据
       
    for other_evidence_item in combined_evidence_dictlist:  ##遍历其它的name evidence，并配对成edge
        if(other_evidence_item["evidence_content"]=="None" or other_evidence_item["evidence_content"]==current_evidence_item["evidence_content"]):
            continue
        sameline_values.append((current_evidence_item["evidence_number"], other_evidence_item["evidence_number"]))                       
    return sameline_values


def create_this_row_evidence_list(evidence_array,number,current_line_number,evidence_type):
    evidence_list=[]
    previous_evidence="None"
    for evidence in evidence_array:
        if(evidence.startswith("None")):
            continue                
        #If a piece of evidence is recorded multiple times in a row, skip it
        if(evidence==previous_evidence):
            continue
        previous_evidence=evidence
        
        dict={}
        dict["evidence_content"] = evidence
        dict["evidence_number"] = str(current_line_number)+"." + str(number)
        dict["evidence_type"]=evidence_type
        number = number+1
        evidence_list.append(dict)
    return evidence_list,number
