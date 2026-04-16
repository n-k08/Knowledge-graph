import spacy
import networkx as nx
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load("en_core_web_sm")

# -------------------------------
# Clean words
# -------------------------------
def clean_words(text):
    doc = nlp(text)
    return [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and token.text.lower() not in STOP_WORDS
    ]

# -------------------------------
# Sentence-level triples
# -------------------------------
def extract_sentence_triples(text):
    doc = nlp(text)
    triples = []

    for sent in doc.sents:
        for token in sent:
            if token.dep_ in ("nsubj", "nsubjpass"):
                subject = " ".join([t.text for t in token.subtree])
                relation = token.head.lemma_

                obj = None
                for child in token.head.children:
                    if child.dep_ in ("dobj", "pobj", "attr"):
                        obj = " ".join([t.text for t in child.subtree])

                if subject and obj:
                    triples.append((subject, relation, obj))

    return triples

# -------------------------------
# Word-level graph
# -------------------------------
def build_word_graph(text, window_size=2):
    words = clean_words(text)
    edges = []

    for i in range(len(words)):
        for j in range(i+1, min(i+window_size, len(words))):
            if words[i] != words[j]:
                edges.append((words[i], words[j], "co_occurs"))

    return edges

# -------------------------------
# HYBRID GRAPH
# -------------------------------
def build_hybrid_graph(text):
    G = nx.DiGraph()

    # Sentence triples
    triples = extract_sentence_triples(text)

    for s, r, o in triples:
        G.add_node(s, type="entity")
        G.add_node(o, type="entity")
        G.add_edge(s, o, label=r, type="relation")

    # Word connections
    word_edges = build_word_graph(text)

    for w1, w2, rel in word_edges:
        G.add_node(w1, type="word")
        G.add_node(w2, type="word")
        G.add_edge(w1, w2, label=rel, type="co_occurrence")

    return G, triples