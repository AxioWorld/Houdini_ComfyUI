import subprocess
import time
import os
import hou  # type: ignore
import urllib.parse 
import psutil # type: ignore
import requests  # type: ignore 

def is_server_responsive(url, timeout=1):
    """
    Checks if the server is responsive by making an HTTP GET request.
    """
    try:
        response = requests.get(url, timeout=timeout)
        # Consider the server responsive if we get any 2xx or 3xx status code
        return 200 <= response.status_code < 400
    except requests.exceptions.RequestException:
        return False

def start_server(extra_args=None, host="127.0.0.1", port=8188, startup_timeout=10):
    url = f"http://{host}:{port}"

    if get_comfyui_process_from_url() is not None:
        print("Le serveur ComfyUI est déjà en cours d'exécution.")
        return True

    command = [os.path.join(hou.expandString("$HCOMFYUI_VENV"), "scripts", "python.exe"), "main.py", "--port", "8188"]
    if extra_args:
        command.extend(extra_args)
    try:
        print("Démarrage du serveur ComfyUI...")
        comfyui_path = hou.expandString("$HCOMFYUI_COMFYUI")
        process = subprocess.Popen(command, cwd=comfyui_path) #creationflags = subprocess.CREATE_NO_WINDOW

        # Vérifier si le serveur est en cours d'exécution
        start_time = time.time()
        while time.time() - start_time < startup_timeout:
            if is_server_responsive(url):
                print("Serveur ComfyUI démarré.")
                return True
            time.sleep(0.1) 
        else:
            print("Le serveur ComfyUI n'a pas démarré correctement.")
            return False
    except FileNotFoundError:
        print(f"Erreur: Le chemin vers ComfyUI est incorrect: {comfyui_path}")
        return False
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur ComfyUI: {e}")
        return False



def get_comfyui_process_from_url(port=8188):
    try:
        if port is None:
            port = 80  # Port HTTP par défaut (à ajuster si nécessaire)
        print(f"Recherche du processus sur le port : {port}")

        # Trouver les connexions utilisant ce port
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    # Décodage prudent du nom du processus
                    process_name = proc.info['name']
                    if isinstance(process_name, bytes):
                        try:
                            process_name = process_name.decode('utf-8')
                        except UnicodeDecodeError:
                            process_name = "Nom inconnu (non décodable)"

                    for conn in proc.info['connections']:
                        if conn.laddr.port == port and conn.status == 'LISTEN':
                            print(f"Processus trouvé (PID={proc.info['pid']}, Name={process_name})")
                            return proc
                except Exception:  # Capturez les exceptions plus générales ici
                    pass
        except Exception as e:
            print(f"Erreur lors de la recherche du processus ComfyUI : {e}")
            return None
        
        #print(f"Aucun processus trouvé écoutant sur {url}")
        return None

    except Exception as e:
        print(f"Erreur lors de la recherche du processus ComfyUI : {e}")
        return None

def stop_server():
    process = get_comfyui_process_from_url()
    if process is None:
        print("No ComfyUI Server found to stop.")
    print("Arrêt du serveur ComfyUI...")
    try:
        if process:
            process.kill()
            process.wait(timeout=5)
            print("Serveur ComfyUI arrêté.")
            return True
        else:
            print("Aucun processus à arrêter.")
            return False
    except psutil.NoSuchProcess:
        print("Le processus n'existe déjà plus.")
        return True
    except psutil.TimeoutExpired:
        print("Le processus n'a pas répondu à la demande d'arrêt dans le délai imparti. Tentative de forcer l'arrêt...")
        try:
            process.kill()
            process.wait()
            print("Serveur ComfyUI arrêté de force.")
            return True
        except Exception as e:
            print(f"Erreur lors de l'arrêt forcé du serveur : {e}")
            return False
    except Exception as e:
        print(f"Erreur lors de l'arrêt du serveur : {e}")
        return False

def is_running():
    return get_comfyui_process_from_url() is not None   

