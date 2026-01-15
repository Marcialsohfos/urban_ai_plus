"""
🏙️ URBAN AI - Version Finale Complète (Data + IA)
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
import os

# ==================== 1. CONFIGURATION ====================
GITHUB_USER = "Marcialsohfos"
GITHUB_REPO = "urban_ai_plus"
GITHUB_BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# Mot de passe : urbankit@1001a
MASTER_PASSWORD_HASH = hashlib.sha256("urbankit@1001a".encode()).hexdigest()

st.set_page_config(page_title="URBAN AI | Cameroun", page_icon="🇨🇲", layout="wide")

# ==================== 2. IMPORTATION DU MODÈLE IA ====================
# On utilise un try/except pour ne pas faire planter l'appli si le dossier models n'est pas encore poussé
try:
    from models.predictive_maintenance import MaintenancePredictor
    HAS_AI = True
except ImportError:
    HAS_AI = False

# ==================== 3. FONCTIONS UTILITAIRES ====================
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 URBAN AI Access")
            password = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter", type="primary"):
                if hashlib.sha256(password.encode()).hexdigest() == MASTER_PASSWORD_HASH:
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Mot de passe incorrect")
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
    commune = str(row.get('Nom de la Commune', '')).strip().title()
    base = COMMUNE_COORDS.get(commune, {'lat': 3.86, 'lon': 11.52})
    return pd.Series({
        'latitude': base['lat'] + random.uniform(-0.02, 0.02),
        'longitude': base['lon'] + random.uniform(-0.02, 0.02)
    })

@st.cache_data(ttl=3600)
def load_data():
    """
    Charge les données depuis le fichier local s'il existe (cas du déploiement),
    sinon tente de le télécharger depuis GitHub (cas du développement local sans data).
    """
    local_path = "data/uploads/indicateurs_urbains.xlsx"
    df = pd.DataFrame()

    # Tentative 1 : Lecture Locale (Recommandé pour Streamlit Cloud)
    if os.path.exists(local_path):
        try:
            df = pd.read_excel(local_path)
        except Exception as e:
            st.error(f"Erreur lecture fichier local : {e}")
    
    # Tentative 2 : Téléchargement GitHub (Fallback)
    if df.empty:
        url = f"{BASE_URL}/data/uploads/indicateurs_urbains.xlsx"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with io.BytesIO(response.content) as f:
                df = pd.read_excel(f)
        except Exception as e:
            # Si on est ici, ni le local ni le distant n'ont marché
            st.error("Impossible de charger les données. Vérifiez que le fichier 'indicateurs_urbains.xlsx' est bien dans 'data/uploads/' sur GitHub.")
            return pd.DataFrame()

    # Nettoyage et ajout GPS
    df.columns = df.columns.str.strip()
    if 'latitude' not in df.columns:
        gps_data = df.apply(add_simulated_gps, axis=1)
        df = pd.concat([df, gps_data], axis=1)
    
    return df

def get_img_url_github(filename, folder):
    if pd.isna(filename) or str(filename).strip() == "": return None
    clean_name = str(filename).strip().replace(" ", "%20")
    return f"{BASE_URL}/data/uploads/{folder}/{clean_name}"

# ==================== 4. APPLICATION PRINCIPALE ====================
def main():
    if not check_password(): return

    with st.sidebar:
        st.title("🏙️ URBAN AI")
        st.success("Mode : Connecté")
        if HAS_AI:
            st.info("🧠 Module IA : Actif")
        else:
            st.warning("🧠 Module IA : Non détecté (Vérifiez le dossier models/)")
        
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()

    with st.spinner("Chargement des données..."):
        df = load_data()
    if df.empty: st.stop()

    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        villes = sorted(df['Ville'].astype(str).unique())
        ville_sel = st.selectbox("Ville", villes)
    with col2:
        communes = sorted(df[df['Ville'] == ville_sel]['Nom de la Commune'].astype(str).unique())
        commune_sel = st.selectbox("Commune", communes)

    df_c = df[(df['Ville'] == ville_sel) & (df['Nom de la Commune'] == commune_sel)]

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tableau de Bord", "📸 Images", "🗺️ Carte", "🧠 Analyse IA"])

    with tab1:
        st.header(f"KPIs : {commune_sel}")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Tronçons", len(df_c))
        k2.metric("Linéaire", f"{df_c['linéaire de voirie(ml)'].sum():,.0f} m")
        nb_nids = len(df_c[df_c['présence du nid de poule'].notna()])
        k3.metric("Zones Dégradées", nb_nids, delta_color="inverse")
        k4.metric("Taudis", f"{df_c['superficie de la poche du quartier de taudis'].sum():,.0f} m²")
        st.dataframe(df_c, use_container_width=True)

    with tab2:
        st.header("Galerie")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Voirie")
            for _, row in df_c.iterrows():
                url = get_img_url_github(row.get('image_troncon'), "troncons")
                if url: st.image(url, caption=row.get('tronçon de voirie'), use_container_width=True)
        with c2:
            st.subheader("Taudis")
            for _, row in df_c.iterrows():
                url = get_img_url_github(row.get('image_taudis'), "taudis")
                if url: st.image(url, caption=row.get('Nom de la poche du quartier de taudis'), use_container_width=True)

    with tab3:
        st.header("Carte")
        if 'latitude' in df_c.columns:
            center = [df_c['latitude'].mean(), df_c['longitude'].mean()]
            m = folium.Map(location=center, zoom_start=13)
            for _, row in df_c.iterrows():
                color = 'red' if row.get('présence du nid de poule') == 'Oui' else 'green'
                folium.Marker([row['latitude'], row['longitude']], popup=row.get('tronçon de voirie'), icon=folium.Icon(color=color)).add_to(m)
            st_folium(m, width=None, height=500)

    # --- TAB 4 : INTELLIGENCE ARTIFICIELLE ---
    with tab4:
        st.header("🤖 Maintenance Prédictive & Recommandations")
        
        if not HAS_AI:
            st.error("Le fichier 'models/predictive_maintenance.py' est introuvable ou contient des erreurs.")
            st.info("Assurez-vous d'avoir un fichier vide '__init__.py' dans le dossier 'models'.")
        else:
            # Instanciation du modèle
            predictor = MaintenancePredictor()
            
            st.markdown("Ce module utilise l'IA pour prioriser les interventions en fonction de la dégradation, de l'éclairage et de l'importance de la voirie.")
            
            if st.button("🚀 Lancer l'analyse IA sur la commune"):
                results = []
                
                # Barre de progression
                progress_bar = st.progress(0)
                
                for i, (index, row) in enumerate(df_c.iterrows()):
                    # Appel au modèle pour chaque ligne
                    pred = predictor.predict_priority(row)
                    
                    results.append({
                        "Tronçon": row.get('tronçon de voirie'),
                        "Priorité": pred['label'],
                        "Score Risque": pred['score'],
                        "Action Recommandée": pred['action'],
                        "État Actuel": "Dégradé" if row.get('présence du nid de poule') == 'Oui' else "Stable"
                    })
                    progress_bar.progress((i + 1) / len(df_c))
                
                # Création du tableau de résultats
                res_df = pd.DataFrame(results)
                
                # Tri par score de risque
                res_df = res_df.sort_values(by="Score Risque", ascending=False)
                
                # Affichage avec couleurs
                def highlight_urgent(val):
                    color = 'red' if 'URGENT' in str(val) else 'black'
                    return f'color: {color}; font-weight: bold'

                st.subheader("📋 Rapport de Priorisation")
                st.dataframe(res_df.style.map(highlight_urgent, subset=['Priorité']), use_container_width=True)
                
                # Statistiques de l'analyse
                n_urgent = len(res_df[res_df['Priorité'].str.contains('URGENT')])
                st.warning(f"⚠️ {n_urgent} tronçons nécessitent une intervention immédiate dans cette commune.")

if __name__ == "__main__":
    main()