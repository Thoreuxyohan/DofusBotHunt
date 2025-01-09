import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw
import time
import os
import pytesseract

def configurer_tesseract():
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

def trouver_fenetre_dofus():
    """Trouve la fenêtre Dofus"""
    # Chercher la fenêtre qui contient le titre
    fenetres = gw.getWindowsWithTitle('Yowplays-Ttv')
    for fenetre in fenetres:
        if 'Yowplays-Ttv' in fenetre.title:
            print(f"Fenêtre trouvée: {fenetre.title}")
            return fenetre
    return None

def charger_image_reference(nom_image: str):
    """Charge une image de référence depuis le dossier images"""
    chemin_images = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    chemin_complet = os.path.join(chemin_images, nom_image)
    
    if not os.path.exists(chemin_complet):
        print(f"Image de référence non trouvée: {chemin_complet}")
        return None
        
    return cv2.imread(chemin_complet)

def test_detection_havre_sac():
    """Test la détection du havre-sac"""
    # Configurer Tesseract
    configurer_tesseract()
    
    # Trouver la fenêtre
    fenetre = trouver_fenetre_dofus()
    if not fenetre:
        print("Fenêtre Dofus non trouvée")
        return
        
    print(f"Fenêtre trouvée: {fenetre.title}")
    print(f"Position: ({fenetre.left}, {fenetre.top}) - ({fenetre.right}, {fenetre.bottom})")
    
    # Zone de capture pour le titre "Havre-sac"
    bbox = (
        fenetre.left + 0,     # X début
        fenetre.top + 40,     # Y début
        fenetre.left + 221,   # X fin
        fenetre.top + 66      # Y fin
    )
    
    # Capturer l'image
    image = np.array(ImageGrab.grab(bbox=bbox))
    
    # Sauvegarder l'image originale
    cv2.imwrite('test_havre_original.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    
    # Convertir en HSV pour isoler le blanc
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Définir la plage de blanc
    lower_white = np.array([0, 0, 200])  # Très peu saturé, très lumineux
    upper_white = np.array([180, 30, 255])  # Toutes teintes, peu saturé, très lumineux
    
    # Créer un masque pour le blanc
    mask = cv2.inRange(hsv, lower_white, upper_white)
    cv2.imwrite('test_havre_mask.png', mask)
    
    # Redimensionner x4
    scale = 4
    resized = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite('test_havre_resized.png', resized)
    
    # Débruiter
    denoised = cv2.fastNlMeansDenoising(resized)
    cv2.imwrite('test_havre_denoised.png', denoised)
    
    # Dilater pour connecter les caractères
    kernel = np.ones((2,2), np.uint8)
    dilated = cv2.dilate(denoised, kernel, iterations=1)
    cv2.imwrite('test_havre_dilated.png', dilated)
    
    # Inverser l'image pour avoir du texte noir sur fond blanc
    inverted = cv2.bitwise_not(dilated)
    cv2.imwrite('test_havre_inverted.png', inverted)
    
    # OCR sur l'image traitée
    texte = pytesseract.image_to_string(
        inverted,
        config='--psm 7 -l fra'
    ).strip().lower()
    
    print(f"\nTexte détecté: '{texte}'")
    
    # Vérifier si on est dans le havre-sac
    if 'havre' in texte or 'sac' in texte:
        print("On est dans le havre-sac!")
    else:
        print("On n'est pas dans le havre-sac")

if __name__ == "__main__":
    test_detection_havre_sac()
