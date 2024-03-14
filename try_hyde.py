# -- coding:UTF-8 --

"""

confi.ini


"""

import os
import json
from datetime import datetime
import openai
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig,
)
from pyserini.search.lucene import LuceneSearcher

import pytz
import requests
from dotenv import load_dotenv

# ablot data
DATAPATH_2_DOCUMENT = "/user_data/DG/clean_data/data/agriculture.json"
# DATAPATH_2_PSEUDO_QUERY = "/user_data/DG/hyde_with_table/logging/hyde_the_query/psuedo_query.json"
DATAPATH_2_PSEUDO_QUERY = "/user_data/DG/hyde_with_table/logging/hyde_the_query/sheila.json"


# about model
DEVICE_MAP = "auto"
DATAPATH_2_PROMPT = "/user_data/DG/hyde_with_table/prompt.json"
DATAPATH_2_TABLE = "/user_data/DG/clean_data/data/agriculture.json"

BOT = "breeze"
# BOT = "taide"
# BOT = "chatGPT"

if BOT=="taide":
    API_USE = True
    load_dotenv(".env")

    # PATH_2_MODEL = "/user_data/DG/clean_data/model/b.1.0.0"
    TOKEN = os.getenv("TAIDE_api_key")
    # print(f"TOKEN = {TOKEN}")
    HEADERS = {
        "Authorization": "Bearer " + TOKEN
    }
    HOST = "https://td.nchc.org.tw/api/v1"
    # 原本的
    DATA = {
        "model": "TAIDE/b.11.0.0",
        # "prompt": prompt, # assigned in the funciton api_TAIDE()
        "temperature": 0,
        "top_p": 0.9,
        "presence_penalty": 1,
        "frequency_penalty": 1,
        "max_tokens": 3000,
        "repetition_penalty":1.2
    }

if BOT=="chatGPT":

    API_USE = True
    load_dotenv(".env")

    openai.api_key = os.getenv("openai_api_key")

elif BOT=="breeze":

    API_USE = False
    PATH_2_MODEL = "/user_data/DG/clean_data/model/MediaTek-Research/Breeze-7B-Instruct-v1_0"
    print("\tbefore GenerationConfig")
    GENERATION_CONFIG = GenerationConfig(
        # max_new_tokens=10,
        # do_sample=True,
        # temperature=1,
        num_beams = 6,
        num_return_sequences=1, # < num_beams

        # no_repeat_ngram_size=2,
        early_stopping=False,
        max_length=4096, #CUDA oom 輸出有關
        # top_p=0.92,   # 前 p 可能，共多少個不知道
        # top_k=15,     # 前 k 個，共佔多少機率不知道
    )
    print("\tbefore GenerationConfig")


# about BM25
DATAPATH_2_INVERTED_INDEX_TABLE = "/user_data/DG/hyde_with_table/BM25/Agri_inverted_agri_table_only"

SEARCHER = LuceneSearcher(DATAPATH_2_INVERTED_INDEX_TABLE)
SEARCHER.set_language('zh')

K = 15


# about time

# 取得當下的 UTC 時間
UTC_NOW = datetime.utcnow()

# 設定 UTC+8 的時區
UTC_8 = pytz.timezone('Asia/Taipei')

# 將 UTC 時間轉換為 UTC+8 時區的時間
NOW = UTC_NOW.replace(tzinfo=pytz.utc).astimezone(UTC_8)


def init_model():
    """123
    """
    print("enter init_model")

    # # 我寫的
    # model = AutoModelForCausalLM.from_pretrained(
    #     PATH_2_MODEL,
    #     low_cpu_mem_usage=True,
    #     device_map=DEVICE_MAP
    # )

    if API_USE is False:
        torch.cuda.empty_cache()
        print(f"GPU: {torch.cuda.get_device_name(0)}")

        # 信彰的
        model = AutoModelForCausalLM.from_pretrained(
            PATH_2_MODEL,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            # attn_implementation="flash_attention_2", # optional for inference (有些顯卡不能用)
            # 會報錯要去 huggingface 下載
            # pip install flash-attn --no-build-isolation
            trust_remote_code=True, # MUST
        )
        model.config.use_cache = False
        model.config.pretraining_tp = 1

        tokenizer = AutoTokenizer.from_pretrained(PATH_2_MODEL, trust_remote_code=True)
        tokenizer.padding_side = "right"

        print("exit init_model")
        return model, tokenizer

    return None


