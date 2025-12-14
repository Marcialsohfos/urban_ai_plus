"""
🏙️ URBAN AI - Version Finale Corrigée (Streamlit + GitHub)
Power by Lab_Math and CIE - Copyright © 2025
"""

import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import hashlib
import io
import random

# ==================== 1. CONFIGURATION DU PROJET ====================
# Vérifiez scrupuleusement ces informations
GITHUB_USER = "Marcialsohfos"       
GITHUB_REPO = "urban_ai_plus"       
GITHUB_BRANCH = "main"              

# Construction de la racine URL
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# Mot de passe hashé (urbankit@1001a)
MASTER_PASSWORD_HASH = hashlib.sha256("urbankit@1001a".encode()).hexdigest()

st.set_page_config(
    page_title="URBAN AI | Cameroun",
    page_icon="🇨🇲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 2. FONCTIONS UTILITAIRES ====================

def check_password():
    """Gère l'écran de connexion"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 URBAN AI Access")
            st.markdown("### Système de gestion des données urbaines")
            password = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter", type="primary"):
                if hashlib.sha256(password.encode()).hexdigest() == MASTER_PASSWORD_HASH:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")
        return False
    return True

COMMUNE_COORDS = {
    'Yaounde 1': {'lat': 3.8850, 'lon': 11.5200}, 'Yaounde 2': {'lat': 3.8980, 'lon': 11.5000},
    'Yaounde 3': {'lat': 3.8400, 'lon': 11.5000}, 'Yaounde 4': {'lat': 3.8450, 'lon': 11.5500},
    'Yaounde 5': {'lat': 3.8700, 'lon': 11.5400}, 'Yaounde 6': {'lat': 3.8550, 'lon': 11.4800},
    'Yaounde 7': {'lat': 3.8750, 'lon': 11.4500}, 'Douala 1': {'lat': 4.0500, 'lon': 9.7000},
    'Douala 2': {'lat': 4.0600, 'lon': 9.7100},   'Douala 3': {'lat': 4.0400, 'lon': 9.7300},
    'Douala 4': {'lat': 4.0700, 'lon': 9.6600},   'Douala 5': {'lat': 4.0800, 'lon': 9.7500},
}

def add_simulated_gps(row):
    """Ajoute des coordonnées GPS si elles manquent"""
    commune = str(row.get('Nom de la Commune', '')).strip().title()
    base = COMMUNE_COORDS.get(commune, {'lat': 3.86, 'lon': 11.52})
    return pd.Series({
        'latitude': base['lat'] + random.uniform(-0.02, 0.02),
        'longitude': base['lon'] + random.uniform(-0.02, 0.02)
    })

@st.cache_data(ttl=3600)
def load_data():
    """Télécharge l'Excel depuis GitHub avec gestion d'erreur intelligente"""
    
    # 1. Essai avec le dossier /data/
    url_v1 = f"{BASE_URL}/data/indicateurs_urbains.xlsx"
    # 2. Essai à la racine (au cas où l'utilisateur n'a pas mis de dossier data)
    url_v2 = f"{BASE_URL}/indicateurs_urbains.xlsx"

    try:
        # Tentative 1
        response = requests.get(url_v1, timeout=10)
        
        # Si échec (404), on tente le chemin racine
        if response.status_code == 404:
            # st.warning(f"Fichier non trouvé dans /data/, tentative à la racine...") # Décommenter pour debug
            response = requests.get(url_v2, timeout=10)
        
        response.raise_for_status()
        
        with io.BytesIO(response.content) as f:
            df = pd.read_excel(f)
        
        df.columns = df.columns.str.strip()
        
        if 'latitude' not in df.columns:
            gps_data = df.apply(add_simulated_gps, axis=1)
            df = pd.concat([df, gps_data], axis=1)
            
        return df
        
    except Exception as e:
        st.error(f"❌ ERREUR CRITIQUE DE CHARGEMENT")
        st.write(f"Le système a tenté de lire : `{url_v1}`")
        st.write(f"Erreur technique : {e}")
        st.info("💡 CONSEIL : Vérifiez que votre dépôt GitHub est PUBLIC et que le fichier 'indicateurs_urbains.xlsx' existe bien.")
        return pd.DataFrame()

def get_img_url_github(filename, folder):
    """Génère le lien direct vers l'image GitHub"""
    if pd.isna(filename) or str(filename).strip() == "":
        return None
    
    clean_name = str(filename).strip().replace(" ", "%20")
    
    # URL V1: Dans le dossier data/uploads
    url = f"{BASE_URL}/data/uploads/{folder}/{clean_name}"
    
    # Vous pouvez ajouter ici une logique de vérification si nécessaire
    return url

# ==================== 3. APPLICATION PRINCIPALE ====================

def main():
    if not check_password():
        return

    with st.sidebar:
        st.title("🏙️ URBAN AI")
        st.success("Statut : Connecté")
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()

    # --- CHARGEMENT ---
    with st.spinner(f"Synchronisation avec {GITHUB_REPO}..."):
        df = load_data()

    if df.empty:
        st.stop()

    # --- FILTRES ---
    col1, col2 = st.columns(2)
    with col1:
        villes = sorted(df['Ville'].astype(str).unique())
        ville_sel = st.selectbox("Ville", villes)
    with col2:
        communes = sorted(df[df['Ville'] == ville_sel]['Nom de la Commune'].astype(str).unique())
        commune_sel = st.selectbox("Commune", communes)

    df_c = df[(df['Ville'] == ville_sel) & (df['Nom de la Commune'] == commune_sel)]

    tab1, tab2, tab3 = st.tabs(["📊 Tableau de Bord", "📸 Galerie Images", "🗺️ Carte Interactive"])

    # --- TAB 1: DASHBOARD ---
    with tab1:
        st.header(f"Indicateurs : {commune_sel}")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Tronçons", len(df_c))
        k2.metric("Linéaire Total", f"{df_c['linéaire de voirie(ml)'].sum():,.0f} ml")
        k3.metric("Surface Taudis", f"{df_c['superficie de la poche du quartier de taudis'].sum():,.0f} m²")
        
        nb_nids = len(df_c[df_c['présence du nid de poule'].notna()])
        k4.metric("Zones Dégradées", nb_nids, delta_color="inverse")
        
        # Correction warning: use_container_width au lieu de use_column_width
        st.dataframe(df_c, use_container_width=True)

    # --- TAB 2: IMAGES ---
    with tab2:
        st.header("Inspection Visuelle")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🛣️ Voirie")
            for _, row in df_c.iterrows():
                url = get_img_url_github(row.get('image_troncon'), "troncons")
                if url:
                    # Correction warning
                    st.image(url, caption=row.get('tronçon de voirie'), use_container_width=True)
        
        with c2:
            st.subheader("🏘️ Taudis")
            for _, row in df_c.iterrows():
                url = get_img_url_github(row.get('image_taudis'), "taudis")
                if url:
                    # Correction warning
                    st.image(url, caption=row.get('Nom de la poche du quartier de taudis'), use_container_width=True)

    # --- TAB 3: CARTE ---
    with tab3:
        st.header("Cartographie des Risques")
        if 'latitude' in df_c.columns:
            center = [df_c['latitude'].mean(), df_c['longitude'].mean()]
            m = folium.Map(location=center, zoom_start=13)
            
            for _, row in df_c.iterrows():
                color = 'red' if row.get('présence du nid de poule') == 'Oui' else 'green'
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=f"{row.get('tronçon de voirie')}",
                    icon=folium.Icon(color=color)
                ).add_to(m)
            
            st_folium(m, width=None, height=500)
        else:
            st.warning("Coordonnées GPS indisponibles.")

if __name__ == "__main__":
    main()