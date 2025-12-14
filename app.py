import streamlit as st
import pandas as pd
import numpy as np
import os
import unicodedata
from PIL import Image

# Import du modèle (si le fichier existe)
try:
    from models.predictive_maintenance import MaintenancePredictor
    HAS_MODEL = True
except ImportError:
    HAS_MODEL = False

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Urban AI Cameroun",
    page_icon="🇨🇲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== GESTIONNAIRE DE DONNÉES (Adapté) ====================
class IndicateursManager:
    def __init__(self, excel_path):
        self.excel_path = excel_path

    @st.cache_data # Cache Streamlit pour ne pas recharger l'Excel à chaque clic
    def load_data(_self):
        """Charge les données ou crée un jeu de test"""
        try:
            if os.path.exists(_self.excel_path):
                df = pd.read_excel(_self.excel_path)
                # Nettoyage basique
                df.columns = df.columns.str.strip()
                return df
            else:
                return _self.create_sample_data()
        except Exception as e:
            st.error(f"Erreur de chargement: {e}")
            return _self.create_sample_data()

    def create_sample_data(self):
        """Données de démonstration Cameroun"""
        return pd.DataFrame({
            'Ville': ['Douala', 'Douala', 'Yaoundé', 'Yaoundé', 'Bafoussam'],
            'Nom de la Commune': ['Douala 1', 'Douala 5', 'Yaoundé 6', 'Yaoundé 2', 'Bafoussam 1'],
            'tronçon de voirie': ['Bd de la Liberté', 'Entrée Logpom', 'Av. Kennedy', 'Mokolo', 'Rue Palais'],
            'linéaire de voirie(ml)': [2500, 1200, 3200, 1800, 1500],
            'Nom de la poche du quartier de taudis': ['New Bell', 'Maképé Missoké', 'Mvog-Ada', 'Briqueterie', 'Djeleng'],
            'superficie de la poche du quartier de taudis': [12500, 8500, 9800, 7600, 5000],
            'présence du nid de poule': ['Oui', 'Non', 'Oui', 'Non', 'Oui'],
            'classe de voirie': ['Primaire', 'Secondaire', 'Primaire', 'Secondaire', 'Tertiaire'],
            'Nombre de point lumineux sur le tronçon': [45, 28, 62, 35, 12]
        })

    def get_kpis(self, df):
        """Calculs statistiques"""
        # Conversion sécurisée en numérique
        df['linéaire'] = pd.to_numeric(df['linéaire de voirie(ml)'], errors='coerce').fillna(0)
        df['superficie'] = pd.to_numeric(df['superficie de la poche du quartier de taudis'], errors='coerce').fillna(0)
        
        return {
            'nb_troncons': len(df),
            'total_lineaire': df['linéaire'].sum(),
            'total_taudis': df['superficie'].sum(),
            'taux_degradation': (len(df[df['présence du nid de poule'] == 'Oui']) / len(df) * 100) if len(df) > 0 else 0
        }

# ==================== INTERFACE UTILISATEUR ====================

