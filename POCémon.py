import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text

# Récupérer la configuration de la base distante depuis les secrets
db_config = st.secrets["postgres"]
connection_string = (
    f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
    f"@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
)

# Création de l'engine SQLAlchemy
engine = create_engine(connection_string)

# Fichier Excel initial
EXCEL_FILE = "base_de_donnees_pokemon.xlsx"

# Fonction d'initialisation de la base PostgreSQL à partir de l'Excel
def init_db_from_excel(engine):
    with engine.connect() as conn:
        # Créer la table si elle n'existe pas (attention aux accents : on met "Disponibilité" entre guillemets)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pokemon (
                "Pokemon" TEXT PRIMARY KEY,
                "PNG" TEXT,
                "Disponibilité" TEXT,
                "Nom" TEXT,
                "Message" TEXT
            )
        """))
        # Vérifier si la table est vide
        result = conn.execute(text("SELECT COUNT(*) FROM pokemon"))
        count = result.fetchone()[0]
        if count == 0:
            # Charger l'Excel et insérer les données dans la table
            df = pd.read_excel(EXCEL_FILE)
            df.to_sql("pokemon", engine, if_exists="append", index=False)
        conn.commit()
    return engine

# Initialisation de la base distante
engine = init_db_from_excel(engine)

# Fonction pour obtenir les Pokémon disponibles
def get_available_pokemon(engine):
    query = 'SELECT * FROM pokemon WHERE "Disponibilité" = \'Disponible\''
    df = pd.read_sql_query(query, engine)
    return df

# Configuration de Streamlit
st.set_page_config(layout="wide", page_title="Pot de départ Mickaël", page_icon="🎉")
st.title("Pot de Départ de Mickaël")

st.text("Pour son pot de départ, nous allons faire un jeu de carte avec les mots de chacun sur le thème de Pokémon, en effet la communauté Pokémon au sein de OnePoint est plus grande que l'on s'imagine !")
col1, col2 = st.columns(2)
prenom = col1.text_input("Prénom :", key="prenom")
nom = col2.text_input("Nom :", key="nom")
message = st.text_area("Ton message d'au revoir (max 150 caractères car limité par la taille de la carte) :", max_chars=150, key="message")

# Affichage de la grille des Pokémon disponibles
st.subheader("Choisis un Pokémon :")
df_dispo = get_available_pokemon(engine)
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
            with engine.connect() as conn:
                conn.execute(text("""
                    UPDATE pokemon
                    SET "Nom" = :nom, "Message" = :message, "Disponibilité" = 'Indisponible'
                    WHERE "Pokemon" = :pokemon
                """), {"nom": nom, "message": message, "pokemon": st.session_state["selected_pokemon"]})
                conn.commit()
            st.success("Ton message a bien été envoyé et enregistré dans la base de données !")
            st.session_state["selected_pokemon"] = None
        else:
            st.error("Merci de remplir tous les champs et de sélectionner un Pokémon !")
