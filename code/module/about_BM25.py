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


def call_BM25(total_query):
    """123
    """
    print("\tenter call_BM25")

    print(f"\ttotal_query =\n\t{total_query}")
    SEARCHER = init_BM25()
    TOP_K = os.getenv("TOP_K")
    TOP_K = int(TOP_K)
    total_query_hits = []
    for query in total_query:
        print(f"\t\tquery =\n\t\t{query}")
        total_query_hits.append(SEARCHER.search(query, TOP_K))

    total_query_docids = []
    total_query_docs = []
    for query_hits in total_query_hits:
        total_docid = []
        total_doc = []
        for hit in query_hits:
            print(f"\thit =\n\t\t{hit}")

            doc_id = hit.docid
            total_docid.append(doc_id)

            raw_doc = SEARCHER.doc(doc_id).raw()
            content = json.loads(raw_doc)['contents']
            total_doc.append(content)

        total_query_docids.append(total_docid)
        total_query_docs.append(total_doc)

    print("\texit call_BM25")
    return total_query_docids, total_query_docs