import streamlit as st
from graph_builder import build_hybrid_graph
from pyvis.network import Network
import random

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Hybrid Knowledge Graph", layout="wide")

# -------------------------------
# Dark UI Styling
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
textarea {
    background-color: #1c1f26 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Hybrid Knowledge Graph")
st.markdown("Dark mode • Clean • Colorful Nodes")

# -------------------------------
# Input
# -------------------------------
text = st.text_area(
    "Enter text",
    height=200,
    placeholder="Example: Elon Musk founded SpaceX. Tesla builds electric cars."
)

# -------------------------------
# Generate Graph
# -------------------------------
if st.button("Generate Graph"):
    if not text.strip():
        st.warning("⚠️ Enter some text")
    else:
        G, triples = build_hybrid_graph(text)

        st.subheader("🔗 Extracted Relationships")
        st.write(triples if triples else "No strong relations found.")

        # -------------------------------
        # Graph Setup
        # -------------------------------
        net = Network(
            height="750px",
            width="100%",
            directed=True,
            bgcolor="#0e1117",
            font_color="white"
        )

        # 🎨 NODE COLORS (random)
        node_colors = ["#9D4EDD", "#2ECC71", "#FF4DA6"]  # Violet, Green, Pink

        # 🔗 EDGE COLOR
        edge_color = "#FFA500"  # Orange

        # -------------------------------
        # Add Nodes (Random Colors)
        # -------------------------------
        for node in G.nodes():
            net.add_node(
                node,
                label=node,
                color=random.choice(node_colors),
                size=22,
                font={"size": 16, "color": "white"}
            )

        # -------------------------------
        # Add Edges (Orange only)
        # -------------------------------
        for s, t, data in G.edges(data=True):
            net.add_edge(
                s, t,
                label=data.get("label", ""),
                color=edge_color,
                width=2
            )

        # -------------------------------
        # Smooth Layout
        # -------------------------------
        net.set_options("""
        {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -2300,
              "centralGravity": 0.3,
              "springLength": 140,
              "springConstant": 0.05,
              "damping": 0.9
            }
          },
          "interaction": {
            "hover": true,
            "zoomView": true,
            "dragView": true,
            "navigationButtons": true
          },
          "edges": {
            "smooth": {
              "type": "dynamic"
            }
          }
        }
        """)

        html = net.generate_html()
        st.components.v1.html(html, height=750)

        # -------------------------------
        # Download
        # -------------------------------
        st.download_button(
            label="📥 Download Graph",
            data=html,
            file_name="colorful_graph.html",
            mime="text/html"
        )