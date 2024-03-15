"""
123
"""

import os
import json
from pyserini.search.lucene import LuceneSearcher


# about datapath
PATH_2_RESULT = "/user_data/DG/hyde_with_table/logging/taide_2024_0312_1103.json"
PATH_2_ORGANIZED_RESULT = f"{PATH_2_RESULT[:-5]}_organized.json"


# about BM25
# 指定索引目錄的路徑
DATAPATH_2_INVERTED_INDEX_TABLE = '/user_data/DG/hyde_with_table/BM25/Agri_inverted_agri_table_only'

# 創建一個 SimpleSearcher 物件
SEARCHER = LuceneSearcher(DATAPATH_2_INVERTED_INDEX_TABLE)


def organize_result():
    """
    123
    """
    with open(PATH_2_RESULT, 'r', encoding='utf-8') as file:
        total_result = json.load(file)

    total_result_about_docid = []
    for idx, reslut in enumerate(total_result):

        query = reslut['original']['query']
        hyde_query = reslut['hyde']['query']
        print()
        print("*"*100)
        print()
        print(f"query =\t\t{query}")
        print(f"hyde_query =\t\t{hyde_query}")

        docid = set(reslut['original']['docid'])
        hyde_docid = set(reslut['hyde']['docid'])

        docid_orig = docid - hyde_docid
        docid_hyde = hyde_docid - docid
        docid_inter = hyde_docid & docid

        total_result_about_docid.append({})
        total_result_about_docid[-1]['idx'] = idx

        total_result_about_docid[-1]['original'] = {}
        total_result_about_docid[-1]['original']['query'] = query
        total_result_about_docid[-1]['original']['docid'] = list(docid_orig)

        total_result_about_docid[-1]['hyde'] = {}
        total_result_about_docid[-1]['hyde']['query'] = hyde_query
        total_result_about_docid[-1]['hyde']['docid'] = list(docid_hyde)

        total_result_about_docid[-1]['intersection'] = {}
        total_result_about_docid[-1]['intersection']['docid'] = list(docid_inter)

    print(total_result_about_docid)
    with open(PATH_2_ORGANIZED_RESULT, 'w', encoding='utf-8') as file:
        json.dump(total_result_about_docid, file, ensure_ascii=False)


def see_certain_result_doc(result_idx, docid_type):
    """
    docid_type: "original" or "hyde" or "intersection"
    """
    with open(PATH_2_ORGANIZED_RESULT, 'r', encoding='utf-8') as file:
        total_organized_result = json.load(file)

    query = {}
    if docid_type in ["intersection", "original"]:
        query["original"] = total_organized_result[result_idx]["original"]['query']
    if docid_type in ["intersection", "hyde"]:
        query["hyde"] = total_organized_result[result_idx]["hyde"]['query']

    for docid in total_organized_result[result_idx][docid_type]['docid']:
        doc = SEARCHER.doc(docid).raw()
        doc = json.loads(doc)["contents"]

        print("*"*100)
        print(f"\n\tdocid = {docid}\n")
        print("*"*100)
        for key, value in query.items():
            print(f"query[{key}] = {value}")
        print("*"*100)
        print()
        print(doc)
        print("*"*100)


def main():
    """123
    """
    if not os.path.exists(PATH_2_ORGANIZED_RESULT):
        organize_result()

    result_idx = 0

    # docid_type = "original"
    # docid_type = "hyde"
    docid_type = "intersection"

    see_certain_result_doc(result_idx, docid_type)

if __name__ == "__main__":
    main()
