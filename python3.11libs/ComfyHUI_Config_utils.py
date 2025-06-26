import json
import os
import hou # type: ignore

def load_json_config(filepath):
    """
    Charge un fichier JSON de configuration.

    Args:
        filepath (str): Le chemin vers le fichier JSON.

    Returns:
        dict: Le contenu du fichier JSON sous forme de dictionnaire,
              ou None si le fichier n'existe pas ou une erreur survient.
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{filepath}' n'a pas été trouvé.")
        return None
    except json.JSONDecodeError:
        print(f"Erreur: Impossible de décoder le JSON dans '{filepath}'.")
        return None
    except Exception as e:
        print(f"Une erreur inattendue s'est produite lors du chargement de '{filepath}': {e}")
        return None

def save_json_config(data, filepath):
    """
    Sauvegarde un dictionnaire de données dans un fichier JSON.

    Args:
        data (dict): Le dictionnaire de données à sauvegarder.
        filepath (str): Le chemin où sauvegarder le fichier JSON.
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)  # Indentation pour une meilleure lisibilité
        print(f"Configuration sauvegardée avec succès dans '{filepath}'.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la sauvegarde dans '{filepath}': {e}")

def update_env_variable(config, env_name, value, method="set"):
    """
    Met à jour ou ajoute une variable d'environnement dans la section 'env' de la configuration.

    Args:
        config (dict): Le dictionnaire de configuration.
        env_name (str): Le nom de la variable d'environnement à mettre à jour ou ajouter.
        value (str or list): La nouvelle valeur de la variable.
        method (str): La méthode de mise à jour pour 'PYTHONPATH' (si 'env_name' est PYTHONPATH).
                      Peut être "set", "prepend", "append". Par défaut "set".
    """
    found = False
    for env_item in config.get("env", []):
        if isinstance(env_item, dict) and env_name in env_item:
            if env_name == "PYTHONPATH" and isinstance(env_item[env_name], dict):
                env_item[env_name]["value"] = value
                env_item[env_name]["method"] = method
            else:
                env_item[env_name] = value
            found = True
            break
    if not found:
        if env_name == "PYTHONPATH":
            config.setdefault("env", []).append({env_name: {"value": value, "method": method}})
        else:
            config.setdefault("env", []).append({env_name: value})

def get_env_variable(config, env_name):
    """
    Récupère la valeur d'une variable d'environnement de la section 'env' de la configuration.

    Args:
        config (dict): Le dictionnaire de configuration.
        env_name (str): Le nom de la variable d'environnement à récupérer.

    Returns:
        str or dict or None: La valeur de la variable, ou None si non trouvée.
                             Retourne un dictionnaire pour PYTHONPATH.
    """
    for env_item in config.get("env", []):
        if isinstance(env_item, dict) and env_name in env_item:
            return env_item[env_name]
    return None


# Path to .json config file 
# hou.expandString("$HOUDINI_USER_PREF_DIR")+"/packages/Houdini_ComfyUI.json"

#
#   Updata HCOMFYUI path
#
"""
config_file_path = hou.expandString("$HOUDINI_USER_PREF_DIR")+"/packages/Houdini_ComfyUI.json" 

config_data = load_json_config(config_file_path)

if config_data:
    # Définissez la nouvelle valeur pour HCOMFYUI
    new_hcomfyui_path = "E:/nouveau_chemin/Houdini_ComfyUI"

    # Utilisez la fonction update_env_variable pour modifier la variable
    update_env_variable(config_data, "HCOMFYUI", new_hcomfyui_path)

    # Sauvegardez les modifications dans le fichier JSON
    save_json_config(config_data, config_file_path)
else:
    print("Impossible de charger le fichier de configuration.")

"""