# comfyui_connector/workflow_manager.py
import json
import os
import hou  # type: ignore

class ComfyUIWorkflowManager:
    def __init__(self):
        self.workflow_directory = os.path.join(hou.expandString("$HCOMFYUI"), "ressources", "workflows")
        self.workflow = None

    def load_workflow(self, filename):
        filepath = os.path.join(self.workflow_directory, filename)
        try:
            with open(filepath, 'r') as f:
                self.workflow = json.load(f)
                return self.workflow
        except FileNotFoundError:
            print(f"Erreur: Le workflow '{filename}' n'a pas été trouvé dans '{self.workflow_directory}'.")
            return None
        except json.JSONDecodeError:
            print(f"Erreur: Le fichier '{filename}' n'est pas un JSON valide.")
            return None

    def save_workflow(self, filename):
        filepath = os.path.join(self.workflow_directory, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(self.workflow, f, indent=4)
            print(f"Workflow sauvegardé dans '{filepath}'.")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du workflow: {e}")
            return False

    def list_workflows(self):
        return [f for f in os.listdir(self.workflow_directory) if f.endswith(".json")]
    
    def modifier_workflow_specifique(self, id, input, value):
        """
        Modifie le prompt positif, les étapes du KSampler et le nom du checkpoint
        dans un dictionnaire de workflow.
        """
        #modifications_effectuees = []

        if id in self.workflow:
            if "inputs" in self.workflow[id]:
                if input in self.workflow[id]["inputs"]:
                    self.workflow[id]["inputs"][input] = value
                    #modifications_effectuees.append("Prompt positif du nœud '6' modifié.")
                else:
                    print(f"No input : {input} found in node id : {id} {self.workflow[id]['class_type']}")
        else:
            print(f"No id : {id} found in workflow {self.workflow}")
        return self.workflow #, modifications_effectuees
    
    def Get_ID_By_ClassType(self, classType):
        """

        """
        #modifications_effectuees = []

        id_list = []

        try:
            for id in self.workflow:
                if self.workflow[id]["class_type"] == classType:
                    id_list.append(id)

            if len(id_list) > 0:
                return id_list
            else:
                print(f"No node with class type : {classType} found")
                id_list.append(None)
                return id_list
        except:
            print(f"Error while trying to retrieve nodes with class type : {classType} ")
            id_list.append(None)
            return id_list

    def Get_ID_By_Title(self, title):
        """

        """
        #modifications_effectuees = []

        id_list = []
        try:
            for id in self.workflow:
                if self.workflow[id]["_meta"]["title"] == title:
                    id_list.append(id)

            if len(id_list) > 0:
                return id_list
            else:
                print(f"No node with Title : {title} found")
        except:
            print(f"Error while trying to retrieve nodes with title : {title} ")

        id_list.append(None)
        return id_list

    def Get_Workflow(self):
        return self.workflow
    
"""
workflow_manager = ComfyUIWorkflowManager()

# Clone default workflow
default_workflow_path = os.path.join(hou.expandString("$HCOMFYUI"), "ressources", "workflows", "Houdini_ComfyUI.json")
default_workflow = workflow_manager.load_workflow(default_workflow_path)
temp_workflow = os.path.join(hou.expandString("$HOUDINI_TEMP_DIR"), "Houdini_ComfyUI_TEMP.json")

# Update workflow to node parameter
workflow_manager.modifier_workflow_specifique(default_workflow, id, input, "value")

# Save to Houdini Temp dir
workflow_manager.save_workflow(default_workflow, temp_workflow)

# Lister les workflows
#print("Workflows disponibles:", workflow_manager.list_workflows())
"""