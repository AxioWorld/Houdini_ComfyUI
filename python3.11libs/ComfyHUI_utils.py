import subprocess
import os
import hou  # type: ignore
import sys
import re
from hutil.Qt import QtCore, QtGui, QtWidgets # type: ignore

import ComfyHUI_Config_utils 
import Install_utils 

# URLs pour les modèles
SD15_MODEL_URL = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
VAE_MODEL_URL = "https://huggingface.co/ffxvs/vae-flux/resolve/main/ae.safetensors"
FLUX_QUANTIZED_MODEL_URL = "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"
CLIP_L = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
T5XXL_FP8 = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"

def COMFYHUI_Install_DefaultModels():
    import comfyui_connector.model_manager

    model_manager = comfyui_connector.model_manager.ComfyUIModelManager()
    model_manager.download_models(SD15_MODEL_URL, type="checkpoints")
    model_manager.download_models(CLIP_L, type="clip")
    model_manager.download_models(T5XXL_FP8, type="clip")
    model_manager.download_models(FLUX_QUANTIZED_MODEL_URL, type="checkpoints") #HTTP Error 401: Unauthorized
    model_manager.download_models(VAE_MODEL_URL, type="vae")


def COMFYHUI_Install_Dependencies():
    """
        Install packages needed for COMFYHUI inside Houdini.
        Checks if the package is already installed before attempting installation.
    """
    packages = ["websocket-client", "requests", "psutil", "huggingface_hub"]

    hfs_path = os.environ.get("HFS")
    if not hfs_path:
        print("Error: HFS environment variable not set. Cannot determine Houdini Python executable.")
        return

    python_executable = (os.path.normpath(os.path.abspath(hfs_path)) + "/python311/python.exe")
    target_directory = os.path.join(hou.expandString("$HCOMFYUI"), "python")

    for package in packages:
        try:
            # Try importing the package to check if it's already installed
            __import__(package)
            print(f"'{package}' is already installed in the Houdini Python environment.")
        except ImportError:
            print(f"'{package}' is not installed. Attempting to install...")
            try:
                subprocess.run([python_executable, "-m", "pip", "install","--target", target_directory, package], check=True)
                print(f"Le module '{package}' a été installé avec succès dans l'environnement Python de Houdini.")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'installation de '{package}': {e}")
                print(f"Veuillez vérifier que '{python_executable}' est correct et que pip est installé.")
            except FileNotFoundError:
                print(f"L'exécutable Python '{python_executable}' est introuvable. Veuillez vérifier votre installation Houdini.")

