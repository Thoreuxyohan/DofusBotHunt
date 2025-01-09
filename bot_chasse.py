import pyautogui
import keyboard
import mouse
import time
import cv2
import numpy as np
from PIL import ImageGrab
import os
import json
from datetime import datetime
import pytesseract
from typing import Optional, Tuple, Dict
from gestionnaire_indices import GestionnaireIndices
from gestionnaire_zaaps import GestionnaireZaaps
from navigateur import NavigateurDofus

class BotChasseDofus:
    def __init__(self):
        self.en_marche = False
        self.touche_pause = 'p'
        self.touche_arret = 'esc'
        self.seuil_confiance = 0.8
        
        # Créer le dossier images s'il n'existe pas
        self.dossier_images = os.path.join(os.path.dirname(__file__), 'images')
        os.makedirs(self.dossier_images, exist_ok=True)
        
        # Initialiser les gestionnaires
        chemin_indices = os.path.join(os.path.dirname(__file__), 'indice_list.json')
        chemin_zaaps = os.path.join(os.path.dirname(__file__), 'zaaps.json')
        self.gestionnaire_indices = GestionnaireIndices(chemin_indices)
        self.gestionnaire_zaaps = GestionnaireZaaps(chemin_zaaps)
        self.navigateur = NavigateurDofus()
        
        # État de la chasse
        self.position_actuelle = None
        self.indice_actuel = None
        self.etape_actuelle = 0
        self.historique_indices = []
    
    def ouvrir_havre_sac(self):
        """Ouvre le havre-sac avec la touche H"""
        keyboard.press_and_release('h')
        time.sleep(1)
    
    def navigation_initiale(self) -> bool:
        """Effectue la séquence de navigation initiale"""
        try:
            # 1. Aller aux Champs de Cania
            if not self.navigateur.aller_champs_cania():
                print("Échec de la navigation vers les Champs de Cania")
                return False
            
            # 2. Aller aux coordonnées du bâtiment de chasse
            self.navigateur.aller_vers_coordonnees(-25, -36)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la navigation initiale: {e}")
            return False
    
    def entrer_commande_travel(self, x: int, y: int):
        """Entre une commande de voyage dans le chat"""
        keyboard.press_and_release('space')
        time.sleep(0.5)
        keyboard.write(f"/travel {x},{y}")
        keyboard.press_and_release('enter')
        time.sleep(2)
    
    def entrer_batiment_chasse(self):
        """Entre dans le bâtiment de chasse"""
        # Cliquer sur la porte
        pos_porte = self.trouver_texte_ocr("Porte")
        if pos_porte:
            self.cliquer_position(pos_porte)
            time.sleep(1)
        
        # Cliquer pour aller à la salle suivante
        # TODO: Ajouter les coordonnées précises du clic
        
        # Cliquer sur le tas de cartes
        pos_cartes = self.trouver_texte_ocr("Tas de cartes")
        if pos_cartes:
            self.cliquer_position(pos_cartes)
            time.sleep(1)
            
        # Cliquer pour lancer la chasse
        pos_lancer = self.trouver_texte_ocr("Lancer")
        if pos_lancer:
            self.cliquer_position(pos_lancer)
            time.sleep(1)
    
    def sortir_batiment(self):
        """Sort du bâtiment de chasse"""
        # Sortir de la salle 2
        pos_sortie = self.trouver_texte_ocr("Sortie")
        if pos_sortie:
            self.cliquer_position(pos_sortie)
            time.sleep(1)
            
        # Sortir du bâtiment
        pos_porte = self.trouver_texte_ocr("Porte")
        if pos_porte:
            self.cliquer_position(pos_porte)
            time.sleep(1)
    
    def lire_coordonnees_depart(self) -> Tuple[int, int]:
        """Lit les coordonnées de départ avec OCR"""
        texte = self.capturer_texte_ocr()
        # Recherche du format "Départ [X,Y]"
        import re
        match = re.search(r"Départ \[(-?\d+),(-?\d+)\]", texte)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None
    
    def aller_vers_coordonnees(self, x: int, y: int):
        """Se déplace vers les coordonnées spécifiées"""
        # Trouver le zaap le plus proche
        zaap_proche = self.gestionnaire_zaaps.trouver_zaap_proche(x, y)
        if not zaap_proche:
            return
            
        # Aller au zaap
        self.ouvrir_havre_sac()
        self.aller_vers_zaap(zaap_proche)
        
        # Se déplacer aux coordonnées finales
        self.entrer_commande_travel(x, y)
    
    def verifier_position_actuelle(self) -> Tuple[int, int]:
        """Vérifie la position actuelle du personnage via OCR"""
        texte = self.capturer_texte_ocr()
        # Recherche des coordonnées dans le format [X,Y]
        import re
        match = re.search(r"\[(-?\d+),(-?\d+)\]", texte)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None
    
    def valider_indice(self):
        """Clique sur le bouton pour valider un indice"""
        pos_valider = self.trouver_texte_ocr("Valider")
        if pos_valider:
            self.cliquer_position(pos_valider)
            time.sleep(1)
    
    def gerer_combat(self):
        """Gère le combat final"""
        pos_combat = self.trouver_texte_ocr("Combat")
        if pos_combat:
            self.cliquer_position(pos_combat)
            # TODO: Implémenter la logique de combat
    
    def trouver_texte_ocr(self, texte: str) -> Optional[Tuple[int, int]]:
        """Trouve la position d'un texte à l'écran via OCR"""
        screenshot = np.array(ImageGrab.grab())
        texte_trouve = pytesseract.image_to_data(
            screenshot,
            output_type=pytesseract.Output.DICT,
            lang='fra'
        )
        
        # Rechercher le texte et retourner ses coordonnées
        for i, mot in enumerate(texte_trouve['text']):
            if texte.lower() in mot.lower():
                x = texte_trouve['left'][i]
                y = texte_trouve['top'][i]
                return (x + texte_trouve['width'][i]//2,
                       y + texte_trouve['height'][i]//2)
        return None
    
    def capturer_texte_ocr(self) -> str:
        """Capture tout le texte visible à l'écran"""
        screenshot = np.array(ImageGrab.grab())
        return pytesseract.image_to_string(screenshot, lang='fra')
    
    def executer(self):
        """Exécute le bot de chasse"""
        print("\nDémarrage du Bot de Chasse Dofus...")
        
        # Trouver et activer la fenêtre Dofus
        if not self.navigateur.trouver_fenetre_dofus():
            print("Impossible de trouver la fenêtre Dofus, arrêt du bot")
            return
            
        # Navigation initiale
        try:
            if not self.navigation_initiale():
                print("Échec de la navigation initiale, arrêt du bot")
                return
        except Exception as e:
            print(f"Erreur lors de la navigation initiale: {str(e)}")
            print("Échec de la navigation initiale, arrêt du bot")
            return
        
        self.en_marche = True
        
        try:
            # Étape 1: Aller au bâtiment de chasse
            self.entrer_commande_travel(-25, -36)
            
            # Étape 2: Entrer dans le bâtiment et lancer la chasse
            self.entrer_batiment_chasse()
            
            # Étape 3: Sortir et lire les coordonnées de départ
            self.sortir_batiment()
            coords_depart = self.lire_coordonnees_depart()
            
            if coords_depart:
                # Étape 4: Aller au point de départ
                self.aller_vers_coordonnees(*coords_depart)
                
                # Étape 5: Gérer les indices
                while self.en_marche:
                    # Vérifier si c'est un combat
                    if self.trouver_texte_ocr("Combat"):
                        self.gerer_combat()
                        break
                    
                    # Lire et traiter l'indice
                    indice = self.lire_indice()
                    if indice:
                        self.indice_actuel = indice
                        self.historique_indices.append(indice)
                        
                        # Se déplacer et valider
                        self.deplacer_position_suivante()
                        self.valider_indice()
                    
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Erreur lors de l'exécution: {e}")
        finally:
            self.sauvegarder_etat()
    
    def sauvegarder_etat(self):
        """Sauvegarde l'état actuel de la chasse"""
        etat = {
            'horodatage': datetime.now().isoformat(),
            'position_actuelle': self.position_actuelle,
            'indice_actuel': self.indice_actuel,
            'etape_actuelle': self.etape_actuelle,
            'historique_indices': self.historique_indices
        }
        
        with open('etat_chasse.json', 'w', encoding='utf-8') as f:
            json.dump(etat, f, indent=2, ensure_ascii=False)

def main():
    bot = BotChasseDofus()
    try:
        bot.executer()
    except KeyboardInterrupt:
        print("\nBot interrompu par l'utilisateur")
    finally:
        bot.sauvegarder_etat()

if __name__ == "__main__":
    main()
