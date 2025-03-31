import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
import os

st.set_page_config(page_title="Sociograma", layout="wide")

st.title("🧠 Generador de Sociogramas")

# --- Paso 1: Introducir nombres de alumnos ---
st.header("1. Introduce la lista de alumnos")
nombres_input = st.text_area("Escribe un nombre por línea:")

if nombres_input:
    alumnos = [nombre.strip() for nombre in nombres_input.splitlines() if nombre.strip()]
    st.success(f"{len(alumnos)} alumnos introducidos")
else:
    alumnos = []

# --- Paso 2: Añadir preguntas ---
st.header("2. Añade preguntas sociométricas")

preguntas = st.experimental_get_query_params().get("preguntas", [])
nueva_pregunta = st.text_input("Escribe una nueva pregunta:")

if st.button("Añadir pregunta") and nueva_pregunta:
    preguntas.append(nueva_pregunta)
    st.experimental_set_query_params(preguntas=preguntas)

if preguntas:
    st.write("Preguntas añadidas:")
    for i, p in enumerate(preguntas):
        st.write(f"{i+1}. {p}")

# --- Paso 3: Responder preguntas ---
st.header("3. Responde cada pregunta por alumno")
respuestas = {}

if alumnos and preguntas:
    for pregunta in preguntas:
        st.subheader(pregunta)
        respuestas[pregunta] = {}
        for alumno in alumnos:
            seleccionados = st.multiselect(
                f"{alumno} elige (máx. 3)",
                options=[a for a in alumnos if a != alumno],
                key=f"{pregunta}-{alumno}",
                max_selections=3
            )
            respuestas[pregunta][alumno] = seleccionados

    # Guardar respuestas
    if st.button("💾 Guardar respuestas"):
        datos = {
            "alumnos": alumnos,
            "preguntas": preguntas,
            "respuestas": respuestas
        }
        with open("respuestas_sociograma.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        st.success("Datos guardados correctamente en 'respuestas_sociograma.json'")

# --- Paso 4: Visualizar sociogramas ---
st.header("4. Visualizar sociogramas")

if st.button("📊 Generar sociogramas"):
    if not respuestas:
        try:
            with open("respuestas_sociograma.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
                alumnos = datos["alumnos"]
                preguntas = datos["preguntas"]
                respuestas = datos["respuestas"]
        except FileNotFoundError:
            st.error("No hay datos guardados. Primero debes guardar respuestas.")

    if respuestas:
        for pregunta in preguntas:
            st.subheader(f"Sociograma: {pregunta}")
            G = nx.DiGraph()
            G.add_nodes_from(alumnos)
            for origen, destinos in respuestas[pregunta].items():
                for destino in destinos:
                    G.add_edge(origen, destino)

            # Calcular tamaño de nodos según popularidad (in-degree)
            in_degrees = dict(G.in_degree())
            sizes = [300 + in_degrees[n]*300 for n in G.nodes()]

            # Colores: rojo para aislados
            colors = ['red' if G.degree(n) == 0 else 'skyblue' for n in G.nodes()]

            # Layout mejorado (orgánico, más espaciado)
            pos = nx.spring_layout(G, seed=42, k=1.5, iterations=200)

            fig, ax = plt.subplots(figsize=(7, 7))
            nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes, alpha=0.9)
            nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True, arrowstyle='-|>', min_source_margin=15, min_target_margin=15)
            nx.draw_networkx_labels(G, pos, font_size=9)
            plt.axis('off')
            st.pyplot(fig)
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=2000, font_size=10, edge_color="gray", arrows=True)
            st.pyplot(fig)
