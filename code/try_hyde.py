# -- coding:UTF-8 --

"""

confi.ini


"""

import os
import json
from datetime import datetime

import pytz
from dotenv import load_dotenv
from module.about_model import init_model, call_model
from module.about_BM25 import call_BM25


# about model
BOT = "breeze"
# BOT = "taide"
# BOT = "chatGPT"


# about time

# 取得當下的 UTC 時間
# UTC_NOW = datetime.utcnow() # 舊的
UTC_NOW = datetime.now()

# 設定 UTC+8 的時區
UTC_8 = pytz.timezone('Asia/Taipei')

# 將 UTC 時間轉換為 UTC+8 時區的時間
NOW = UTC_NOW.replace(tzinfo=pytz.utc).astimezone(UTC_8)


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

    full_prompt = f"<s> {system_prompt} [INST] 你現在是一位農業病蟲害防治專家，幫我解釋以下表格：{user_prompt} [/INST] "

    print("exit create_full_prompt")
    return full_prompt


def exam_hyde_query(model_and_tokenizer):
    """123
    """
    print("enter exam_hyde_query")

    datapath = os.getenv("DATAPATH_2_PSEUDO_QUERY")
    with open(datapath, 'r', encoding='utf-8') as file:
        total_query = json.load(file)

    total_query = [query['query'] for query in total_query]
    total_hyde_query = []
    for query in total_query:
        full_prompt = create_full_prompt(query)
        hyde_query = call_model(BOT, full_prompt, model_and_tokenizer)
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


def hyde_table():
    """123
    """
    datapath = os.getenv("DATAPATH_2_PSEUDO_QUERY")
    with open(datapath, 'r', encoding='utf-8') as file:
        total_ndr_table = json.load(file)
    pass


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
