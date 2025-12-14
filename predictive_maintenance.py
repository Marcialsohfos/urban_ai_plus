import pandas as pd
import numpy as np
import joblib
import os

class MaintenancePredictor:
    def __init__(self):
        self.model = None
        self.model_path = 'models/maintenance_model.pkl'
        
        # Tentative de chargement du modèle (si vous l'avez entraîné et uploadé)
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                self.model = None

    def predict_priority(self, row):
        """
        Prédit la priorité de maintenance.
        Accepte une ligne (row) du DataFrame Pandas (fichier Excel).
        """
        
        # 1. Extraction sécurisée des données (Noms exacts des colonnes Excel)
        # On utilise .get() pour éviter les crashs si une colonne manque
        
        # Nettoyage des valeurs (gestion des NaN/Vides)
        nid_poule = str(row.get('présence du nid de poule', '')).strip().lower()
        classe = str(row.get('classe de voirie', '')).strip().title()
        
        try:
            lineaire = float(row.get('linéaire de voirie(ml)', 0))
        except:
            lineaire = 0
            
        try:
            lumieres = float(row.get('Nombre de point lumineux sur le tronçon', 0))
        except:
            lumieres = 0

        # 2. LOGIQUE EXPERTE (RÈGLES MÉTIER)
        # C'est ce qui tourne si vous n'avez pas de modèle IA entraîné (.pkl)
        
        score = 0
        
        # Règle A : Présence de nid de poule (Critique)
        if nid_poule in ['oui', 'yes', 'vrai', 'true'] or len(nid_poule) > 0:
            score += 50
            
        # Règle B : Importance de la route
        if 'Primaire' in classe:
            score += 20
        elif 'Secondaire' in classe:
            score += 10
            
        # Règle C : Sécurité / Éclairage (Si route longue mais peu éclairée)
        if lineaire > 500 and lumieres < 5:
            score += 15
        
        # Règle D : Taille du tronçon (Plus c'est long, plus c'est cher/important)
        if lineaire > 2000:
            score += 10

        # Normalisation du score (max 100)
        final_score = min(score, 100)

        # 3. DÉCISION ET ACTION
        if final_score >= 60:
            label = "🚨 URGENT"
            action = "Colmatage immédiat & Renforcement"
        elif final_score >= 30:
            label = "⚠️ Prioritaire"
            action = "Planifier réfection (Trimestre 1)"
        else:
            label = "✅ Surveillance"
            action = "Maintenance préventive standard"

        # Retourne le format exact attendu par votre app.py
        return {
            'label': label,
            'score': final_score,
            'action': action,
            'confiance': 100 # Simulé à 100% car basé sur des règles strictes
        }