import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text

st.set_page_config(layout="wide", page_title="Pot de départ Mickaël", page_icon="🎉")
st.title("Pot de Départ de Mickaël")

@st.cache_resource
def get_engine(): 
    db_config = st.secrets["postgres"]
    connection_string = (
        f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    )
    return create_engine(connection_string)

engine = get_engine()

@st.cache_data(ttl=300)
def get_available_pokemon():
    query = 'SELECT * FROM pokemon WHERE "Disponibilité" = \'Disponible\''
    df = pd.read_sql_query(query, engine)
    return df


st.text("Pour son pot de départ, nous allons faire un jeu de carte avec les mots de chacun sur le thème de Pokémon, la communauté Pokémon au sein de Onepoint est plus grande qu'on ne l'imagine !")
col1, col2 = st.columns(2)
prenom = col1.text_input("Prénom :", key="prenom")
nom = col2.text_input("Nom :", key="nom")
message = st.text_area("Ton message d'au revoir (max 250 caractères car limité par la taille de la carte) :", max_chars=250, key="message")


st.subheader("Choisis un Pokémon :")
df_dispo = get_available_pokemon()

pokemon_list = df_dispo.to_dict(orient="records")


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
        if prenom and nom and message and st.session_state["selected_pokemon"]:
            with engine.connect() as conn:
                conn.execute(text("""
                    UPDATE pokemon
                    SET "Prénom" = :prenom, "Nom" = :nom, "Message" = :message, "Disponibilité" = 'Indisponible'
                    WHERE "Pokemon" = :pokemon
                """), {"prenom":prenom, "nom": nom, "message": message, "pokemon": st.session_state["selected_pokemon"]})
                conn.commit()
            st.success("Ton message a bien été envoyé et enregistré !")
            st.session_state["selected_pokemon"] = None
            get_available_pokemon.clear()
            st.rerun()
        else:
            st.error("Merci de remplir tous les champs et de sélectionner un Pokémon !")
