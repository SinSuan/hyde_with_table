"""123
"""

import os
import openai
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig,
)
import requests


def init_model(BOT):
    """123
    """
    print("enter init_model")

    if BOT=="breeze":
        print("\tenter if breeze")

        torch.cuda.empty_cache()
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print("\t\tget GPU")

        # 信彰的
        DEVICE_MAP = "auto"
        PATH_2_MODEL = os.getenv("PATH_2_MODEL")
        print("\t\tget PATH_2_MODEL")
        model = AutoModelForCausalLM.from_pretrained(
            PATH_2_MODEL,
            device_map=DEVICE_MAP,
            torch_dtype=torch.bfloat16,
            # attn_implementation="flash_attention_2", # optional for inference (有些顯卡不能用)
            # 會報錯要去 huggingface 下載
            # pip install flash-attn --no-build-isolation
            trust_remote_code=True, # MUST
        )
        print("\t\tget model")

        model.config.use_cache = False
        model.config.pretraining_tp = 1

        tokenizer = AutoTokenizer.from_pretrained(PATH_2_MODEL, trust_remote_code=True)
        tokenizer.padding_side = "right"

        print("exit init_model")

        model_and_tokenizer = [model, tokenizer]

        print("\texit if breeze")

    elif BOT=="taide":
        model_and_tokenizer = None

    elif BOT=="chatGPT":
        openai.api_key = os.getenv("openai_api_key")
        model_and_tokenizer = None

    return model_and_tokenizer


def call_model(BOT, prompt, model_and_tokenizer: None):
    """123
    """
    print("enter call_model")

    if BOT=="breeze":
        model, tokenizer = model_and_tokenizer

        print("\tbefore tokenize")
        sentence_input = tokenizer(
            prompt,
            add_special_tokens=False,
            return_tensors="pt"
        ).to(model.device)
        print("\tafter tokenize")

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

    elif BOT=="taide":

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

        DATA["prompt"]=prompt

        r = requests.post(HOST+"/completions", json=DATA, headers=HEADERS)
        r = r.json()
        if "choices" in r:
            response = r["choices"][0]["text"]
            response = str(response)

    elif BOT=="chatGPT":

        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106", messages=messages, temperature=0
        )
        response = response.choices[0].message.content

    print("exit call_model")
    return response
