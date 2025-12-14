#!/usr/bin/env python3
"""
Script d'initialisation du projet Urban AI
"""

import os
import sys
import shutil

def setup_project():
    """Configure l'ensemble du projet"""
    
    print("=" * 60)
    print("🔧 CONFIGURATION DU PROJET URBAN AI")
    print("=" * 60)
    
    # 1. Création des dossiers nécessaires
    folders = [
        'models',
        'data',
        'static/css',
        'static/js',
        'static/images',
        'templates',
        'uploads/troncons',
        'uploads/taudis',
        'temp'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Dossier créé: {folder}")
    
    # 2. Création des fichiers de modèles d'IA
    models_content = {
        'models/__init__.py': '# Package des modèles d\'IA\n',
        'models/predictive_maintenance.py': '''import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
import os

class MaintenancePredictor:
    def __init__(self):
        self.model = None
        self.model_path = 'models/maintenance_model.pkl'
        self.load_or_train_model()
    
    def load_or_train_model(self):
        """Charge un modèle existant ou en entraîne un nouveau"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print("✅ Modèle de maintenance chargé depuis le fichier")
            else:
                print("⚠️ Modèle non trouvé, création d'un modèle factice")
                self.model = self.create_dummy_model()
                joblib.dump(self.model, self.model_path)
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            self.model = self.create_dummy_model()
    
    def create_dummy_model(self):
        """Crée un modèle factice pour la démonstration"""
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        
        # Données d'exemple pour l'entraînement
        X_train = np.random.rand(100, 6)
        y_train = np.random.randint(0, 4, 100)
        
        model.fit(X_train, y_train)
        return model
    
    def predict_priority(self, troncon_data):
        """Prédit la priorité de maintenance pour un tronçon"""
        priority_labels = {
            0: 'Basse priorité',
            1: 'Priorité moyenne', 
            2: 'Haute priorité',
            3: 'Urgence'
        }
        
        try:
            features = self.prepare_features(troncon_data)
            prediction = self.model.predict_proba(features)[0]
            priority_level = np.argmax(prediction)
            
            return {
                'niveau': int(priority_level),
                'label': priority_labels.get(priority_level, 'Inconnu'),
                'probabilite': float(prediction[priority_level]),
                'details': prediction.tolist()
            }
        except Exception as e:
            print(f"Erreur prédiction: {e}")
            return {
                'niveau': 0,
                'label': 'Indéterminé',
                'probabilite': 0.0,
                'details': [0.25, 0.25, 0.25, 0.25]
            }
    
    def prepare_features(self, troncon_data):
        """Prépare les caractéristiques pour la prédiction"""
        try:
            features = [
                troncon_data.get('lineaire_ml', 0),
                2 if troncon_data.get('classe') == 'Primaire' else 1,
                troncon_data.get('points_lumineux', 0),
                np.random.randint(5, 20),
                troncon_data.get('points_lumineux', 0) * 100,
                np.random.uniform(1000, 2000)
            ]
            return np.array(features).reshape(1, -1)
        except Exception as e:
            print(f"Erreur préparation caractéristiques: {e}")
            return np.zeros((1, 6))
''',
        
        'models/image_analysis.py': '''import numpy as np
import os

class RoadDefectDetector:
    def __init__(self):
        self.classes = ['bon_etat', 'nids_poule', 'fissures', 'deformation']
    
    def analyze_road_image(self, img_path):
        """Analyse une image de route (version factice)"""
        if not os.path.exists(img_path):
            return self.create_dummy_analysis()
        
        try:
            return self.create_dummy_analysis()
        except Exception as e:
            print(f"Erreur analyse image: {e}")
            return self.create_dummy_analysis()
    
    def create_dummy_analysis(self):
        """Crée une analyse factice"""
        probs = np.random.dirichlet(np.ones(4))
        class_idx = np.argmax(probs)
        
        return {
            'etat': self.classes[class_idx],
            'confiance': float(probs[class_idx]),
            'details': dict(zip(self.classes, probs.tolist()))
        }
    
    def detect_potholes(self, img_path):
        """Détection factice des nids-de-poule"""
        return {
            'nombre_nids_poule': np.random.randint(0, 5),
            'superficie_totale': np.random.uniform(0, 10),
            'details': []
        }
''',
        
        'models/resource_optimization.py': '''import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class UrbanResourceOptimizer:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def optimize_lighting(self, data):
        """Optimise l'éclairage public (version factice)"""
        if len(data) == 0:
            return []
        
        try:
            df = pd.DataFrame(data)
            features = df[['lineaire_ml', 'points_lumineux']].fillna(0).values
            
            if len(features) < 3:
                return self.create_simple_recommendations(df)
            
            features_scaled = self.scaler.fit_transform(features)
            
            kmeans = KMeans(n_clusters=min(3, len(features)), random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            
            recommendations = []
            for i in range(kmeans.n_clusters):
                cluster_data = df.iloc[clusters == i]
                avg_lights = cluster_data['points_lumineux'].mean()
                avg_length = cluster_data['lineaire_ml'].mean()
                
                optimal_lights = max(5, int(avg_length / 40))
                
                recommendations.append({
                    'cluster': i,
                    'troncons': len(cluster_data),
                    'eclairage_actuel_moyen': float(avg_lights),
                    'eclairage_recommande': optimal_lights,
                    'economie_potentielle': float(avg_lights - optimal_lights),
                    'troncons_cibles': cluster_data['nom'].tolist()[:5]
                })
            
            return recommendations
        except Exception as e:
            print(f"Erreur optimisation éclairage: {e}")
            return self.create_simple_recommendations(data)
    
    def create_simple_recommendations(self, data):
        """Crée des recommandations simples"""
        if not data:
            return []
        
        return [{
            'cluster': 0,
            'troncons': len(data),
            'eclairage_actuel_moyen': 20.0,
            'eclairage_recommande': 15,
            'economie_potentielle': 5.0,
            'troncons_cibles': [d.get('nom', 'Inconnu') for d in data[:3]]
        }]
'''
    }
    
    for file_path, content in models_content.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fichier créé: {file_path}")
    
    # 3. Vérification des dépendances
    print("\n📦 Vérification des dépendances...")
    try:
        import flask
        import pandas
        print("✅ Flask et pandas sont installés")
    except ImportError:
        print("❌ Certaines dépendances ne sont pas installées")
        print("   Exécutez: pip install -r requirements.txt")
    
    # 4. Instructions pour les données
    print("\n📁 INSTRUCTIONS POUR VOS DONNÉES:")
    print("=" * 40)
    print("1. Placez votre fichier Excel dans le dossier 'data/'")
    print("2. Renommez-le en 'indicateurs_urbains.xlsx'")
    print("3. Ou modifiez le chemin dans app.py (ligne 33)")
    print("\nStructure attendue des colonnes:")
    print("  - Ville")
    print("  - Nom de la Commune")
    print("  - tronçon de voirie")
    print("  - linéaire de voirie(ml)")
    print("  - Nom de la poche du quartier de taudis")
    print("  - superficie de la poche du quartier de taudis")
    print("  - présence du nid de poule")
    print("  - classe de voirie")
    print("  - Nombre de point lumineux sur le tronçon")
    print("  - image_troncon (optionnel)")
    print("  - image_taudis (optionnel)")
    
    # 5. Création du fichier requirements.txt
    requirements = '''flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
openpyxl==3.1.2
scikit-learn==1.3.0
joblib==1.3.2
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
opencv-python-headless==4.8.1.78
'''
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    print(f"✅ Fichier créé: requirements.txt")
    
    # 6. Message final
    print("\n" + "=" * 60)
    print("🎉 CONFIGURATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 60)
    print("\n📋 COMMANDES POUR DÉMARRER:")
    print("1. Installez les dépendances:")
    print("   pip install -r requirements.txt")
    print("\n2. Placez vos données Excel dans: data/indicateurs_urbains.xlsx")
    print("\n3. Lancez l'application:")
    print("   python app.py")
    print("\n4. Ouvrez votre navigateur à: http://127.0.0.1:5000")
    print("\n⚠️  Si vous avez des erreurs:")
    print("   - Vérifiez que vos données sont au bon format")
    print("   - Assurez-vous que toutes les dépendances sont installées")
    print("   - Consultez les logs pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = setup_project()
    sys.exit(0 if success else 1)