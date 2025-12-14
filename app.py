"""
🏙️ URBAN AI - Version Streamlit avec données GitHub
Power by Lab_Math and CIE - Copyright © 2025
"""

import streamlit as st
import pandas as pd
import hashlib
import requests
import io
import os
from PIL import Image

# ==================== CONFIGURATION GLOBALE ====================
st.set_page_config(
    page_title="URBAN AI | Lab_Math",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration des URLs GitHub (À adapter avec VOS liens réels)
# Astuce : Utilisez toujours l'URL "Raw" pour le fichier Excel
GITHUB_REPO_URL = "https://raw.githubusercontent.com/Marcialsohfos/urban_data/main"
EXCEL_URL = f"{GITHUB_REPO_URL}/indicateurs_urbains.xlsx"
# Pour les images, on pointera vers le dossier raw
IMAGES_BASE_URL = f"{GITHUB_REPO_URL}/images" 

# Mot de passe hashé (urbankit@1001a)
MASTER_PASSWORD_HASH = hashlib.sha256("urbankit@1001a".encode()).hexdigest()

# ==================== FONCTIONS UTILITAIRES ====================

def check_password():
    """Gère l'authentification simple"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown(
            """
            <style>
            .stApp {background-color: #f0f2f6;}
            .login-box {
                max-width: 400px; margin: 100px auto; padding: 30px;
                background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🔐 URBAN AI")
            st.markdown("Système de gestion des données urbaines")
            password = st.text_input("Mot de passe d'accès", type="password")
            
            if st.button("Se connecter", type="primary"):
                if hashlib.sha256(password.encode()).hexdigest() == MASTER_PASSWORD_HASH:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect")
            
            st.caption("Power by Lab_Math and CIE © 2025")
        return False
    return True

@st.cache_data(ttl=3600) # Cache les données pendant 1 heure pour ne pas spammer GitHub
def load_data_from_github():
    """Télécharge et met en cache le fichier Excel depuis GitHub"""
    try:
        headers = {'User-Agent': 'Urban-AI-App/1.0'}
        response = requests.get(EXCEL_URL, headers=headers)
        response.raise_for_status()
        
        # Lecture du contenu binaire
        with io.BytesIO(response.content) as f:
            df = pd.read_excel(f)
            
        # Nettoyage des colonnes (votre logique)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur de connexion GitHub : {e}")
        # Retourne un DataFrame vide en cas d'erreur pour ne pas planter l'app
        return pd.DataFrame()

def get_image_url(filename, folder_type="troncons"):
    """Construit l'URL de l'image sur GitHub"""
    if pd.isna(filename) or str(filename).strip() == "":
        return None
    # On suppose que vos dossiers sur GitHub sont 'uploads/troncons' ou 'uploads/taudis'
    # Adaptez le chemin selon votre structure réelle sur GitHub
    return f"{IMAGES_BASE_URL}/{folder_type}/{filename}"

# ==================== APPLICATION PRINCIPALE ====================

def main():
    # 1. Vérification Mot de passe
    if not check_password():
        return

    # 2. Sidebar & Navigation
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/city.png", width=100)
        st.title("🏙️ URBAN AI")
        st.caption("Version GitOps v3.3")
        st.divider()
        
        # Bouton déconnexion
        if st.button("🚪 Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()
            
        st.divider()
        st.info(f"Source : GitHub\nStatut : Connecté ✅")

    # 3. Chargement des données
    with st.spinner('🔄 Synchronisation avec GitHub en cours...'):
        df = load_data_from_github()

    if df.empty:
        st.warning("⚠️ Aucune donnée chargée. Vérifiez l'URL GitHub dans le code.")
        st.stop()

    # 4. Filtres (Logique hiérarchique Ville -> Commune)
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        villes = sorted(df['Ville'].unique().astype(str))
        selected_ville = st.selectbox("📍 Ville", villes)
    
    with col_filter2:
        # Filtrer les communes selon la ville choisie
        communes = sorted(df[df['Ville'] == selected_ville]['Nom de la Commune'].unique().astype(str))
        selected_commune = st.selectbox("🏘️ Commune", communes)

    # Filtrage du DataFrame principal
    mask = (df['Ville'] == selected_ville) & (df['Nom de la Commune'] == selected_commune)
    df_commune = df[mask]

    # ==================== ONGLETS D'ANALYSE ====================
    tab1, tab2, tab3 = st.tabs(["📊 Tableau de Bord", "📸 Galerie Images", "🤖 Maintenance (IA)"])

    # --- TAB 1: DASHBOARD ---
    with tab1:
        st.header(f"Analyse : {selected_commune}")
        
        # Calcul des KPIs
        total_ml = df_commune['linéaire de voirie(ml)'].sum()
        total_taudis = df_commune['superficie de la poche du quartier de taudis'].sum()
        nb_nids = len(df_commune[df_commune['présence du nid de poule'].notna()])
        nb_lum = df_commune['Nombre de point lumineux sur le tronçon'].sum()

        # Affichage KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Linéaire Voirie", f"{total_ml:,.0f} m")
        k2.metric("Surface Taudis", f"{total_taudis:,.0f} m²")
        k3.metric("Nids de poule", f"{nb_nids} tronçons", delta_color="inverse")
        k4.metric("Éclairage", f"{nb_lum} points", delta_color="normal")

        st.divider()

        # Tableaux de données
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🛣️ Détail des Tronçons")
            cols_voirie = ['tronçon de voirie', 'linéaire de voirie(ml)', 'classe de voirie', 'présence du nid de poule']
            # On vérifie que les colonnes existent
            cols_exist = [c for c in cols_voirie if c in df_commune.columns]
            st.dataframe(df_commune[cols_exist], use_container_width=True, height=300)

        with c2:
            st.subheader("🏘️ Détail des Taudis")
            cols_taudis = ['Nom de la poche du quartier de taudis', 'superficie de la poche du quartier de taudis']
            cols_exist_t = [c for c in cols_taudis if c in df_commune.columns]
            st.dataframe(df_commune[cols_exist_t].drop_duplicates(), use_container_width=True, height=300)

    # --- TAB 2: GALERIE IMAGES (Lecture directe URL GitHub) ---
    with tab2:
        st.header("Inspection Visuelle")
        
        # Streamlit affiche les images directement depuis l'URL GitHub sans téléchargement local !
        # C'est beaucoup plus rapide que votre code Gradio précédent.
        
        st.subheader("Voirie & Tronçons")
        cols = st.columns(3)
        img_count = 0
        
        for index, row in df_commune.iterrows():
            img_name = row.get('image_troncon')
            if pd.notna(img_name) and str(img_name).lower() != 'nan':
                # Construction de l'URL brute GitHub
                # Adaptez 'uploads/troncons/' selon votre repo
                img_url = f"{GITHUB_REPO_URL}/uploads/troncons/{img_name}" 
                
                with cols[img_count % 3]:
                    st.image(img_url, caption=f"{row['tronçon de voirie']}", use_column_width=True)
                    # Petit hack pour vérifier si l'image charge (Streamlit gère les 404 proprement)
                img_count += 1
        
        if img_count == 0:
            st.info("Aucune image de voirie répertoriée pour cette commune.")

    # --- TAB 3: IA & Maintenance (Placeholder) ---
    with tab3:
        st.info("Module IA connecté aux données GitHub.")
        # Ici vous pouvez réimporter votre predictive_maintenance.py si vous le souhaitez
        # comme vu dans les étapes précédentes.

if __name__ == "__main__":
    main()