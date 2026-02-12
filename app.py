import streamlit as st
import spacy
import networkx as nx
from pyvis.network import Network
import os
import random

# -------------------------------
# Load or Download Model
# -------------------------------
@st.cache_resource
def load_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.write("Downloading spaCy model...")
        os.system("python -m spacy download en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_model()

# -------------------------------
# Extract Triples
# -------------------------------
def extract_triples(text):
    doc = nlp(text)
    triples = []
    for sent in doc.sents:
        subject, relation, obj = "", "", ""
        for token in sent:
            if "subj" in token.dep_:
                subject = token.text
            if "obj" in token.dep_:
                obj = token.text
            if token.pos_ == "VERB":
                relation = token.lemma_
        if subject and relation and obj:
            triples.append((subject, relation, obj))
    return triples

# -------------------------------
# Build Connected Graph
# -------------------------------
def text_to_connected_graph(text):
    triples = extract_triples(text)
    G = nx.DiGraph()

    color_palette = [
        "#FF5733", "#33FF57", "#3357FF", "#FF33A6", "#33FFF5",
        "#F3FF33", "#B833FF", "#FF9A33", "#33FF9E", "#FF3333"
    ]

    for s, r, o in triples:
        G.add_node(s, color=random.choice(color_palette))
        G.add_node(o, color=random.choice(color_palette))
        G.add_edge(s, o, title=r, label=r)

    # Connect all subgraphs to one main component
    if not nx.is_connected(G.to_undirected()):
        components = list(nx.connected_components(G.to_undirected()))
        main_component = components[0]
        for i in range(1, len(components)):
            node1 = list(main_component)[0]
            node2 = list(components[i])[0]
            G.add_edge(node1, node2, label="related_to", title="related_to")
            main_component = main_component.union(components[i])

    return G, triples

# -------------------------------
# Visualization with Better Zoom
# -------------------------------
def visualize_graph(G, output_file="knowledge_graph.html"):
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black",
        notebook=False
    )

    net.from_nx(G)

    # Compact layout physics
    net.repulsion(
        node_distance=90,
        spring_length=90,
        spring_strength=0.08,
        damping=0.85
    )

    # ✅ Proper JSON for PyVis (fixes JSONDecodeError)
    net.set_options("""
    {
      "physics": {
        "stabilization": true,
        "barnesHut": {
          "gravitationalConstant": -2000,
          "springLength": 90,
          "springConstant": 0.04
        }
      },
      "interaction": {
        "dragNodes": true,
        "dragView": true,
        "hover": true,
        "zoomView": true,
        "tooltipDelay": 150,
        "zoomSpeed": 0.5,
        "navigationButtons": true,
        "keyboard": true
      },
      "nodes": {
        "shape": "dot",
        "scaling": {
          "min": 8,
          "max": 35
        },
        "font": {
          "size": 14,
          "strokeWidth": 2
        }
      },
      "edges": {
        "arrows": {
          "to": { "enabled": true, "scaleFactor": 0.7 }
        },
        "smooth": {
          "type": "dynamic"
        }
      }
    }
    """)

    net.save_graph(output_file)
    return output_file

# -------------------------------
# Streamlit Interface
# -------------------------------
st.set_page_config(page_title="Knowledge Graph Generator", layout="wide")
st.title("🎨 Multi-Colored Knowledge Graph Generator")
st.markdown(
    "Paste your paragraph below. The app extracts subjects, relations, and objects, then builds a **colorful, zoomable knowledge graph**."
)

user_text = st.text_area(
    "Enter your paragraph:", height=200, placeholder="Type or paste your paragraph here..."
)

if st.button("Generate Knowledge Graph"):
    if not user_text.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Building your graph..."):
            G, triples = text_to_connected_graph(user_text)
            graph_path = visualize_graph(G)

        st.success("✅ Knowledge graph created successfully!")
        st.subheader("Extracted Relations:")
        st.write(triples)

        # Show interactive HTML graph
        st.components.v1.html(open(graph_path, "r", encoding="utf-8").read(), height=750, scrolling=True)

        # Download button
        with open(graph_path, "rb") as f:
            st.download_button(
                label="📥 Download Knowledge Graph (HTML)",
                data=f,
                file_name="knowledge_graph.html",
                mime="text/html"
            )
