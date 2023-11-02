import streamlit as st

# Set the app title and page icon
st.set_page_config(page_title="Bienvenue sur l'application", page_icon=":fr:")

# Define the welcome message
st.title("Bienvenue sur l'application Streamlit")


st.write("Cette application vous propose trois modules de prévision :")
st.write("1. Prévision des demandes")
st.write("2. Plan de production")
st.write("3. Plan de distribution")

st.write("Pour télécharger des données de démonstration :")

# Download links for dummy data
if st.button("Télécharger des données de démonstration pour la Prévision des demandes"):
    st.write("Lien de téléchargement pour les données de prévision des demandes, https://docs.google.com/spreadsheets/d/1EYllPfaaGXW2Gxm9kV9GaqtXQenzjzi9/edit?usp=drive_link&ouid=100086090455415161840&rtpof=true&sd=true")
    # Add a link to download the dummy data for "Prévision des demandes"

if st.button("Télécharger des données de démonstration pour le Plan de distribution"):
    st.write("Lien de téléchargement pour les données de plan de distribution, https://drive.google.com/drive/folders/1eiAI5zAJEclXeHhbaOoZsi6v3NGVos4N?usp=sharing")
    # Add a link to download the dummy data for "Plan de distribution"

# Create a sidebar menu for module selection
module = st.sidebar.selectbox("Sélectionnez un module :", ["Prévision des demandes","Plan de distribution"])

# Instructions for each module
if module == "Prévision des demandes":
    st.header("Module 1 : Prévision des demandes")
    st.write("Ce module vous aide à prévoir la demande de l'année prochaine en se basant sur la demande réelle des années précédentes.")
    st.write("Voici comment utiliser ce module :")
    st.write("1. Tout d'abord, vous devez télécharger les données ou utiliser le fichier de démonstration.")
    st.write("2. Cliquez sur le bouton \"Calculer\" pour obtenir les résultats de la prévision.")
    st.write("3. Vous pouvez afficher les données en cliquant sur \"Afficher la Liste des Ventes\".")
    st.write("Profitez de la fonctionnalité de prévision des demandes pour améliorer votre planification.")
    
    # Add the code for data upload, calculation, and displaying data for Prévision des demandes here

elif module == "Plan de distribution":
    st.header("Module 2 : Plan de distribution")
    st.write("Ce module vous aide à créer un plan de livraison optimal pour minimiser l'âge des produits dans l'étalage.")
    st.write("Voici comment utiliser ce module :")
    st.write("1. Tout d'abord, vous devez télécharger la \"liste des lots\" et \"Télécharger la liste des commandes\" ou utiliser le fichier de démonstration.")
    st.write("2. Cliquez sur le bouton \"Créer Le Plan Optimal\" pour générer votre plan de distribution.")
    st.write("3. Vous pouvez afficher les données en cliquant sur \"Afficher la Liste des Ventes\".")
    st.write("4. Pour télécharger le plan de distribution optimal, cliquez sur \"📥 Télécharger le plan\".")
    st.write("Optimisez votre plan de distribution et améliorez la gestion de vos produits en magasin.")
    
    # Add the code for data upload, plan creation, displaying data, and downloading the plan for Plan de distribution here

# You can add more modules and instructions as needed

# Add a footer or any additional content
st.write("Si vous avez des questions, veuillez nous contacter.")
