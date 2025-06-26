#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script d'installation automatisée pour ComfyUI avec Python 3.11
Ce script permet d'installer ComfyUI avec ses dépendances dans un environnement virtuel Python 3.11,
avec support pour différentes plateformes et configuration personnalisable.

python comfyui_installer_python311 --install-dir "./comfyui_install" --port 8188 --cuda-version 11.8 --method zip

"""
import argparse
import os
import platform
import subprocess
import sys
import shutil
import zipfile
import urllib.request
import time
import venv


# Configuration par défaut
DEFAULT_PORT = 8188
DEFAULT_CUDA_VERSION = "11.8"
DEFAULT_INSTALL_MODELS = False
DEFAULT_INSTALL_METHOD = "git"  # zip ou git
DEFAULT_DOWNLOAD_SD15 = False
DEFAULT_DOWNLOAD_VAE = False
COMFYUI_REPO_URL = "https://github.com/comfyanonymous/ComfyUI.git"
COMFYUI_ZIP_URL = "https://github.com/comfyanonymous/ComfyUI/archive/refs/heads/master.zip"
COMFYUI_MANAGER_REPO_URL = "https://github.com/ltdrdata/ComfyUI-Manager.git"
COMFYUI_MANAGER_ZIP_URL = "https://github.com/ltdrdata/ComfyUI-Manager/archive/refs/heads/main.zip"


def get_platform():
    """Détecte la plateforme et retourne le système d'exploitation."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"
    

def create_venv(install_dir, python_path=None):
    """Crée un environnement virtuel Python dans le répertoire spécifié."""
    venv_path = os.path.join(install_dir, "venv")
    print(f"Création de l'environnement virtuel Python dans {venv_path}...")

    if not python_path:
        # Ensure a python_path is provided
        print(f"Erreur: Le chemin vers l'exécutable Python n'est pas spécifié.")
        sys.exit(1) # Exit if no python_path is provided

    try:
        print(f"DEBUG: python_path passed to create_venv: '{python_path}'")
        subprocess.run([python_path, "-m", "venv", venv_path], check=True)
        print("Environnement virtuel Python  créé avec succès.")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la création de l'environnement virtuel: {e}")
        sys.exit(1)


def get_python_executable(venv_path):
    """Retourne le chemin vers l'exécutable Python dans l'environnement virtuel."""
    os_type = get_platform()
    if os_type == "windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")


def get_pip_executable(venv_path):
    """Retourne le chemin vers l'exécutable pip dans l'environnement virtuel."""
    os_type = get_platform()
    if os_type == "windows":
        return os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_path, "bin", "pip")


