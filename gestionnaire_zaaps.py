import json
import math
from typing import Dict, List, Tuple, Optional

class GestionnaireZaaps:
    def __init__(self, chemin_fichier: str):
        self.chemin_fichier = chemin_fichier
        self.zaaps: List[Dict] = []
        self.charger_zaaps()
    
    def charger_zaaps(self):
        """Charge la liste des zaaps depuis le fichier JSON"""
        try:
            with open(self.chemin_fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.zaaps = data.get('zaaps', [])
        except Exception as e:
            print(f"Erreur lors du chargement des zaaps: {e}")
    
    def trouver_zaap_proche(self, x: int, y: int) -> Optional[Dict]:
        """
        Trouve le zaap le plus proche des coordonnées données
        
        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
            
        Returns:
            Dict: Information du zaap le plus proche
        """
        if not self.zaaps:
            return None
            
        zaap_proche = min(
            self.zaaps,
            key=lambda z: math.sqrt(
                (z['coordonnees'][0] - x) ** 2 +
                (z['coordonnees'][1] - y) ** 2
            )
        )
        return zaap_proche
