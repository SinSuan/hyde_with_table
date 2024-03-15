"""123
"""

import os
import json
from pyserini.search.lucene import LuceneSearcher


def init_BM25():
    """123
    """
    datapath = os.getenv("DATAPATH_2_INVERTED_INDEX_TABLE")
    SEARCHER = LuceneSearcher(datapath)
    SEARCHER.set_language('zh')

    return SEARCHER


def call_BM25(SEARCHER, search_key):
    """123
    """
    print("enter call_BM25")

    TOP_K = os.getenv("TOP_K")
    TOP_K = int(TOP_K)
    total_hit = SEARCHER.search(search_key, TOP_K)
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