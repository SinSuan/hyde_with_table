"""123
"""

import json
from dotenv import load_dotenv
from module.time_now import time_now


# DATAPATH_2_LOG_NDR = \
#     "/user_data/DG/hyde_with_table/logging/ndr/recycle/rearrange_search_records_0312-2.json"
DATAPATH_2_LOG_NDR = \
    "/user_data/DG/hyde_with_table/logging/ndr/recycle/rearrange_search_records_0312.json"

DATAPATH_2_TTL_DOC = \
    "/user_data/DG/hyde_with_table/BM25/Agri_inverted_agri_table_only_113-0309/index/0309.json"



def extract_Document(total_logging):
    """123
    """
    rearrange_logging = {}
    for logging in total_logging:

        # print(f"rearrange_logging = \n\t{rearrange_logging}")
        # print(f"logging = \n\t{logging}")

        Document = logging["Document"]
        if Document not in rearrange_logging:
            rearrange_logging[Document] = {}

        Question = logging["Question"]
        if Question not in rearrange_logging[Document]:
            rearrange_logging[Document][Question] = {}

        Model = logging["Model"]
        Reply = logging["Reply"]
        rearrange_logging[Document][Question][Model] = Reply

    return rearrange_logging


def main() -> None:
    """123
    """

    with open(DATAPATH_2_LOG_NDR, 'r', encoding='utf-8') as file:
        total_logging = json.load(file).keys()
        total_logging = list(total_logging)

    with open(DATAPATH_2_TTL_DOC, 'r', encoding='utf-8') as file:
        total_doc = json.load(file)

    total_ndr_doc = []
    for doc in total_doc:
        if doc['title'] in total_logging:
            total_ndr_doc.append(doc)

    # total_title = extract_Document(total_logging)

    now_time = time_now()
    file_dir = \
        "/user_data/DG/hyde_with_table/BM25/Agri_inverted_agri_table_only_113-0309/index_ndr"
    file_name = f"{now_time}.json"

    file_path = f"{file_dir}/{file_name}"
    with open(file_path, 'w', encoding='utf-8') as file:
        print("\t\tstart save total_logging")
        # json.dump(total_ndr_doc, file, ensure_ascii=False)
        json.dump(total_ndr_doc, file, ensure_ascii=False)
        print("\t\tend save total_logging")


if __name__ == "__main__":
    load_dotenv("/user_data/DG/hyde_with_table/global_variable/.env")
    main()
