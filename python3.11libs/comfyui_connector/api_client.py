import requests  # type: ignore
import json
import websocket  # type: ignore
import uuid
import urllib.parse
import hou  # type: ignore
import os  # Import the os module

class ComfyUIClient:
    """
    A client for interacting with the ComfyUI API, including HTTP and WebSocket communication.
    """

    def __init__(self, server_address="127.0.0.1:8188", output_dir="output"):  # Add output_dir
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.ws = None  # WebSocket connection
        self.output_dir = output_dir  # Store the output directory
        os.makedirs(self.output_dir, exist_ok=True)  # Create the directory if it doesn't exist

    def _http_request(self, url, method="GET", data=None, files=None):
        """
        Internal method to make HTTP requests.
        """
        full_url = f"http://{self.server_address}/{url}"
        try:
            if method == "GET":
                response = requests.get(full_url)
            elif method == "POST":
                response = requests.post(full_url, json=data, files=files)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return None

    def queue_prompt(self, prompt):
        """
        Sends a prompt to the ComfyUI server to be added to the queue.
        """
        data = {"prompt": prompt, "client_id": self.client_id}
        return self._http_request("prompt", method="POST", data=data)

    def get_history(self, prompt_id):
        """
        Retrieves the history of a specific prompt.
        """
        return self._http_request(f"history/{prompt_id}")

    def get_image(self, filename, subfolder, folder_type):
        """
        Retrieves an image from the server.
        """
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_params = urllib.parse.urlencode(params)
        url = f"view?{url_params}"
        try:
            response = requests.get(f"http://{self.server_address}/{url}")
            response.raise_for_status()
            return response.content  # Return raw image bytes
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving image: {e}")
            return None

    def connect_websocket(self):
        """
        Establishes a WebSocket connection to the server.
        """
        ws_url = f"ws://{self.server_address}/ws?clientId={self.client_id}"
        try:
            self.ws = websocket.create_connection(ws_url)
            print("WebSocket connected.")
            return True
        except ConnectionRefusedError:
            print(f"Connection refused. Could not connect to {ws_url}. Ensure the server is running.")
            self.ws = None
            return False
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            self.ws = None
            return False

    def receive_websocket_data(self, callback=None):
        """
        Receives messages from the WebSocket and processes them.

        Args:
            callback (callable, optional): A function to call with image data.
                                         It should accept two arguments: node_id (str) and image_data (bytes).
        """

        if self.ws is None:
            print("WebSocket is not connected.")
            return

        output_images = {}
        current_node = ""
        try:
            while True:
                out = self.ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None:
                            break  # Execution is done
                        else:
                            current_node = data['node']
                else:
                    if current_node == 'SaveImageWebsocket':  # Assuming this is your node name
                        image_data = out[8:]  # Adjust '8' if needed
                        if callback:
                            callback(current_node, image_data)
                        else:
                            images_output = output_images.get(current_node, [])
                            images_output.append(image_data)
                            output_images[current_node] = images_output
                            # Save the image to the output directory
                            return self.save_image_to_directory(image_data)  # Call the save function
        except websocket.WebSocketConnectionClosedException:
            print("WebSocket connection closed.")
        except Exception as e:
            print(f"Error receiving WebSocket data: {e}")
        finally:
            self.close_websocket()

        return output_images if not callback else None

    def close_websocket(self):
        """
        Closes the WebSocket connection.
        """
        if self.ws:
            self.ws.close()
            self.ws = None
            print("WebSocket closed.")

    def save_image_to_directory(self, image_data):
        """
        Saves the received image data to a file in the output directory.
        """
        try:
            # Generate a unique filename for the image
            image_filename = f"image_{uuid.uuid4().hex}.png"  # You can adjust the file extension if needed
            image_path = os.path.join(self.output_dir, image_filename)

            with open(image_path, "wb") as f:
                f.write(image_data)
            print(f"Image saved to: {image_path}")
            return image_path
        except Exception as e:
            print(f"Error saving image: {e}")

        return ""

"""
import comfyui_connector
import importlib
import websocket

importlib.reload(comfyui_connector)

client = comfyui_connector.ComfyUIClient(output_dir="D:/ia/Houdini_Comfy/Nouveau")  # Initialize with output directory

prompt = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8,
            "denoise": 1,
            "latent_image": ["5", 0],
            "model": ["4", 0],
            "negative": ["7", 0],
            "positive": ["6", 0],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 8566251,
            "steps": 20
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "v1-5-pruned-emaonly.fp16.safetensors"
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "batch_size": 1,
            "height": 512,
            "width": 512
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": ["4", 1],
            "text": "a racoon with a wizzard hat and a staff"
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": ["4", 1],
            "text": "bad hands"
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        }
    },
    "SaveImageWebsocket": {
        "class_type": "SaveImageWebsocket",
        "inputs": {
            "images": ["8", 0]
        }
    }
}


# Queue the prompt
prompt_id = client.queue_prompt(prompt)
if prompt_id:
    print(f"Prompt queued with ID: {prompt_id['prompt_id']}")

    # WebSocket example (receiving images)
    if client.connect_websocket():
        def image_callback(node_id, image_data):
            print(f"Received image from node: {node_id}")

        client.receive_websocket_data()
        # Or, to get all images at once after processing:
        # images = client.receive_websocket_data()
        # if images:
        #     for node_id, image_list in images.items():
        #         for image_data in image_list:
        #             client.display_image_from_bytes(image_data)

else:
    print("Prompt queueing failed.")

    
"""