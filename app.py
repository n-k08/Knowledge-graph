import streamlit as st
import spacy
import networkx as nx
from pyvis.network import Network
import random
import subprocess
import sys

# -------------------------------
# Load spaCy Model (Stable Fix)
# -------------------------------
@st.cache_resource
def load_model():
    try:
        return spacy.load("en_core_web_sm")
    except:
        subprocess.run(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
            check=True
        )
        return spacy.load("en_core_web_sm")

nlp = load_model()

# -------------------------------
# Extract Triples
# -------------------------------
def extract_triples(text):
    doc = nlp(text)
    triples = []

    for sent in doc.sents:
        subject, relation, obj = None, None, None

        for token in sent:
            if token.dep_ in ("nsubj", "nsubjpass"):
                subject = token.text
            elif token.dep_ in ("dobj", "pobj"):
                obj = token.text
            elif token.pos_ == "VERB":
                relation = token.lemma_

        if subject and relation and obj:
            triples.append((subject, relation, obj))

    return triples

# -------------------------------
# Build Graph
# -------------------------------
def text_to_connected_graph(text):
    triples = extract_triples(text)
    G = nx.DiGraph()

    colors = [
        "#FF5733", "#33FF57", "#3357FF", "#FF33A6",
        "#33FFF5", "#F3FF33", "#B833FF", "#FF9A33"
    ]

    for s, r, o in triples:
        if s not in G:
            G.add_node(s, color=random.choice(colors))
        if o not in G:
            G.add_node(o, color=random.choice(colors))

        G.add_edge(s, o, label=r, title=r)

    # Connect components
    if len(G.nodes) > 0 and not nx.is_connected(G.to_undirected()):
        comps = list(nx.connected_components(G.to_undirected()))
        main = list(comps[0])

        for comp in comps[1:]:
            G.add_edge(main[0], list(comp)[0], label="related_to")
            main.extend(comp)

    return G, triples

# -------------------------------
# Visualize Graph
# -------------------------------
def visualize_graph(G):
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black",
    )

    net.from_nx(G)

    net.set_options("""
    {
      "physics": {
        "stabilization": true,
        "barnesHut": {
          "gravitationalConstant": -2000,
          "springLength": 120,
          "springConstant": 0.04
        }
      },
      "interaction": {
        "hover": true,
        "zoomView": true,
        "dragView": true,
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)

    return net.generate_html()

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="Knowledge Graph Generator", layout="wide")

st.title("🎨 Knowledge Graph Generator")
st.markdown("Convert text into a **colorful interactive knowledge graph**.")

user_text = st.text_area(
    "Enter your paragraph:",
    height=200,
    placeholder="Example: Alice works at Google. Bob knows Alice."
)

if st.button("Generate Knowledge Graph"):
    if not user_text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating graph..."):
            G, triples = text_to_connected_graph(user_text)
            html = visualize_graph(G)

        st.success("✅ Graph Generated!")

        st.subheader("🔗 Extracted Triples")
        st.write(triples if triples else "No relationships found.")

        st.subheader("📊 Interactive Graph")
        st.components.v1.html(html, height=750, scrolling=True)

        st.download_button(
            label="📥 Download Graph",
            data=html,
            file_name="knowledge_graph.html",
            mime="text/html"
        )