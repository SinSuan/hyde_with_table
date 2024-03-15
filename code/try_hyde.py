# -- coding:UTF-8 --

"""

confi.ini


"""

import os
import json
from datetime import datetime
# from pyserini.search.lucene import LuceneSearcher

import pytz
# import requests
from dotenv import load_dotenv
from module.about_model import init_model, call_model
from module.about_BM25 import init_BM25, call_BM25

# abuot data
# # 存放 raw json 的 "資料夾"
# DATAPATH_2_RAW_JSON = \
#     "/user_data/DG/hyde_with_table/BM25/Agri_inverted_agri_table_only_113-0309/index"


# # about prompt
# DATAPATH_2_PROMPT = "/user_data/DG/hyde_with_table/prompt/prompt.json"

# # DATAPATH_2_PSEUDO_QUERY = "/user_data/DG/hyde_with_table/prompt/psuedo_query.json"
# DATAPATH_2_PSEUDO_QUERY = "/user_data/DG/hyde_with_table/prompt/sheila.json"


# about model
BOT = "breeze"
# BOT = "taide"
# BOT = "chatGPT"


# about time

# 取得當下的 UTC 時間
# UTC_NOW = datetime.utcnow()
UTC_NOW = datetime.now()

# 設定 UTC+8 的時區
UTC_8 = pytz.timezone('Asia/Taipei')

# 將 UTC 時間轉換為 UTC+8 時區的時間
NOW = UTC_NOW.replace(tzinfo=pytz.utc).astimezone(UTC_8)


def create_full_prompt(user_prompt) -> str:
    """
    123
    """
    print("enter create_full_prompt")

    # 讀取 prompt 的 components
    datapath = os.getenv("DATAPATH_2_PROMPT")
    with open(datapath, 'r', encoding='utf-8') as file:
        print("\tstart dealing file")
        total_prompt = json.load(file)["hyde_query"]
        system_prompt = total_prompt[BOT]
        print("\tend dealing file")

    full_prompt = f"<s> {system_prompt} [INST] 依照你的知識回答：{user_prompt} [/INST]"

    print("exit create_full_prompt")
    return full_prompt


def save_logging(file_dir, total_logging):
    """123
    """

    now_time = NOW.strftime("%Y_%m%d_%H%M")
    file_name = f"{BOT}_{now_time}.json"
    file_dir = "/user_data/DG/hyde_with_table/logging/hyde_the_query"

    file_path = f"{file_dir}/{file_name}"
    with open(file_path, 'w', encoding='utf-8') as file:
        print("\t\tstart save total_logging")
        json.dump(total_logging, file, ensure_ascii=False)
        print("\t\tend save total_logging")

    return file_path


def new_logging(total_query):
    """123
    """
    print("enter new_logging")
    total_query_docids, total_query_docs = call_BM25(total_query)

    total_logging = []
    for query, query_docids, query_docs in \
        zip(total_query, total_query_docids, total_query_docs):

        logging = {
            'query': query,
            'docid': query_docids,
            'doc': query_docs
        }
        total_logging.append(logging)

    print("exist new_logging")
    return total_logging


def exam_hyde_query(model_and_tokenizer):
    """123
    """
    print("enter exam_hyde_query")

    datapath = os.getenv("DATAPATH_2_PSEUDO_QUERY")
    with open(datapath, 'r', encoding='utf-8') as file:
        print("\t\tstart dealing PSEUDO_QUERY")
        total_query = json.load(file)
        print("\t\tend dealing PSEUDO_QUERY")

    print(f"before total_query = {total_query}")
    total_query = [query['query'] for query in total_query]
    print(f"after total_query = {total_query}")
    total_hyde_query = []
    for query in total_query:
        print(f"before query = {query}")
        full_prompt = create_full_prompt(query)
        print(f"after query = {query}")
        hyde_query = call_model(BOT, full_prompt, model_and_tokenizer)
        print(f"after hyde_query = {hyde_query}")
        total_hyde_query.append(hyde_query)
    
    print(f"after total_hyde_query = {total_hyde_query}")

    original_query_logging = new_logging(total_query)
    hyde_query_logging = new_logging(total_hyde_query)

    total_logging = []
    for original, hyde in zip(original_query_logging, hyde_query_logging):

        logging = {
            'original' : original,
            'hyde' : hyde
        }
        total_logging.append(logging)


    file_dir = "/user_data/DG/hyde_with_table/logging/hyde_the_query"
    save_logging(file_dir, total_logging)

    print("exit exam_hyde_query")
    return total_logging


def main() -> None:
    """123
    """
    print("enter main")

    model_and_tokenizer = init_model(BOT)

    exam_hyde_query(model_and_tokenizer)

    print("exit main")



if __name__ == "__main__":
    load_dotenv("/user_data/DG/hyde_with_table/global_variable/.env")
    main()
