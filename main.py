from navigateur import NavigateurDofus
from bot_chasse import BotChasseDofus
import time
import tkinter as tk
from threading import Thread
import sys

class Main:
    def __init__(self):
        self.navigateur = NavigateurDofus()
        self.bot = BotChasseDofus(self.navigateur)
        self.running = False
        
        # Création de l'interface
        self.root = tk.Tk()
        self.root.title("Bot Chasse Dofus")
        self.root.geometry("300x150")
        
        # Boutons
        self.start_button = tk.Button(self.root, text="Démarrer", command=self.start_bot)
        self.start_button.pack(pady=20)
        
        self.stop_button = tk.Button(self.root, text="Arrêter", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(self.root, text="Bot arrêté")
        self.status_label.pack(pady=10)

    def start_bot(self):
        """Démarre le bot dans un thread séparé"""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Bot en cours d'exécution")
        Thread(target=self.demarrer, daemon=True).start()

    def stop_bot(self):
        """Arrête le bot"""
        print("\nArrêt du bot demandé...")
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Bot arrêté")
        
        # Forcer l'arrêt de la vérification de position
        if hasattr(self.bot.navigateur, 'continuer_verification'):
            self.bot.navigateur.continuer_verification = False

    def demarrer(self):
        """Démarre le bot de chasse"""
        print("Démarrage du bot de chasse...")
        while self.running:
            try:
                # Étape 1 : Vérifier si une chasse est en cours
                if not self.bot.verifier_chasse_en_cours():
                    print("Aucune chasse en cours, début de l'étape 1...")
                    # Aller récupérer une chasse
                    self.bot.ouvrir_havre_sac()
                    self.bot.navigation_initiale()
                    self.bot.entrer_commande_travel(-25, -36)
                    time.sleep(2)  # Attendre d'arriver à destination
                    
                    # Vérifier à nouveau après l'étape 1
                    if self.bot.verifier_chasse_en_cours():
                        print("Chasse récupérée avec succès, passage à l'étape 2...")
                    else:
                        print("Échec de la récupération de la chasse, nouvelle tentative...")
                        continue
                
                # Étape 2 : La chasse est en cours, commencer la résolution
                print("Début de l'étape 2...")
                coords = self.bot.navigateur.lire_coordonnees_chasse()
                if coords and coords[0] is not None and coords[1] is not None:
                    x, y = coords
                    print(f"Coordonnées trouvées : [{x}, {y}]")
                    zaap_proche = self.bot.navigateur.trouver_zaap_proche(x, y)
                    if zaap_proche:
                        print(f"Zaap le plus proche trouvé : {zaap_proche}")
                        self.bot.ouvrir_havre_sac()
                        if self.bot.navigateur.se_teleporter(zaap_proche):
                            print("Téléportation réussie, vérification de la position...")
                            if self.bot.navigateur.verification_pos_demarrage_chasse(x, y):
                                print("Position vérifiée, arrêt du bot...")
                                self.running = False
                                return
                            else:
                                print("Échec de la vérification de position, nouvelle tentative...")
                        else:
                            print("Échec de la téléportation, nouvelle tentative...")
                    else:
                        print("Aucun zaap proche trouvé")
                else:
                    print("Impossible de lire les coordonnées de la chasse")
                
                time.sleep(1)  # Petit délai entre les itérations
                
            except Exception as e:
                print(f"Erreur : {e}")
                time.sleep(1)  # Attendre en cas d'erreur

    def run(self):
        """Lance l'interface graphique"""
        self.root.mainloop()

if __name__ == '__main__':
    main = Main()
    main.run()
