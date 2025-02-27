import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
import time
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

@st.dialog("Confirmation", width="small")
def show_confirmation_dialog():
    st.write("🥳​ Ton pokémon et ton message ont bien été enregistrés ! ✅​")
    if st.button("Fermer"):
        st.session_state["selected_pokemon"] = None
        get_available_pokemon.clear()
        st.rerun()

colonne1, colonne2 = st.columns([3, 1])
with colonne1:

    st.text("Pour son pot de départ, nous allons faire un jeu de carte avec les mots de chacun sur le thème de Pokémon, la communauté Pokémon au sein de Onepoint est plus grande qu'on ne l'imagine !")
    st.info("⚠️ Pour info : premier arrivé, premier servi. Si un Pokémon a déjà été choisi, il n'apparaît plus dans les propositions.")

    col1, col2 = st.columns(2)
    prenom = col1.text_input("Prénom :", key="prenom")
    nom = col2.text_input("Nom :", key="nom")
    message = st.text_area("Ton message d'au revoir (max 250 caractères car limité par la taille de la carte) :", max_chars=250, key="message")

with colonne2:
    st.markdown("**Exemple de carte :**")
    example_images = "carte1.png"
    image_path = os.path.join("cartes", example_images)
    st.image(image_path, width=250)

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
            show_confirmation_dialog()
        else:
            st.error("Merci de remplir tous les champs et de sélectionner un Pokémon !")