def install_pytorch(python_exec, cuda_version):
    """Installe PyTorch avec le support CUDA approprié."""
    print(f"Installation de PyTorch avec CUDA {cuda_version}...")

    os_type = get_platform()

    # Commandes d'installation pour différentes versions de CUDA
    if cuda_version == "none":
        # Installation CPU only
        if os_type == "macos":
            # PyTorch pour macOS (MPS/CPU)
            cmd = [python_exec, "-m", "pip", "install", "torch", "torchvision", "torchaudio"]
        else:
            cmd = [python_exec, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url",
                   "https://download.pytorch.org/whl/cpu"]
    else:
        # Installation avec CUDA
        cuda_url = f"https://download.pytorch.org/whl/cu{cuda_version.replace('.', '')}"
        cmd = [python_exec, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", cuda_url]

    try:
        subprocess.run(cmd, check=True)
        print("PyTorch installé avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'installation de PyTorch: {e}")
        sys.exit(1)


def download_comfyui(install_dir, method="zip"):
    """Télécharge ComfyUI depuis GitHub en utilisant la méthode spécifiée."""
    comfyui_path = os.path.join(install_dir, "ComfyUI")

    if method == "git":
        print(f"Clonage du dépôt ComfyUI dans {comfyui_path}...")
        try:
            subprocess.run(["git", "clone", COMFYUI_REPO_URL, comfyui_path], check=True)
            print("ComfyUI cloné avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du clonage de ComfyUI: {e}")
            print("Essai de la méthode zip à la place...")
            method = "zip"  # Fallback à la méthode zip
        except FileNotFoundError:
            print("Git n'est pas installé. Utilisation de la méthode zip à la place...")
            method = "zip"  # Fallback à la méthode zip

    if method == "zip":
        zip_path = os.path.join(install_dir, "comfyui.zip")
        try:
            urllib.request.urlretrieve(COMFYUI_ZIP_URL, zip_path)

            print("Extraction de l'archive ComfyUI...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # L'archive contient un dossier racine ComfyUI-master
                zip_ref.extractall(install_dir)

            # Renommer le dossier extrait si nécessaire
            extracted_dir = os.path.join(install_dir, "ComfyUI-master")
            if os.path.exists(extracted_dir):
                if os.path.exists(comfyui_path):
                    shutil.rmtree(comfyui_path)
                os.rename(extracted_dir, comfyui_path)

            # Supprimer l'archive
            os.remove(zip_path)
            print("ComfyUI téléchargé et extrait avec succès.")
        except Exception as e:
            print(f"Erreur lors du téléchargement ou de l'extraction de ComfyUI: {e}")
            sys.exit(1)

    return comfyui_path


def install_comfyui_manager(comfyui_path, method="git"):
    """Installe ComfyUI-Manager dans le répertoire custom_nodes de ComfyUI."""
    manager_path = os.path.join(comfyui_path, "custom_nodes", "ComfyUI-Manager")
    print(f"Installation de ComfyUI-Manager dans {manager_path}...")

    if method == "git":
        try:
            subprocess.run(["git", "clone", COMFYUI_MANAGER_REPO_URL, manager_path], check=True)
            print("ComfyUI-Manager installé avec succès (via git).")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du clonage de ComfyUI-Manager: {e}")
        except FileNotFoundError:
            print("Git n'est pas installé. Tentative d'installation via zip...")
            method = "zip"  # Essayer zip si git échoue

    if method == "zip":
        zip_path = os.path.join(comfyui_path, "comfyui-manager.zip")  # Nom temporaire

        try:
            urllib.request.urlretrieve(COMFYUI_MANAGER_ZIP_URL, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(comfyui_path, "custom_nodes"))  # Extraire dans custom_nodes

            # Renommer le dossier extrait si nécessaire (à adapter selon la structure du zip)
            extracted_dir_name = "ComfyUI-Manager-main"  # <---  **IMPORTANT : Ajuster ce nom si nécessaire**
            extracted_dir = os.path.join(comfyui_path, "custom_nodes", extracted_dir_name)
            if os.path.exists(extracted_dir):
                shutil.move(extracted_dir, manager_path)  # Renommer au bon endroit
            os.remove(zip_path)  # Nettoyer le zip
            print("ComfyUI-Manager installé avec succès (via zip).")

        except Exception as e:
            print(f"Erreur lors du téléchargement/extraction de ComfyUI-Manager (zip): {e}")


def install_build_tools(python_exec):
    """Installe les outils de compilation nécessaires."""
    os_type = get_platform()

    print("Installation des outils de build nécessaires...")

    try:
        # Installation de wheel et setuptools à jour
        subprocess.run([python_exec, "-m", "pip", "install", "--upgrade", "wheel", "setuptools"], check=True)

        if os_type == "windows":
            # Sur Windows, installez Microsoft C++ Build Tools
            print("Sur Windows, vous devez avoir les Microsoft C++ Build Tools installés.")
            print("Si l'installation échoue, veuillez installer:")
            print("1. Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
            print("2. Sélectionnez 'C++ build tools' pendant l'installation")
    except subprocess.CalledProcessError as e:
        print(f"Avertissement lors de l'installation des outils de build: {e}")


def read_requirements(requirements_path):
    """Lit le fichier requirements.txt et retourne la liste des packages."""
    packages = []
    try:
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    packages.append(line)
        return packages
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier requirements.txt: {e}")
        return []


def install_dependencies(python_exec, pip_exec, comfyui_path):
    """Installe les dépendances Python requises pour ComfyUI"""
    print("Installation des dépendances Python pour ComfyUI...")
    requirements_path = os.path.join(comfyui_path, "requirements.txt")

    # Mise à jour de pip
    try:
        subprocess.run([python_exec, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Avertissement lors de la mise à jour de pip: {e}")

    # Installation des outils de build
    install_build_tools(python_exec)

    # Lire les dépendances
    packages = read_requirements(requirements_path)

    if not packages:
        print("Aucune dépendance trouvée ou erreur lors de la lecture du fichier requirements.txt")
        print("Tentative d'installation directe du fichier requirements.txt...")
        try:
            subprocess.run([pip_exec, "install", "-r", requirements_path], check=True)
            print("Installation des dépendances réussie.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation directe des dépendances: {e}")
            print("Passage à l'installation individuelle des packages...")

    # Installation des packages les plus problématiques en premier avec des wheels précompilés si possible
    critical_packages = ["numpy<2", "pillow", "opencv-python", "opencv-contrib-python", "websocket", "requests"]

    for package in critical_packages:
        matching_pkg = next((p for p in packages if p.startswith(package)), None)
        if matching_pkg:
            print(f"Installation du package critique {matching_pkg}...")
            try:
                # Pour opencv, essayer d'abord la version précompilée
                if "opencv" in matching_pkg:
                    subprocess.run([pip_exec, "install", "--only-binary", ":all:", matching_pkg],
                                   check=True, stderr=subprocess.PIPE)
                else:
                    subprocess.run([pip_exec, "install", matching_pkg], check=True)
                # Supprimer de la liste principale
                packages.remove(matching_pkg)
            except subprocess.CalledProcessError as e:
                print(f"Avertissement lors de l'installation de {matching_pkg}: {e}")
                print("Tentative avec une installation alternative...")
                try:
                    if "opencv" in matching_pkg:
                        # Si opencv échoue, essayer opencv-python-headless
                        alt_pkg = matching_pkg.replace("opencv-python", "opencv-python-headless")
                        subprocess.run([pip_exec, "install", alt_pkg], check=True)
                    else:
                        # Essayer sans version spécifique
                        base_pkg = matching_pkg.split('==')[0].split('>=')[0].split('<=')[0]
                        subprocess.run([pip_exec, "install", base_pkg], check=True)
                except subprocess.CalledProcessError as e2:
                    print(f"Erreur lors de l'installation alternative de {matching_pkg}: {e2}")

    # Installation des packages restants un par un
    failed_packages = []
    for package in packages:
        print(f"Installation de {package}...")
        try:
            subprocess.run([pip_exec, "install", package], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation de {package}: {e}")
            failed_packages.append(package)

    if failed_packages:
        print("\n=== Certains packages n'ont pas pu être installés ===")
        print("Les packages suivants ont échoué:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\nVous devrez peut-être les installer manuellement ou résoudre les dépendances manquantes.")

        # Tentative d'installation des packages avec --no-deps
        print("\nTentative d'installation des packages échoués sans leurs dépendances...")
        for pkg in failed_packages:
            try:
                subprocess.run([pip_exec, "install", "--no-deps", pkg], check=True)
                print(f"Package {pkg} installé sans dépendances.")
            except subprocess.CalledProcessError:
                pass

        # Demander à l'utilisateur s'il souhaite continuer
        print("\nCertains packages n'ont pas pu être installés, mais ComfyUI pourrait fonctionner sans eux.")
        print("Continuer l'installation? (Continuation automatique dans 10 secondes...)")

        # Auto-continuer après 10 secondes
        time.sleep(10)
        return True
    else:
        print("Toutes les dépendances ont été installées avec succès.")
        return True


def create_launch_script(install_dir, comfyui_path, venv_path, port):
    """Crée un script de lancement pour ComfyUI avec le port configuré."""
    os_type = get_platform()
    python_exec = get_python_executable(venv_path)

    if os_type == "windows":
        launch_path = os.path.join(install_dir, "launch_comfyui.bat")
        with open(launch_path, "w") as f:
            f.write(f'@echo off\n')
            f.write(f'echo Démarrage de ComfyUI sur le port {port}...\n')
            f.write(f'"{python_exec}" "{os.path.join(comfyui_path, "main.py")}" --port {port}\n')
            f.write(f'pause\n')
    else:
        launch_path = os.path.join(install_dir, "launch_comfyui.sh")
        with open(launch_path, "w") as f:
            f.write(f'#!/bin/bash\n')
            f.write(f'echo "Démarrage de ComfyUI sur le port {port}..."\n')
            f.write(f'"{python_exec}" "{os.path.join(comfyui_path, "main.py")}" --port {port}\n')

        # Rendre le script exécutable
        os.chmod(launch_path, 0o755)

    print(f"Script de lancement créé: {launch_path}")
    return launch_path
    

def main():
    parser = argparse.ArgumentParser(description="Script d'installation automatisée pour ComfyUI")
    parser.add_argument("--install-dir", default="./comfyui_install", help="Répertoire d'installation")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port pour le serveur ComfyUI (défaut: {DEFAULT_PORT})")
    parser.add_argument("--cuda-version", default=DEFAULT_CUDA_VERSION,
                        choices=["none", "11.7", "11.8", "12.1"],
                        help=f"Version CUDA à utiliser (défaut: {DEFAULT_CUDA_VERSION})")
    parser.add_argument("--install-models", action="store_true", default=DEFAULT_INSTALL_MODELS,
                        help="Configurer les dossiers pour les modèles")
    parser.add_argument("--method", default=DEFAULT_INSTALL_METHOD, choices=["zip", "git"],
                        help=f"Méthode d'installation (défaut: {DEFAULT_INSTALL_METHOD})")
    parser.add_argument("--skip-deps", action="store_true", help="Ignorer l'installation des dépendances")
    parser.add_argument("--python-path", default="C:/Program Files/Side Effects Software/Houdini 20.5.613/python311/python.exe",
                        help="Chemin explicite vers l'exécutable Python 3.11 de Houdini")

    args = parser.parse_args()

    # Créer le répertoire d'installation s'il n'existe pas
    install_dir = os.path.abspath(args.install_dir)
    os.makedirs(install_dir, exist_ok=True)

    print(f"=== Installation de ComfyUI avec Python 3.11 dans {args.install_dir} ===")
    print(f"Système détecté: {get_platform()}")

    # Obtenir le chemin de Python 3.11
    python_path = args.python_path    
    
    # Étape 1: Créer l'environnement virtuel avec Python 3.11
    venv_path = create_venv(install_dir, python_path)
    python_exec = get_python_executable(venv_path)
    pip_exec = get_pip_executable(venv_path)

    # Étape 2: Installer PyTorch avec support CUDA
    install_pytorch(python_exec, args.cuda_version)

    # Étape 3: Télécharger ComfyUI
    comfyui_path = download_comfyui(install_dir, args.method)
    install_comfyui_manager(comfyui_path, args.method)

    # Étape 4: Installer les dépendances
    if not args.skip_deps:
        install_dependencies(python_exec, pip_exec, comfyui_path)
    else:
        print("Installation des dépendances ignorée à la demande de l'utilisateur.")

    # Étape 6: Créer un script de lancement
    launch_script = create_launch_script(install_dir, comfyui_path, venv_path, args.port)

    print("\n=== Installation terminée avec succès ! ===")
    print(f"Pour lancer ComfyUI, exécutez: {launch_script}")
    print(f"ComfyUI sera accessible à l'adresse: http://localhost:{args.port}")

    # Afficher un message d'aide en cas de problème
    print("\nEn cas de problème d'installation des dépendances, vous pouvez essayer:")
    print(f"1. {python_exec} -m pip install --upgrade pip wheel setuptools")
    print(f"2. {python_exec} -m pip install -r {os.path.join(comfyui_path, 'requirements.txt')}")
    print("\nOu lancer ce script avec l'option --skip-deps et installer les dépendances manuellement.")


if __name__ == "__main__":
    main()
