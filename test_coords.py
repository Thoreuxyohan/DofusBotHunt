import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract
import pygetwindow as gw
import time
import os
import re

def trouver_fenetre_dofus():
    """Trouve la fenêtre Dofus"""
    fenetres_dofus = [w for w in gw.getAllWindows() if w.title.startswith("Yowplays-Ttv")]
    return fenetres_dofus[0] if fenetres_dofus else None

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
            "Tesseract-OCR n'est pas installé. Veuillez l'installer depuis : "
            "https://github.com/UB-Mannheim/tesseract/wiki"
        )
    
    # Configurer le chemin Tesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # Configurer TESSDATA_PREFIX
    tessdata_dir = os.path.join(os.path.dirname(tesseract_path), 'tessdata')
    os.environ['TESSDATA_PREFIX'] = tessdata_dir
    
    print(f"Tesseract configuré :")
    print(f"- Chemin : {tesseract_path}")
    print(f"- Données : {tessdata_dir}")

def test_detection_coords():
    """Test la détection des coordonnées"""
    # Configurer Tesseract
    configurer_tesseract()
    
    # Trouver la fenêtre
    fenetre = trouver_fenetre_dofus()
    if not fenetre:
        print("Fenêtre Dofus non trouvée")
        return
        
    print(f"Fenêtre trouvée: {fenetre.title}")
    print(f"Position: ({fenetre.left}, {fenetre.top}) - ({fenetre.right}, {fenetre.bottom})")
    
    # Zone exacte des coordonnées
    x1, y1 = 5, 73
    x2, y2 = 88, 96
    print(f"\nZone de capture: ({x1}, {y1}) - ({x2}, {y2})")
    
    # Capturer l'image
    bbox = (
        fenetre.left + x1,
        fenetre.top + y1,
        fenetre.left + x2,
        fenetre.top + y2
    )
    image = np.array(ImageGrab.grab(bbox=bbox))
    
    # Sauvegarder l'image originale
    cv2.imwrite('test_coords_original.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    
    # Convertir en HSV pour mieux isoler le blanc
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Définir la plage de blanc
    lower_white = np.array([0, 0, 200])  # Très peu saturé, très lumineux
    upper_white = np.array([180, 30, 255])  # Toutes teintes, peu saturé, très lumineux
    
    # Créer un masque pour le blanc
    mask = cv2.inRange(hsv, lower_white, upper_white)
    cv2.imwrite('test_coords_mask.png', mask)
    
    # Redimensionner x4
    scale = 4
    resized = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite('test_coords_resized.png', resized)
    
    # Débruiter
    denoised = cv2.fastNlMeansDenoising(resized)
    cv2.imwrite('test_coords_denoised.png', denoised)
    
    # Dilater pour connecter les caractères
    kernel = np.ones((2,2), np.uint8)
    dilated = cv2.dilate(denoised, kernel, iterations=1)
    cv2.imwrite('test_coords_dilated.png', dilated)
    
    # Inverser l'image pour avoir du texte noir sur fond blanc (meilleur pour Tesseract)
    inverted = cv2.bitwise_not(dilated)
    cv2.imwrite('test_coords_inverted.png', inverted)
    
    # Test OCR sur les différentes versions
    print("\nTest OCR sur différentes versions:")
    
    # Sur le masque original
    texte = pytesseract.image_to_string(
        mask,
        config='--psm 7 -c tessedit_char_whitelist=0123456789,- -l eng'
    ).strip()
    print(f"1. Masque original: '{texte}'")
    
    # Sur l'image inversée finale
    texte = pytesseract.image_to_string(
        inverted,
        config='--psm 7 -c tessedit_char_whitelist=0123456789,- -l eng'
    ).strip()
    print(f"2. Image traitée: '{texte}'")
    
    # Essayer de reconstruire les coordonnées
    try:
        chiffres = re.findall(r'-?\d+', texte)
        if len(chiffres) >= 2:
            x = int(chiffres[0])
            y = int(chiffres[1])
            coords = f"{x},{y}"
            print(f"\nCoordonnées reconstruites: {coords}")
    except Exception as e:
        print(f"Erreur lors de la reconstruction: {e}")

if __name__ == "__main__":
    test_detection_coords()
