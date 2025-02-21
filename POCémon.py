import streamlit as st
import pandas as pd
import os

# -------------------------------------------------------------------
# 1) Streamlit Page Config
# -------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Choisis ton Pokémon")

# -------------------------------------------------------------------
# 2) Load Excel Data
# -------------------------------------------------------------------
excel_file = "base_de_donnees_pokemon.xlsx"
df = pd.read_excel(excel_file)
# Filter only available Pokémon
df_dispo = df[df["Disponibilité"] == "Disponible"]

# -------------------------------------------------------------------
# 3) Initialize Session State for the Selected Pokémon
# -------------------------------------------------------------------
if "selected_pokemon" not in st.session_state:
    st.session_state["selected_pokemon"] = None

# -------------------------------------------------------------------
# 4) Display the text inputs (name and message)
# -------------------------------------------------------------------
st.title("Pot de départ de Mickaël")

st.text("Pour son pot de départ, nous allons faire un jeu de carte avec les mots de chacun sur le thème de Pokémon, en effet la communauté Pokémon au sein de OnePoint ets plus grande que l'on s'imagine !")
col1, col2 = st.columns(2)
prenom = col1.text_input("Prénom :", key="prenom")
nom = col2.text_input("Nom :", key="nom")

message = st.text_area("Ton message d'au revoir (max 150 caractères car limité par la taille de la carte) :", max_chars=150, key="message")

# -------------------------------------------------------------------
# 5) Display a Grid of Pokémon (Image + Button)
# -------------------------------------------------------------------
st.subheader("Choisis un Pokémon :")
num_cols = 8  # Number of columns per row (adjust as needed)
cols = st.columns(num_cols)

for idx, row in df_dispo.iterrows():
    col = cols[idx % num_cols]
    with col:
        image_path = os.path.join("pokmon", row["PNG"])
        # Display the Pokémon image (adjust width as desired)
        st.image(image_path, width=150)
        # When this button is clicked, store the selected Pokémon in session state
        if st.button(row["Pokemon"], key=row["Pokemon"]):
            st.session_state["selected_pokemon"] = row["Pokemon"]

# Inform the user which Pokémon is currently selected
if st.session_state["selected_pokemon"]:
    st.info(f"Vous avez sélectionné : **{st.session_state['selected_pokemon']}**")
else:
    st.info("Aucun Pokémon sélectionné pour le moment.")

# -------------------------------------------------------------------
# 6) Send Button to Submit All Data
# -------------------------------------------------------------------
# Center the "Envoyer" button and change its color
col_center = st.columns([1,1,1])
with col_center[1]:
    if st.button("Envoyer", key="envoyer", help="Cliquez pour envoyer votre message", use_container_width=True):
        if nom and message and st.session_state["selected_pokemon"]:
            # Update the DataFrame for the selected Pokémon
            df.loc[df["Pokemon"] == st.session_state["selected_pokemon"],
                   ["Nom", "Message", "Disponibilité"]] = [nom, message, "Indisponible"]
            df.to_excel(excel_file, index=False)
            st.success("Ton message a bien été envoyé !")
            # Reset the selection and re-run the app to reflect changes
            st.session_state["selected_pokemon"] = None
            st.rerun()
        else:
            st.error("Merci de remplir tous les champs et de sélectionner un Pokémon !")
