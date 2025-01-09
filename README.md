# Bot de Chasse Dofus

Bot automatisé pour la chasse au trésor dans Dofus.

## Prérequis

1. Python 3.8 ou supérieur
2. Tesseract OCR avec support français

### Installation de Tesseract OCR

1. Téléchargez Tesseract OCR pour Windows :
   - Allez sur [la page UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Téléchargez la dernière version 64-bit
   - Installez en gardant le chemin par défaut (`C:\Program Files\Tesseract-OCR`)
   - **Important** : Cochez l'option pour installer les données de langue française pendant l'installation

2. Vérifiez que ces fichiers existent :
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - `C:\Program Files\Tesseract-OCR\tessdata\fra.traineddata`

Si les données françaises ne sont pas installées :
1. Téléchargez [fra.traineddata](https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata)
2. Placez le fichier dans `C:\Program Files\Tesseract-OCR\tessdata\`

## Installation des dépendances Python

```bash
pip install -r requirements.txt
```

## Configuration

1. Assurez-vous que la fenêtre Dofus est visible et non minimisée
2. Le titre de la fenêtre doit commencer par "Yowplays-Ttv"

## Utilisation

```bash
python main.py
```

## Fonctionnalités

- Navigation automatique vers les points de chasse
- Détection OCR des indices
- Gestion des combats
- Suivi des étapes de chasse

## Dépannage

Si vous avez des erreurs liées à Tesseract :
1. Vérifiez que Tesseract est installé dans `C:\Program Files\Tesseract-OCR\`
2. Vérifiez que les données françaises sont présentes dans le dossier `tessdata`
3. Réinstallez Tesseract en cochant l'option pour les données françaises
