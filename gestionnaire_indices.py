import json
from typing import Dict, Optional, Tuple
import os

class GestionnaireIndices:
    def __init__(self, chemin_fichier: str):
        """
        Initialise le gestionnaire d'indices
        
        Args:
            chemin_fichier (str): Chemin vers le fichier contenant les indices et positions
        """
        self.chemin_fichier = chemin_fichier
        self.indices: Dict[int, dict] = {}
        self.indices_par_nom: Dict[str, int] = {}
        self.charger_indices()
    
    def charger_indices(self):
        """Charge les indices depuis le fichier JSON"""
        try:
            with open(self.chemin_fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Charger tous les indices
            for indice in data.get('clues', []):
                id_indice = indice.get('clue-id')
                if id_indice:
                    self.indices[id_indice] = indice
                    # Indexer par nom français pour une recherche rapide
                    nom_fr = indice.get('name-fr', '').lower()
                    if nom_fr:
                        self.indices_par_nom[nom_fr] = id_indice
                        
            print(f"Chargé {len(self.indices)} indices depuis le fichier")
        except Exception as e:
            print(f"Erreur lors du chargement des indices: {e}")
            
    def obtenir_indice_par_id(self, id_indice: int) -> Optional[dict]:
        """
        Obtient les informations d'un indice par son ID
        
        Args:
            id_indice (int): L'ID de l'indice à rechercher
            
        Returns:
            dict: Les informations de l'indice ou None si non trouvé
        """
        return self.indices.get(id_indice)
    
    def obtenir_indice_par_nom(self, nom: str) -> Optional[dict]:
        """
        Obtient les informations d'un indice par son nom français
        
        Args:
            nom (str): Le nom de l'indice en français
            
        Returns:
            dict: Les informations de l'indice ou None si non trouvé
        """
        id_indice = self.indices_par_nom.get(nom.lower())
        if id_indice:
            return self.indices[id_indice]
        return None
    
    def verifier_indice(self, texte: str) -> Optional[dict]:
        """
        Vérifie si un texte correspond à un indice connu
        
        Args:
            texte (str): Le texte à vérifier
            
        Returns:
            dict: Les informations de l'indice correspondant ou None si aucune correspondance
        """
        texte = texte.lower()
        # Recherche exacte
        if texte in self.indices_par_nom:
            return self.indices[self.indices_par_nom[texte]]
            
        # Recherche partielle
        for nom, id_indice in self.indices_par_nom.items():
            if texte in nom or nom in texte:
                return self.indices[id_indice]
        
        return None
