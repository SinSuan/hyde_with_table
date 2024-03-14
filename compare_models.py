"""
123
"""

import json

import pytz
from datetime import datetime

DATAPATH_2DATAPATH = "/user_data/DG/hyde_with_table/datapath.json"

# about time

# 取得當下的 UTC 時間
UTC_NOW = datetime.utcnow()

# 設定 UTC+8 的時區
UTC_8 = pytz.timezone('Asia/Taipei')

# 將 UTC 時間轉換為 UTC+8 時區的時間
NOW = UTC_NOW.replace(tzinfo=pytz.utc).astimezone(UTC_8)

# def init_result()

def compare(model_1, model_2, total_path):
    """
    123
    """
    
    path_1 = total_path[model_1]
    path_2 = total_path[model_2]
    
    with open(path_1, 'r', encoding='utf-8') as file:
        total_result_1 = json.load(file)
        
    with open(path_2, 'r', encoding='utf-8') as file:
        total_result_2 = json.load(file)
    
    total_compare_hyde_docid = []
    for idx, _ in enumerate(total_result_1):
        compare_hyde_docid = {}
        
        docid_1 = total_result_1[idx]["hyde"]["docid"]
        docid_1 = set(docid_1)
        docid_2 = total_result_2[idx]["hyde"]["docid"]
        docid_2 = set(docid_2)
        
        
        only_docid_1 = docid_1 - docid_2
        only_docid_2 = docid_2 - docid_1
        docid_inter = docid_2 & docid_1
        docid_union = docid_1 | docid_2
        
        
        # print(total_result_1[idx])
        compare_hyde_docid['query_idx'] = idx
        IoU = float(len(docid_inter))/float(len(docid_union))
        compare_hyde_docid['IoU'] = IoU
        compare_hyde_docid[f'{model_1}_only'] = list(only_docid_1)
        compare_hyde_docid[f'{model_2}_only'] = list(only_docid_2)
        compare_hyde_docid['intersection'] = list(docid_inter)
        
        total_compare_hyde_docid.append(compare_hyde_docid)
        
        return total_compare_hyde_docid
        
    

def main():
    
    # init total_compare_result[]
    with open(DATAPATH_2DATAPATH, 'r', encoding='utf-8') as file:
        total_compare_result = json.load(file)

    total_compare_result.append({})
    total_model = list(total_compare_result[0].keys())
    for idx, model_1 in enumerate(total_model[:-1]):
        for model_2 in total_model[idx+1:]:
            compare_result = compare(model_1, model_2, total_compare_result[0])
            total_compare_result[-1][f'{model_1}_{model_2}'] = compare_result
    
    file_dir = "/user_data/DG/hyde_with_table/logging"
    now_time = NOW.strftime("%Y_%m%d_%H%M")
    file_name = f"compare_{now_time}.json"

    file_path = f"{file_dir}/{file_name}"
    with open(file_path, 'w', encoding='utf-8') as file:
        print("\tstart dealing file")
        json.dump(total_compare_result, file, ensure_ascii=False)
        print("\tend dealing file")
    
    
if __name__ == "__main__":
    main()