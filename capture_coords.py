import keyboard
import pygetwindow as gw
import time
import pyautogui
import sys

def main():
    print("Utilitaire de capture de coordonnées pour Dofus")
    print("\nInstructions:")
    print("1. Assurez-vous que votre fenêtre Dofus est ouverte")
    print("2. Vous avez 3 secondes pour placer votre souris à l'endroit voulu")
    print("3. Appuyez sur 'C' pour capturer les coordonnées")
    print("4. Appuyez sur 'Echap' pour quitter")
    
    while True:
        if keyboard.is_pressed('esc'):
            print("\nFin du programme")
            break
            
        if keyboard.is_pressed('c'):
            # Attendre que la touche soit relâchée
            while keyboard.is_pressed('c'):
                time.sleep(0.1)
            
            # Trouver la fenêtre Dofus
            fenetres_dofus = [w for w in gw.getAllWindows() if w.title.startswith("Yowplays-Ttv")]
            if not fenetres_dofus:
                print("Aucune fenêtre Dofus trouvée!")
                continue
                
            fenetre = fenetres_dofus[0]
            
            # Obtenir la position de la souris
            x, y = pyautogui.position()
            
            # Calculer les coordonnées relatives à la fenêtre
            x_rel = x - fenetre.left
            y_rel = y - fenetre.top
            
            print(f"\nPosition relative à la fenêtre Dofus:")
            print(f"X: {x_rel}")
            print(f"Y: {y_rel}")
            
            # Petite pause pour éviter les captures multiples
            time.sleep(0.5)
        
        time.sleep(0.1)  # Réduire l'utilisation CPU

if __name__ == "__main__":
    main()