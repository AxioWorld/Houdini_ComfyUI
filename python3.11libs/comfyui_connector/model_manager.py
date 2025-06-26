# comfyui_connector/model_manager.py
import os
import sys
import urllib
import hou # type: ignore
import re
from hutil.Qt import QtCore, Qt, QtWidgets # type: ignore

class ComfyUIModelManager:
    def __init__(self):
        self.comfyui_path = hou.expandString("$HCOMFYUI_COMFYUI")
        self.model_directories = {
            "checkpoints": os.path.join(self.comfyui_path, "models", "checkpoints"),
            "vae": os.path.join(self.comfyui_path, "models", "vae"),
            "clip": os.path.join(self.comfyui_path, "models", "clip"),
            "upscale_models": os.path.join(self.comfyui_path, "models", "upscale_models"),
            "loras": os.path.join(self.comfyui_path, "models", "loras"),
            "controlnet": os.path.join(self.comfyui_path, "models", "controlnet"),
            "unet": os.path.join(self.comfyui_path, "models", "unet"),
            # Ajoutez d'autres chemins de modèles si nécessaire
        }

    def list_models(self, model_type="checkpoints"):
        if model_type in self.model_directories:
            directory = self.model_directories[model_type]
            try:
                return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            except FileNotFoundError:
                print(f"Erreur: Le répertoire pour '{model_type}' n'a pas été trouvé.")
                return []
        else:
            print(f"Type de modèle '{model_type}' non reconnu.")
            return []

    def list_to_menu(self,list):
        menu = []

        for i in range(len(list)):
            index = str(i)
            item = list[i]
            menu.append(index)
            menu.append(item)

        return menu

    def get_model_path(self, model_name, model_type="checkpoints"):
        if model_type in self.model_directories:
            directory = self.model_directories[model_type]
            filepath = os.path.join(directory, model_name)
            if os.path.exists(filepath):
                return filepath
            else:
                print(f"Modèle '{model_name}' non trouvé dans '{directory}'.")
                return None
        else:
            print(f"Type de modèle '{model_type}' non reconnu.")
            return None

    def download_file(self, url, destination, description):
        """Télécharge un fichier avec une barre de progression simple."""
        
        try:
            # Créer le répertoire de destination s'il n'existe pas
            os.makedirs(os.path.dirname(destination), exist_ok=True)       
            # Fonction pour afficher la progression
            def report_progress(count, block_size, total_size):
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\rTéléchargement: {percent}% [{count * block_size}/{total_size} octets]")
                sys.stdout.flush()
            
            """ TO DO DOWNLOAD BAR
            with hou.InterruptableOperation(
                "Downloading Models", open_interrupt_dialog=True
            ) as operation:

                # Trying to download get-pip with curl , this can quietly fail when behind proxy
                hou.ui.setStatusMessage("download")
            """

            # Télécharger le fichier
            urllib.request.urlretrieve(url, destination, reporthook=report_progress)
            print(f"\nTéléchargement de {description} terminé.")
            return True
        except Exception as e:
            print(f"\nErreur lors du téléchargement de {description}: {e}")
            return False

                    
    def download_models(self, url, type="checkpoint"):
        """Configure les dossiers pour les modèles et télécharge les modèles sélectionnés."""
        # Créer les dossiers nécessaires
        models_dir = os.path.join(self.comfyui_path, "models")
        install_dir = os.path.join(models_dir, type)

        os.makedirs(install_dir, exist_ok=True)
        
        # Download
        model_name = url.split("/")[-1]
        model_path = os.path.join(install_dir, model_name)
        if os.path.exists(model_path):
            print(f"Model {model_name} already exist in: {model_path}")
        else:
            success = self.download_file(url, model_path, model_name)
            if success:
                print(f"Model {model_name} download in: {model_path}")
            else:
                print("Failed download for {model_name}")

         