def create_full_prompt(user_prompt) -> str:
    """
    123
    """
    print("enter create_full_prompt")

    # 讀取 prompt 的 components
    with open(DATAPATH_2_PROMPT, 'r', encoding='utf-8') as file:
        print("\tstart dealing file")
        total_prompt = json.load(file)
        system_prompt = total_prompt[BOT]
        print("\tend dealing file")

    full_prompt = f"<s> {system_prompt} [INST] 依照你的知識回答：{user_prompt} [/INST]"

    print("exit create_full_prompt")
    return full_prompt


def call_model(prompt, model_and_tokenizer: None):
    """123
    """
    print("enter call_model")

    if API_USE is True:
        if BOT=="taide":

            DATA["prompt"]=prompt

            r = requests.post(HOST+"/completions", json=DATA, headers=HEADERS)
            r = r.json()
            if "choices" in r:
                response = r["choices"][0]["text"]
                response = str(response)

        if BOT=="chatGPT":

            messages = [{"role": "user", "content": prompt}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106", messages=messages, temperature=0
            )
            response = response.choices[0].message.content

    else:
        model, tokenizer = model_and_tokenizer

        print("\tbefore tokenize")
        sentence_input = tokenizer(
            prompt,
            add_special_tokens=False,
            return_tensors="pt"
        ).to(model.device)
        print("\tafter tokenize")

        print("\tbefore generate")
        response = model.generate(
            **sentence_input,
            generation_config=GENERATION_CONFIG,
        )
        print("\tafter generate")
        print(f"\tresponse =\n\t\t{response}")

        response = tokenizer.batch_decode(
            response[:, sentence_input.input_ids.size(1) :], skip_special_tokens=True
            )
        print(f"\tresponse =\n\t\t{response}")

    print("exit call_model")
    return response


def call_BM25(search_key):
    """123
    """
    print("enter call_BM25")

    total_hit = SEARCHER.search(search_key, K)
    print(f"\ttotal_hit =\n\t\t{total_hit}")
    # total_docid = [hit.docid for hit in total_hit]
    total_docid = []
    total_doc = []
    for hit in total_hit:
        print(f"\thit =\n\t\t{hit}")

        doc_id = hit.docid
        total_docid.append(doc_id)

        raw_doc = SEARCHER.doc(doc_id).raw()
        content = json.loads(raw_doc)['contents']
        total_doc.append(content)

    print("exit call_BM25")
    return total_docid, total_doc


def save_logging(file_dir, total_logging):
    """123
    """

    now_time = NOW.strftime("%Y_%m%d_%H%M")
    file_name = f"{BOT}_{now_time}.json"
    file_dir = "/user_data/DG/hyde_with_table/logging/hyde_the_query"

    file_path = f"{file_dir}/{file_name}"
    with open(file_path, 'w', encoding='utf-8') as file:
        print("\t\tstart dealing file")
        json.dump(total_logging, file, ensure_ascii=False)
        print("\t\tend dealing file")

    return file_path


def new_logging(query):
    """123
    """
    logging = {}
    logging['query'] = query
    total_docid, total_doc = call_BM25(query)
    logging['docid'] = total_docid
    logging['doc'] = total_doc

    return logging


def exam_hyde_query(model_and_tokenizer):
    """123
    """
    print("enter exam_hyde_query")

    with open(DATAPATH_2_PSEUDO_QUERY, 'r', encoding='utf-8') as file:
        print("\t\tstart dealing file")
        total_query = json.load(file)
        print("\t\tend dealing file")

    total_logging = []
    for query in total_query:
        print(f"\t\tquery =\n\t\t\t{query}")
        total_logging.append({})

        query = query['query']
        print(f"\t\tquery =\n\t\t\t{query}")
        total_logging[-1]['original'] = new_logging(query)

        full_prompt = create_full_prompt(query)
        hyde_query = call_model(full_prompt, model_and_tokenizer)
        print(f"\t\thyde_query =\n\t\t\t{hyde_query}")
        total_logging[-1]['hyde'] = new_logging(query)


    file_dir = "/user_data/DG/hyde_with_table/logging/hyde_the_query"
    save_logging(file_dir, total_logging)

    print("exit exam_hyde_query")
    return total_logging


def main() -> None:
    """123
    """
    print("enter main")

    if API_USE is True:
        model_and_tokenizer = None
    else:
        model_and_tokenizer = init_model()

    exam_hyde_query(model_and_tokenizer)

    print("exit main")

if __name__ == "__main__":
    main()
