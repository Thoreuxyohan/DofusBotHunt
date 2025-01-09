import keyboard
import mouse
import time
import pyautogui
import pytesseract
from PIL import ImageGrab, Image
import numpy as np
import cv2
from typing import Optional, Tuple, Dict
import json
import os
import pygetwindow as gw
import random
import re

class NavigateurDofus:
    def __init__(self):
        self.delai_entre_actions = 0.5
        self.delai_deplacement = 2.0
        self.fenetre_dofus = None
        self.chemin_images = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
        self.configurer_tesseract()
        
    def configurer_tesseract(self):
        """Configure Tesseract OCR avec le chemin correct"""
        # Chemins possibles pour Tesseract
        chemins_tesseract = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        
        # Chercher Tesseract
        tesseract_path = None
        for chemin in chemins_tesseract:
            if os.path.exists(chemin):
                tesseract_path = chemin
                break
        
        if not tesseract_path:
            raise Exception(
                "Tesseract-OCR n'est pas installé. Veuillez suivre les instructions dans le README.md"
            )
        
        # Configurer le chemin Tesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Configurer TESSDATA_PREFIX
        tessdata_dir = os.path.join(os.path.dirname(tesseract_path), 'tessdata')
        os.environ['TESSDATA_PREFIX'] = tessdata_dir
        
        # Vérifier que les données de langue française sont disponibles
        if not os.path.exists(os.path.join(tessdata_dir, 'fra.traineddata')):
            raise Exception(
                "Les données de langue française ne sont pas installées. "
                "Veuillez suivre les instructions dans le README.md"
            )
            
        # Test rapide de Tesseract
        try:
            pytesseract.get_languages()
        except Exception as e:
            raise Exception(
                f"Erreur lors du test de Tesseract: {str(e)}\n"
                f"TESSDATA_PREFIX est défini à: {os.environ.get('TESSDATA_PREFIX', 'Non défini')}\n"
                "Veuillez vérifier l'installation de Tesseract."
            )
    
    def charger_image_reference(self, nom_image: str) -> Optional[np.ndarray]:
        """Charge une image de référence depuis le dossier images"""
        chemin_image = os.path.join(self.chemin_images, nom_image)
        if not os.path.exists(chemin_image):
            print(f"Image de référence non trouvée: {chemin_image}")
            return None
            
        # Charger l'image avec OpenCV
        return cv2.imread(chemin_image)
    
    def trouver_image(self, image_reference: np.ndarray, seuil: float = 0.8) -> Optional[Tuple[int, int]]:
        """Cherche une image de référence dans la fenêtre Dofus"""
        if not self.fenetre_dofus:
            return None
            
        # Capturer l'écran de jeu
        screenshot = np.array(ImageGrab.grab(bbox=(
            self.fenetre_dofus.left,
            self.fenetre_dofus.top,
            self.fenetre_dofus.right,
            self.fenetre_dofus.bottom
        )))
        
        # Convertir en BGR pour OpenCV
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        # Faire la correspondance de modèle
        resultat = cv2.matchTemplate(screenshot, image_reference, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultat)
        
        if max_val >= seuil:
            # Retourner le centre de la correspondance
            h, w = image_reference.shape[:2]
            return (max_loc[0] + w//2, max_loc[1] + h//2)
            
        return None
    
    def trouver_fenetre_dofus(self):
        """Trouve et active la fenêtre Dofus"""
        if self.fenetre_dofus and self.fenetre_dofus.isMinimized:
            self.fenetre_dofus.restore()
            
        # Si on n'a pas encore la fenêtre, la chercher
        if not self.fenetre_dofus:
            fenetres = gw.getWindowsWithTitle('Yowplays-Ttv')
            for fenetre in fenetres:
                if 'Yowplays-Ttv' in fenetre.title:
                    self.fenetre_dofus = fenetre
                    break
        
        if self.fenetre_dofus:
            self.fenetre_dofus.activate()
            return True
            
        return False
    
    def activer_fenetre(self):
        """Active la fenêtre Dofus"""
        if self.fenetre_dofus:
            try:
                # Restaurer si minimisé
                if self.fenetre_dofus.isMinimized:
                    self.fenetre_dofus.restore()
                
                # Mettre au premier plan
                self.fenetre_dofus.activate()
                time.sleep(0.5)  # Attendre que la fenêtre soit active
                
                # Centrer la souris dans la fenêtre
                center_x = self.fenetre_dofus.left + (self.fenetre_dofus.width // 2)
                center_y = self.fenetre_dofus.top + (self.fenetre_dofus.height // 2)
                mouse.move(center_x, center_y)
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Erreur lors de l'activation de la fenêtre: {e}")
    
    def verifier_fenetre_active(self) -> bool:
        """Vérifie si la fenêtre Dofus est toujours active"""
        if not self.fenetre_dofus:
            return self.trouver_fenetre_dofus()
            
        try:
            fenetre_active = gw.getActiveWindow()
            if fenetre_active != self.fenetre_dofus:
                print("La fenêtre Dofus n'est plus active, réactivation...")
                self.activer_fenetre()
            return True
        except Exception as e:
            print(f"Erreur lors de la vérification de la fenêtre active: {e}")
            return False
    
    def appuyer_touche(self, touche: str):
        """Appuie sur une touche du clavier"""
        if self.verifier_fenetre_active():
            keyboard.press_and_release(touche)
            time.sleep(self.delai_entre_actions)
    
    def cliquer(self, x: int, y: int):
        """Effectue un clic gauche à la position spécifiée"""
        if not self.fenetre_dofus:
            return
            
        # Convertir en coordonnées absolues
        x_abs = self.fenetre_dofus.left + x
        y_abs = self.fenetre_dofus.top + y
        
        # Déplacer la souris
        mouse.move(x_abs, y_abs)
        
        # Ajouter un petit délai aléatoire entre le mouvement et le clic
        time.sleep(0.05 + random.random() * 0.1)
        
        # Presser le bouton gauche
        mouse.press(button='left')
        
        # Ajouter un délai aléatoire pour le maintien du clic
        time.sleep(0.05 + random.random() * 0.1)
        
        # Relâcher le bouton gauche
        mouse.release(button='left')
    
    def capturer_zone(self, x: int, y: int, largeur: int, hauteur: int):
        """Capture une zone spécifique de l'écran"""
        if self.verifier_fenetre_active():
            # Ajuster les coordonnées relatives à la fenêtre
            x_ajuste = x + self.fenetre_dofus.left
            y_ajuste = y + self.fenetre_dofus.top
            return ImageGrab.grab(bbox=(x_ajuste, y_ajuste, 
                                      x_ajuste + largeur, 
                                      y_ajuste + hauteur))
        return None
    
    def trouver_texte(self, zone_image) -> str:
        """Extrait le texte d'une image"""
        return pytesseract.image_to_string(zone_image, lang='fra')
    
    def trouver_element(self, texte: str, zone: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        Trouve un élément contenant le texte spécifié
        
        Args:
            texte: Le texte à rechercher
            zone: (x, y, largeur, hauteur) de la zone de recherche, None pour écran entier
            
        Returns:
            (x, y) du centre de l'élément trouvé, ou None si non trouvé
        """
        if zone:
            screenshot = np.array(self.capturer_zone(*zone))
        else:
            screenshot = np.array(ImageGrab.grab())
            
        # Convertir en niveaux de gris pour meilleure reconnaissance
        gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        
        # Utiliser Tesseract avec HOCR pour obtenir les positions
        hocr = pytesseract.image_to_data(gray, lang='fra', output_type=pytesseract.Output.DICT)
        
        # Chercher le texte
        for i, mot in enumerate(hocr['text']):
            if texte.lower() in mot.lower():
                x = hocr['left'][i] + (hocr['width'][i] // 2)
                y = hocr['top'][i] + (hocr['height'][i] // 2)
                
                # Ajuster les coordonnées si une zone spécifique est utilisée
                if zone:
                    x += zone[0]
                    y += zone[1]
                    
                return (x, y)
        return None
    
    def est_dans_havre_sac(self) -> bool:
        """Vérifie si on est dans le havre-sac en détectant le texte du titre"""
        print("Vérification si dans le havre-sac...")
        
        # Trouver la fenêtre
        if not self.trouver_fenetre_dofus():
            return False
            
        # Zone de capture pour le titre "Havre-sac"
        bbox = (
            self.fenetre_dofus.left + 0,     # X début
            self.fenetre_dofus.top + 40,     # Y début
            self.fenetre_dofus.left + 221,   # X fin
            self.fenetre_dofus.top + 66      # Y fin
        )
        
        # Capturer l'image
        image = np.array(ImageGrab.grab(bbox=bbox))
        
        # Convertir en HSV pour isoler le blanc
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Définir la plage de blanc
        lower_white = np.array([0, 0, 200])  # Très peu saturé, très lumineux
        upper_white = np.array([180, 30, 255])  # Toutes teintes, peu saturé, très lumineux
        
        # Créer un masque pour le blanc
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Redimensionner x4
        scale = 4
        resized = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Débruiter
        denoised = cv2.fastNlMeansDenoising(resized)
        
        # Dilater pour connecter les caractères
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        # Inverser l'image pour avoir du texte noir sur fond blanc
        inverted = cv2.bitwise_not(dilated)
        
        # OCR sur l'image traitée
        texte = pytesseract.image_to_string(
            inverted,
            config='--psm 7 -l fra'
        ).strip().lower()
        
        print(f"Texte détecté: '{texte}'")
        
        # Vérifier si on est dans le havre-sac
        return 'havre' in texte or 'sac' in texte
    
    def ouvrir_havre_sac(self) -> bool:
        """Ouvre le havre-sac s'il n'est pas déjà ouvert"""
        if not self.trouver_fenetre_dofus():
            print("Impossible de trouver la fenêtre Dofus")
            return False
        
        print("Vérification si déjà dans le havre-sac...")
        if self.est_dans_havre_sac():
            print("Déjà dans le havre-sac, pas besoin d'appuyer sur H")
            return True
        
        print("Pas dans le havre-sac, appui sur H...")
        self.appuyer_touche('h')
        
        # Attendre un peu que l'interface s'ouvre
        time.sleep(1.0)
        
        # Vérifier que l'ouverture a réussi
        for _ in range(3):  # Faire 3 tentatives
            if self.est_dans_havre_sac():
                print("Havre-sac ouvert avec succès")
                return True
            time.sleep(0.5)  # Attendre entre les tentatives
        
        print("Échec de l'ouverture du havre-sac après 3 tentatives")
        return False
    
    def cliquer_zaap(self) -> bool:
        """Clique sur le zaap dans le havre-sac avec une position aléatoire"""
        print("\nClic sur le zaap...")
        
        # Position de base du zaap
        base_x, base_y = 722, 561
        
        # Ajouter une variation aléatoire de ±20 pixels
        variation = 20
        x = base_x + random.randint(-variation, variation)
        y = base_y + random.randint(-variation, variation)
        
        print(f"Clic à la position: ({x}, {y})")
        
        # Ajouter un délai aléatoire avant le clic (entre 0.1 et 0.3 secondes)
        time.sleep(0.1 + random.random() * 0.2)
        
        # Cliquer à la position calculée
        self.cliquer(x, y)
        
        # Ajouter un délai aléatoire après le clic
        time.sleep(self.delai_entre_actions + random.random() * 0.5)
        
        return True
    
    def aller_champs_cania(self) -> bool:
        """Va aux champs de Cania en utilisant le zaap"""
        print("\nNavigation vers les Champs de Cania...")
        
        # 1. Si non, vérifier si on est dans le havre-sac
        if not self.est_dans_havre_sac():
            print("Pas dans le havre-sac, ouverture...")
            if not self.ouvrir_havre_sac():
                print("Impossible d'ouvrir le havre-sac")
                return False
        
        # 2. Cliquer sur le zaap
        if not self.cliquer_zaap():
            print("Impossible de cliquer sur le zaap")
            return False
        
        # 3. Chercher et cliquer sur Champs de Cania
        if not self.chercher_zaap("Champs de Cania"):
            print("Impossible de trouver Champs de Cania")
            return False
        
        # 4. Une fois téléporté, aller à la destination finale
        print("Téléportation vers la destination finale...")
        self.entrer_commande_chat("/travel -25,-36")
        time.sleep(5.0)  # Attendre plus longtemps avant de commencer les vérifications
        
        # 5. Vérifier qu'on est bien arrivé aux bonnes coordonnées
        max_tentatives = 5  # Augmenter le nombre de tentatives
        for tentative in range(max_tentatives):
            if self.est_a_position(-25, -36):
                print("Arrivé à la bonne position")
                time.sleep(2.0)  # Attendre un peu avant de commencer la séquence
                # 6. Lancer la séquence de récupération de la chasse et terminer
                self.recuperer_chasse()
                break  # Sortir de la boucle sans lancer d'autres actions
            else:
                if tentative < max_tentatives - 1:
                    print(f"Position incorrecte, tentative {tentative + 1}/{max_tentatives}")
                    time.sleep(2.0)
                
        return True
    
    def chercher_zaap(self, nom_zaap: str):
        """Cherche un zaap spécifique dans la liste"""
        print(f"Recherche du zaap '{nom_zaap}'...")
        # Attendre que l'interface de recherche soit visible
        time.sleep(self.delai_entre_actions)
        
        # Effacer le champ de recherche existant
        keyboard.press_and_release('ctrl+a')
        time.sleep(0.1)
        keyboard.press_and_release('backspace')
        time.sleep(0.1)
        
        # Saisir le nom du zaap
        keyboard.write(nom_zaap)
        time.sleep(self.delai_entre_actions)
        
        # Cliquer sur le zaap dans la liste (coordonnées relatives)
        print("Clic sur le zaap dans la liste...")
        zaap_x = 350  # Position horizontale du zaap dans la liste
        zaap_y = 350  # Position verticale du premier zaap dans la liste
        
        # Ajouter une variation aléatoire
        variation = 10
        x = zaap_x + random.randint(-variation, variation)
        y = zaap_y + random.randint(-variation, variation)
        
        self.cliquer(x, y)
        time.sleep(0.5)  # Attendre que le zaap soit sélectionné
        
        # Appuyer sur Entrée au lieu de cliquer sur le bouton SE TÉLÉPORTER
        print("Appui sur Entrée pour se téléporter...")
        keyboard.press_and_release('enter')
        
        # Attendre la téléportation
        print("Téléportation en cours...")
        time.sleep(self.delai_deplacement)
        return True
    
    def cliquer_se_teleporter(self) -> bool:
        """Clique sur le bouton Se téléporter avec une position aléatoire"""
        print("\nRecherche du bouton Se téléporter...")
        
        # Position de base du bouton (à ajuster selon vos besoins)
        base_x, base_y = 722, 561  # Ces coordonnées sont à remplacer par les bonnes
        
        # Ajouter une variation aléatoire de ±10 pixels
        variation = 10
        x = base_x + random.randint(-variation, variation)
        y = base_y + random.randint(-variation, variation)
        
        print(f"Clic à la position: ({x}, {y})")
        
        # Ajouter un délai aléatoire avant le clic (entre 0.1 et 0.3 secondes)
        time.sleep(0.1 + random.random() * 0.2)
        
        # Cliquer à la position calculée
        self.cliquer(x, y)
        
        # Ajouter un délai aléatoire après le clic
        time.sleep(self.delai_entre_actions + random.random() * 0.5)
        
        return True

    def cliquer_porte_tresor(self):
        """Clique sur la porte du trésor avec une position aléatoire"""
        print("\nClic sur la porte du trésor...")
        
        # Position de base de la porte
        base_x, base_y = 1254, 637
        
        # Ajouter une variation aléatoire de ±15 pixels
        variation = 15
        x = base_x + random.randint(-variation, variation)
        y = base_y + random.randint(-variation, variation)
        
        print(f"Clic à la position: ({x}, {y})")
        
        # Ajouter un délai aléatoire avant le clic (entre 0.1 et 0.3 secondes)
        time.sleep(0.1 + random.random() * 0.2)
        
        # Cliquer à la position calculée
        self.cliquer(x, y)
        
        # Ajouter un délai aléatoire après le clic
        time.sleep(self.delai_entre_actions + random.random() * 0.5)
        
        return True

    def aller_vers_coordonnees(self, x: int, y: int):
        """Va aux coordonnées spécifiées via la commande /travel"""
        commande = f"/travel {x},{y}"
        self.entrer_commande_chat(commande)
        time.sleep(self.delai_deplacement)  # Attendre la fin du déplacement

    def recuperer_position(self, fenetre):
        """Récupère la position actuelle sur la carte"""
        # Zone des coordonnées
        bbox = (
            fenetre.left + 5,    # X début
            fenetre.top + 73,    # Y début
            fenetre.left + 88,   # X fin
            fenetre.top + 96     # Y fin
        )
        
        # Capturer l'image
        image = np.array(ImageGrab.grab(bbox=bbox))
        
        # Convertir en HSV pour isoler le blanc
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Définir la plage de blanc
        lower_white = np.array([0, 0, 200])  # Très peu saturé, très lumineux
        upper_white = np.array([180, 30, 255])  # Toutes teintes, peu saturé, très lumineux
        
        # Créer un masque pour le blanc
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Redimensionner x4
        scale = 4
        resized = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Débruiter
        denoised = cv2.fastNlMeansDenoising(resized)
        
        # Dilater pour connecter les caractères
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        # Inverser l'image pour avoir du texte noir sur fond blanc
        inverted = cv2.bitwise_not(dilated)
        
        # OCR sur l'image traitée
        texte = pytesseract.image_to_string(
            inverted,
            config='--psm 7 -c tessedit_char_whitelist=0123456789,- -l eng'
        ).strip()
        
        # Extraire les coordonnées
        try:
            chiffres = re.findall(r'-?\d+', texte)
            if len(chiffres) >= 2:
                x = int(chiffres[0])
                y = int(chiffres[1])
                return x, y
        except Exception as e:
            print(f"Erreur lors de la lecture des coordonnées: {e}")
        
        return None
    
    def est_a_position(self, x: int, y: int) -> bool:
        """Vérifie si le personnage est à la position donnée en lisant les coordonnées en haut à gauche"""
        print(f"Vérification si à la position [{x},{y}]...")
        
        # Capturer la zone des coordonnées
        zone_coords = np.array(ImageGrab.grab(bbox=(
            self.fenetre_dofus.left + 0,    # X début
            self.fenetre_dofus.top + 72,    # Y début
            self.fenetre_dofus.left + 88,   # X fin
            self.fenetre_dofus.top + 93     # Y fin
        )))
        
        # Convertir en HSV pour isoler le blanc
        hsv = cv2.cvtColor(zone_coords, cv2.COLOR_RGB2HSV)
        
        # Définir la plage de blanc
        lower_white = np.array([0, 0, 200])  # Très peu saturé, très lumineux
        upper_white = np.array([180, 30, 255])  # Toutes teintes, peu saturé, très lumineux
        
        # Créer un masque pour le blanc
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Redimensionner x4
        scale = 4
        resized = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Débruiter
        denoised = cv2.fastNlMeansDenoising(resized)
        
        # Dilater pour connecter les caractères
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        # Inverser l'image pour avoir du texte noir sur fond blanc
        inverted = cv2.bitwise_not(dilated)
        
        # OCR sur l'image traitée
        texte = pytesseract.image_to_string(
            inverted,
            config='--psm 7 -c tessedit_char_whitelist=0123456789,- -l fra'
        ).strip()
        
        print(f"Texte détecté: '{texte}'")
        
        # Vérifier si le texte correspond aux coordonnées attendues
        coords_attendues = f"{x},{y}"
        trouve = texte == coords_attendues
        print(f"Position [{x},{y}]: {'trouvée' if trouve else 'non trouvée'}")
        
        return trouve
    
    def entrer_commande_chat(self, commande: str):
        """Entre une commande dans le chat"""
        print(f"Entrée de la commande: {commande}")
        # Attendre avant d'ouvrir le chat
        time.sleep(0.5)
        keyboard.press_and_release('space')
        time.sleep(0.5)  # Attendre que le chat s'ouvre
        keyboard.write(commande)
        time.sleep(0.5)  # Attendre après avoir écrit la commande
        keyboard.press_and_release('enter')
        
        # Si c'est une commande /travel, appuyer une deuxième fois sur Entrée
        if commande.startswith('/travel'):
            time.sleep(0.5)  # Attendre un peu entre les deux appuis
            keyboard.press_and_release('enter')
            
        time.sleep(0.5)  # Attendre après avoir validé

    def cliquer_position_aleatoire(self, positions):
        """Clique sur une position aléatoire parmi une liste de positions"""
        position = random.choice(positions)
        x, y = position
        # Ajouter une variation aléatoire de ±5 pixels
        variation = 5
        x += random.randint(-variation, variation)
        y += random.randint(-variation, variation)
        self.cliquer(x, y)

    def recuperer_chasse(self):
        """Séquence complète pour récupérer la chasse"""
        print("\nDébut de la séquence de récupération de la chasse...")
        
        # 1. Clic sur la porte pour rentrer (avec variation)
        print("Clic sur la porte pour rentrer...")
        x, y = 1231, 628
        variation = 5
        x += random.randint(-variation, variation)
        y += random.randint(-variation, variation)
        self.cliquer(x, y)
        time.sleep(8.0)  # Attendre le déplacement
        
        # 2. Passer dans la salle 2 (sans variation)
        print("Passage dans la salle 2...")
        self.cliquer(1984, 638)
        time.sleep(4.0)
        
        # 3. Sélectionner le niveau de la chasse (avec variation)
        print("Sélection du niveau de la chasse...")
        x, y = 1386, 641
        variation = 5
        x += random.randint(-variation, variation)
        y += random.randint(-variation, variation)
        self.cliquer(x, y)
        time.sleep(4.0)
        
        # 4. Cliquer sur la chasse (sans variation)
        print("Clic sur la chasse...")
        self.cliquer(1525, 681)
        time.sleep(8.0)
        
        # 5. Retour à la salle 1 (sans variation)
        print("Retour à la salle 1...")
        self.cliquer(444, 1165)
        time.sleep(8.0)
        
        # 6. Cliquer sur la porte pour sortir de la malle (avec variation)
        print("Sortie de la malle...")
        x, y = 587, 1086
        variation = 5
        x += random.randint(-variation, variation)
        y += random.randint(-variation, variation)
        self.cliquer(x, y)
        
        print("Fin de l'étape 1 - Sortie de la malle au trésor")
        return True