class COMFYHUI_Installer(QtWidgets.QDialog):
    """
    import mlops_utils
    from importlib import reload
    reload(mlops_utils)

    mlops_utils.MLOPSConvertModel(hou.qt.mainWindow())
    """

    _instance = None  # Variable de classe pour stocker l'instance

    def __init__(self, parent):
        super(COMFYHUI_Installer, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.buildUI()
        self.resize(self.minimumSizeHint())
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def closeEvent(self, event):
        """Override closeEvent to clear the instance."""
        COMFYHUI_Installer._instance = None
        event.accept()

    def destroy_myself(self):
        """Explicitly destroy the widget."""
        self.close()  # Close the window
        self.deleteLater()  # Schedule for deletion

    def on_accept(self):
        install_dir = hou.text.expandString(self.download_directory_field.text())

        try:
            hfs_path = os.environ.get("HFS")
            python_path = os.path.normpath(os.path.abspath(hfs_path)) + "/python311/python.exe" #Install_utils.find_suitable_python() 
            intall_script = os.path.join(hou.expandString("$HCOMFYUI"), "install_comfyui.py")

            if python_path != None:                
                subprocess.run(
                    [
                        python_path,
                        intall_script,
                        "--install-dir",
                        install_dir,
                        "--port",
                        "8188",
                        "--cuda-version",
                        "11.8",
                        "--method",
                        "git",
                        "--python-path",
                        python_path, # I get a Permission error when i try to get localy installed python
                    ],
                    check=True,
                )
            else:
                hou.ui.displayMessage(
                f"Please download Python using the official installer : https://www.python.org/downloads/",
                buttons=("OK",),
                severity=hou.severityType.ImportantMessage,
                title="ComfyHUI Plugin",
                )
                return
        except subprocess.CalledProcessError as e:
            print(f"Error while trying to run the install ComfyUI: {e}")     
            hou.ui.displayMessage(
                f"Error while trying to run the install ComfyUI: {e}",
                buttons=("OK",),
                severity=hou.severityType.ImportantMessage,
                title="ComfyHUI Plugin",
                )
            return

        # Update path in the .json 
        config_file_path = os.path.join(hou.expandString("$HOUDINI_USER_PREF_DIR/packages"), "Houdini_ComfyUI.json" )
        config_data = ComfyHUI_Config_utils.load_json_config(config_file_path)

        if config_data: 
            ComfyHUI_Config_utils.update_env_variable(config_data, "HCOMFYUI_COMFYUI", os.path.join(install_dir, "ComfyUI"))
            ComfyHUI_Config_utils.update_env_variable(config_data, "HCOMFYUI_VENV", os.path.join(install_dir, "venv") )
            ComfyHUI_Config_utils.save_json_config(config_data, config_file_path)      
        
        # Install lib in Houdini ComfyHUI
        COMFYHUI_Install_Dependencies()

        # Install model
        if self.models_checkbox.checkState():
            COMFYHUI_Install_DefaultModels()

        hou.ui.displayMessage(
        f"You have successfully downloaded ComfyUI",
        buttons=("OK",),
        severity=hou.severityType.ImportantMessage,
        title="ComfyHUI Plugin",
        )

        self.destroy_myself()

    def on_cancel(self):
        self.destroy_myself()

    def open_directory_dialog(self):
        directory = hou.ui.selectFile(
            title="ComfyHUI - Select Download Directory",
            file_type=hou.fileType.Directory,
            multiple_select=False,
            chooser_mode=hou.fileChooserMode.Read,
        )
        if directory:
            self.download_directory_field.setText(directory)

    def buildUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle("ComfyHUI install dependancies")
        message_widget = QtWidgets.QLabel(
            "Install ComfyUI and dependancies required"
        )
        layout.addWidget(message_widget)

        layout_browse = QtWidgets.QHBoxLayout()
        download_path_label = QtWidgets.QLabel("Download Directory: ")
        self.download_directory_field = QtWidgets.QLineEdit("$HCOMFYUI/comfyUI_install_From_Houdini")
        layout_browse.addWidget(download_path_label)
        layout_browse.addWidget(self.download_directory_field)

        # Create QPushButton for directory browser
        self.dir_button = QtWidgets.QPushButton("...")
        self.dir_button.clicked.connect(self.open_directory_dialog)
        layout_browse.addWidget(self.dir_button)

        layout.addLayout(layout_browse)

        self.models_checkbox = QtWidgets.QCheckBox("Install Default models")
        layout.addWidget(self.models_checkbox)
        #self.option_box = QtWidgets.QComboBox() 
        #predefined_options = ["checkpoints", "vae", "upscale_models", "loras", "controlnet"]
        #self.option_box.addItems(predefined_options)
        #layout.addWidget(self.option_box)

        buttonlayout = QtWidgets.QHBoxLayout()
        self.update_button = QtWidgets.QPushButton("Download")
        self.update_button.clicked.connect(self.on_accept)
        buttonlayout.addWidget(self.update_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)
        buttonlayout.addWidget(self.cancel_button)

        layout.addLayout(buttonlayout)

        self.setMinimumSize(hou.ui.scaledSize(500), hou.ui.scaledSize(100))
        self.show()

def show_COMFYHUI_Installer():
    """Function to show the COMFYHUI_Installer dialog, ensuring only one instance exists."""

    if COMFYHUI_Installer._instance is None:
        # Create and show the dialog if it doesn't exist
        COMFYHUI_Installer._instance = COMFYHUI_Installer(hou.ui.mainQtWindow())
        COMFYHUI_Installer._instance.show()
    else:
        # If the dialog already exists, raise (bring to front) it
        COMFYHUI_Installer._instance.raise_()
        COMFYHUI_Installer._instance.activateWindow()  # Ensure it gets focus


class COMFYHUI_ModelInstaller(QtWidgets.QDialog):
    """
    
    """

    _instance = None  # Variable de classe pour stocker l'instance

    def __init__(self, parent):
        super(COMFYHUI_ModelInstaller, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.buildUI()
        self.resize(self.minimumSizeHint())
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def closeEvent(self, event):
        """Override closeEvent to clear the instance."""
        COMFYHUI_ModelInstaller._instance = None
        event.accept()

    def destroy_myself(self):
        """Explicitly destroy the widget."""
        self.close()  # Close the window
        self.deleteLater()  # Schedule for deletion

    def on_accept(self):
        import comfyui_connector.model_manager
        model_manager = comfyui_connector.model_manager.ComfyUIModelManager()

        if self.models_checkbox.checkState():
            COMFYHUI_Install_DefaultModels()
            self.destroy_myself()

        if len(self.modele_url_field.text()) > 0:
            model_manager.download_models(self.modele_url_field.text(), type=self.model_type_box.currentText())
        #model_manager.download_models(self.modele_url_field.text(), type="checkpoint")

        self.destroy_myself()

    def on_cancel(self):
        self.destroy_myself()

    def open_directory_dialog(self):
        directory = hou.ui.selectFile(
            title="ComfyHUI - Select Download Directory",
            file_type=hou.fileType.Directory,
            multiple_select=False,
            chooser_mode=hou.fileChooserMode.Read,
        )
        if directory:
            self.download_directory_field.setText(directory)

    def buildUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle("ComfyHUI Model Downloader")
        message_widget = QtWidgets.QLabel(
            "Download a model"
        )
        layout.addWidget(message_widget)
        self.model_type_box = QtWidgets.QComboBox() 
        predefined_options = ["checkpoints", "vae", "upscale_models", "loras", "controlnet"]
        self.model_type_box.addItems(predefined_options)
        layout.addWidget(self.model_type_box)

        layout_browse = QtWidgets.QHBoxLayout()    

        model_url_label = QtWidgets.QLabel("Model url: ")
        self.modele_url_field = QtWidgets.QLineEdit("")
        layout_browse.addWidget(model_url_label)
        layout_browse.addWidget(self.modele_url_field)
        self.models_checkbox = QtWidgets.QCheckBox("Install Default models")
        layout_browse.addWidget(self.models_checkbox)

        layout.addLayout(layout_browse)        

        buttonlayout = QtWidgets.QHBoxLayout()
        self.update_button = QtWidgets.QPushButton("Download")
        self.update_button.clicked.connect(self.on_accept)
        buttonlayout.addWidget(self.update_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)
        buttonlayout.addWidget(self.cancel_button)

        layout.addLayout(buttonlayout)

        self.setMinimumSize(hou.ui.scaledSize(500), hou.ui.scaledSize(100))
        self.show()

def show_COMFYHUI_ModelInstaller():
    """Function to show the COMFYHUI_ModelInstaller dialog, ensuring only one instance exists."""

    if COMFYHUI_ModelInstaller._instance is None:
        # Create and show the dialog if it doesn't exist
        COMFYHUI_ModelInstaller._instance = COMFYHUI_ModelInstaller(hou.ui.mainQtWindow())
        COMFYHUI_ModelInstaller._instance.show()
    else:
        # If the dialog already exists, raise (bring to front) it
        COMFYHUI_ModelInstaller._instance.raise_()
        COMFYHUI_ModelInstaller._instance.activateWindow()  # Ensure it gets focus