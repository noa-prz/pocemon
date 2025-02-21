import streamlit as st
import pandas as pd
import sqlite3
import os

# Fichiers utilisés
EXCEL_FILE = "base_de_donnees_pokemon.xlsx"
DB_FILE = "pokemon.db"

# Fonction d'initialisation de la base SQLite à partir de l'Excel
def init_db_from_excel():
    # Connexion à la base SQLite (création si nécessaire)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    # Création de la table si elle n'existe pas déjà
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pokemon (
            Pokemon TEXT PRIMARY KEY,
            PNG TEXT,
            Disponibilité TEXT,
            Nom TEXT,
            Message TEXT
        )
    """)
    conn.commit()
    # Si la table est vide, on insère toutes les lignes depuis l'Excel initial
    cursor.execute("SELECT COUNT(*) FROM pokemon")
    count = cursor.fetchone()[0]
    if count == 0:
        df = pd.read_excel(EXCEL_FILE)
        df.to_sql("pokemon", conn, if_exists="append", index=False)
    return conn

# Initialisation de la base
conn = init_db_from_excel()

# Fonction pour obtenir les Pokémon disponibles
def get_available_pokemon(conn):
    query = "SELECT * FROM pokemon WHERE Disponibilité = 'Disponible'"
    df = pd.read_sql_query(query, conn)
    return df

# Configurer Streamlit
st.set_page_config(layout="wide", page_title="Pot de départ Mickaël", page_icon="🎉")
st.title("Pot de Départ de Mickaël")

st.text("Pour son pot de départ, nous allons faire un jeu de carte avec les mots de chacun sur le thème de Pokémon, en effet la communauté Pokémon au sein de OnePoint est plus grande que l'on s'imagine !")
col1, col2 = st.columns(2)
prenom = col1.text_input("Prénom :", key="prenom")
nom = col2.text_input("Nom :", key="nom")
message = st.text_area("Ton message d'au revoir (max 150 caractères car limité par la taille de la carte) :", max_chars=150, key="message")

# Affichage de la grille des Pokémon disponibles
st.subheader("Choisis un Pokémon :")
df_dispo = get_available_pokemon(conn)
# Conversion du DataFrame en liste de dictionnaires
pokemon_list = df_dispo.to_dict(orient="records")

# Définir le nombre de colonnes par ligne
num_cols = 8
cols = st.columns(num_cols)

# Initialiser la variable de sélection dans la session
if "selected_pokemon" not in st.session_state:
    st.session_state["selected_pokemon"] = None

for idx, pokemon in enumerate(pokemon_list):
    col = cols[idx % num_cols]
    with col:
        image_path = os.path.join("pokmon", pokemon["PNG"])
        st.image(image_path, width=150)
        if st.button(pokemon["Pokemon"], key=pokemon["Pokemon"]):
            st.session_state["selected_pokemon"] = pokemon["Pokemon"]

if st.session_state["selected_pokemon"]:
    st.info(f"Vous avez sélectionné : **{st.session_state['selected_pokemon']}**")
else:
    st.info("Aucun Pokémon sélectionné pour le moment.")

# Bouton pour envoyer les informations
col_center = st.columns([1,1,1])
with col_center[1]:
    if st.button("Envoyer", key="envoyer", help="Cliquez pour envoyer votre message", use_container_width=True):
        if nom and message and st.session_state["selected_pokemon"]:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pokemon
                SET Nom = ?, Message = ?, Disponibilité = 'Indisponible'
                WHERE Pokemon = ?
            """, (nom, message, st.session_state["selected_pokemon"]))
            conn.commit()
            st.success("Ton message a bien été envoyé et enregistré dans la base de données !")
            st.session_state["selected_pokemon"] = None
        else:
            st.error("Merci de remplir tous les champs et de sélectionner un Pokémon !")