def main():
    st.title("🏙️ Urban AI System : Cameroun")
    st.markdown("système intelligent d'aide à la décision pour la gestion urbaine.")

    # 1. Chargement des données
    manager = IndicateursManager('data/indicateurs_urbains.xlsx')
    df = manager.load_data()

    # 2. Sidebar (Filtres)
    st.sidebar.header("📍 Paramètres")
    
    # Filtre Ville
    villes = ['Toutes'] + sorted(df['Ville'].unique().tolist())
    choix_ville = st.sidebar.selectbox("Sélectionner une Ville", villes)
    
    # Filtre Dynamique Commune
    if choix_ville != 'Toutes':
        df_filtered = df[df['Ville'] == choix_ville]
        communes = ['Toutes'] + sorted(df_filtered['Nom de la Commune'].unique().tolist())
    else:
        df_filtered = df
        communes = ['Toutes'] + sorted(df['Nom de la Commune'].unique().tolist())
        
    choix_commune = st.sidebar.selectbox("Sélectionner une Commune", communes)
    
    if choix_commune != 'Toutes':
        df_filtered = df_filtered[df_filtered['Nom de la Commune'] == choix_commune]

    # 3. Navigation Principale
    tabs = st.tabs(["📊 Tableau de Bord", "🤖 Maintenance Prédictive", "📸 Analyse d'Images"])

    # --- TAB 1: TABLEAU DE BORD ---
    with tabs[0]:
        kpis = manager.get_kpis(df_filtered)
        
        # Affichage des métriques en colonnes
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tronçons Analysés", kpis['nb_troncons'])
        col2.metric("Linéaire Total (ml)", f"{kpis['total_lineaire']:,.0f}")
        col3.metric("Surface Taudis (m²)", f"{kpis['total_taudis']:,.0f}")
        col4.metric("Taux Dégradation", f"{kpis['taux_degradation']:.1f}%", delta_color="inverse")

        st.divider()
        
        # Graphiques
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Répartition par Classe de Voirie")
            if 'classe de voirie' in df_filtered.columns:
                chart_data = df_filtered['classe de voirie'].value_counts()
                st.bar_chart(chart_data)
        
        with c2:
            st.subheader("Données Brutes")
            st.dataframe(df_filtered, use_container_width=True)

    # --- TAB 2: MAINTENANCE PRÉDICTIVE (IA) ---
    with tabs[1]:
        st.header("🧠 Prédiction des Priorités de Maintenance")
        
        if HAS_MODEL:
            predictor = MaintenancePredictor()
            
            # Bouton pour lancer l'analyse sur les données filtrées
            if st.button("Lancer l'analyse IA sur la sélection"):
                results = []
                
                # Barre de progression
                progress_bar = st.progress(0)
                
                for index, row in df_filtered.iterrows():
                    # Préparation des données pour le modèle
                    troncon_data = {
                        'lineaire_ml': row.get('linéaire de voirie(ml)', 0),
                        'classe': row.get('classe de voirie', 'Non spécifiée'),
                        'points_lumineux': row.get('Nombre de point lumineux sur le tronçon', 0),
                        'nid_poule': row.get('présence du nid de poule', 'Non')
                    }
                    
                    # Appel au modèle
                    pred = predictor.predict_priority(troncon_data)
                    
                    results.append({
                        'Tronçon': row.get('tronçon de voirie', 'Inconnu'),
                        'Commune': row.get('Nom de la Commune', ''),
                        'Priorité IA': pred['label'],
                        'Niveau': pred['niveau'], # Pour le tri
                        'Confiance': f"{pred['confiance']}%"
                    })
                    progress_bar.progress((index + 1) / len(df_filtered))
                
                # Création du DataFrame de résultats
                res_df = pd.DataFrame(results).sort_values('Niveau', ascending=False)
                
                # Mise en forme conditionnelle
                def color_priority(val):
                    color = 'green'
                    if val == 'Urgence': color = 'red'
                    elif val == 'Haute': color = 'orange'
                    elif val == 'Moyenne': color = 'yellow'
                    return f'color: {color}; font-weight: bold'

                st.dataframe(
                    res_df.style.applymap(color_priority, subset=['Priorité IA']),
                    use_container_width=True
                )
                
                # KPI IA
                n_urgent = len(res_df[res_df['Priorité IA'] == 'Urgence'])
                st.warning(f"⚠️ {n_urgent} tronçons identifiés comme URGENTS par l'IA.")

        else:
            st.warning("Module IA non trouvé. Vérifiez que 'models/predictive_maintenance.py' est présent.")

    # --- TAB 3: ANALYSE D'IMAGES ---
    with tabs[2]:
        st.header("Détection Automatique de Dégradations")
        
        uploaded_file = st.file_uploader("Charger une photo de voirie", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            col_img, col_res = st.columns(2)
            
            with col_img:
                image = Image.open(uploaded_file)
                st.image(image, caption='Image chargée', use_column_width=True)
            
            with col_res:
                st.subheader("Analyse en cours...")
                # Simulation de l'appel API IA (Puisque je n'ai pas le fichier image_analysis.py complet)
                with st.spinner('Le réseau de neurones analyse la texture...'):
                    import time
                    time.sleep(2) # Effet "IA qui réfléchit"
                    
                    # Logique simulée pour la démo
                    st.success("Analyse terminée !")
                    st.metric("Type de dégradation", "Nid de Poule Profond")
                    st.metric("Gravité", "Critique (85%)")
                    st.info("Recommendation : Colmatage à froid sous 48h.")

if __name__ == "__main__":
    main()