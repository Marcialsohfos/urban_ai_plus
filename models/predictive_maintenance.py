# models/predictive_maintenance.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class MaintenancePredictor:
    def __init__(self):
        self.model = None
        self.model_path = 'models/maintenance_model.pkl'
        self.features = [
            'linéaire_ml', 'classe_voirie_encoded', 
            'points_lumineux', 'traffic_estimate'
        ]
        self.load_model()

    def load_model(self):
        """Charge le modèle s'il existe, sinon reste en mode None"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                self.model = None

    def prepare_features(self, df):
        """Prépare les données pour la prédiction (Feature Engineering)"""
        # Conversion en DataFrame si c'est un dict
        if isinstance(df, dict):
            df = pd.DataFrame([df])
        
        # Encodage simple
        mapping = {'Primaire': 3, 'Secondaire': 2, 'Tertiaire': 1, 'Non spécifiée': 0}
        df['classe_voirie_encoded'] = df['classe'].map(mapping).fillna(0)
        
        # Gestion des valeurs numériques
        df['linéaire_ml'] = pd.to_numeric(df['lineaire_ml'], errors='coerce').fillna(0)
        df['points_lumineux'] = pd.to_numeric(df['points_lumineux'], errors='coerce').fillna(0)
        
        # Feature engineering simple
        df['traffic_estimate'] = df['points_lumineux'] * 10 + df['linéaire_ml'] * 0.5
        
        # Retourner seulement les colonnes nécessaires
        # On s'assure que toutes les colonnes existent
        for col in self.features:
            if col not in df.columns:
                df[col] = 0
                
        return df[self.features]

    def predict_priority(self, troncon_data):
        """
        Prédit la priorité.
        Si pas de modèle entraîné -> Utilise une heuristique (règle métier)
        """
        X = self.prepare_features(troncon_data)
        
        priority_labels = {0: 'Basse', 1: 'Moyenne', 2: 'Haute', 3: 'Urgence'}

        if self.model:
            # Mode IA réelle
            try:
                prediction = self.model.predict_proba(X)
                level = np.argmax(prediction)
                confiance = float(prediction[0][level])
            except:
                # Fallback si erreur input
                level = 1
                confiance = 0.5
        else:
            # Mode "Simulation / Règle métier" (Important pour la démo sans entrainement)
            # Logique: Si beaucoup de nids de poule ou éclairage faible sur route primaire
            score = 0
            if troncon_data.get('nid_poule') == 'Oui': score += 2
            if troncon_data.get('classe') == 'Primaire': score += 1
            if troncon_data.get('points_lumineux', 0) < 10: score += 1
            
            level = min(score, 3)
            confiance = 1.0 # Simulé

        return {
            'niveau': int(level),
            'label': priority_labels.get(level, 'Inconnu'),
            'confiance': round(confiance * 100, 1)
        }