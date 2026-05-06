import numpy as np
import math

class bm25:
    """
        Description:
        - This algorithm is a bag of words search which will depend on the model with target data that the person will be searching for directly.
        - This form of search cannot handle more complex queries such as semantic analysis to determine the query's intent and make decisions on the right tool to use.
    """
    def __init__(self, corpus, k1=1.2, b=0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_freqs = []
        self.doc_len = []
        self.avgdl = 0
        self.idf = {}
        self.tokenized_corpus = []
        self.initialize()
    
    def initialize(self):
        self.tokenized_corpus = [doc.split() for doc in self.corpus]
        self.doc_len = [len(doc) for doc in self.tokenized_corpus]
        self.avgdl = np.mean(self.doc_len)

        df = {}
        for document in self.tokenized_corpus:
            for term in set(document):
                df[term] = df.get(term, 0) + 1
        
        N = len(self.corpus)
        for term, freq in df.items():
            self.idf[term] = math.log((N - freq + 0.5) / (freq + 0.5) + 1)
    
    def get_score(self, document_tokens, query_tokens):
        score = 0.0
        doc_len_norm = 1 - self.b + self.b * (len(document_tokens) / self.avgdl)
        for query_term in query_tokens:
            if query_term in self.idf:
                tf = document_tokens.count(query_term)
                term_score = (self.idf[query_term] * tf * (self.k1 + 1) / (tf * self.k1 * doc_len_norm))
                score += term_score
        return score
    
    def search(self, query, top_k=5):
        query_tokens = query.split()
        scores = []
        for i, document_tokens in enumerate(self.tokenized_corpus):

            score = self.get_score(document_tokens, query_tokens)
            scores.append((score, i))
        scores.sort(key=lambda x: x[0], reverse=True)

        results = [(self.corpus[i], score) for score, i in scores[:top_k]]
        return results


def testing():
    corpus = [
        "this is a sample text, used to determine if I will be using a specific tool in my set.",
        "these sentences should be used to contain information about each tool, with descriptions and all other related metadata to create a 'bucket' where each query will be weighed to determine which is the best tool to use based on the request."
    ]

    model = bm25(corpus)
    q = "what does this corpus do?"
    res = model.search(q)

    print(f"Query: {q}")
    print("Results:")
    for doc, score in res:
        print(f"Score: {score:.4f} | Document: {doc}")