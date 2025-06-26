# Houdini_ComfyUI

Open source Bridge Houdini and comfyUI

![CUIxHou](https://github.com/user-attachments/assets/3c1b3305-89b4-4b2a-9fdd-04f963c2524d)


# Installation

-move Houdini_ComfyUI.json to C:\Users[YourUserName]\Documents\houdini20.5\packages

-Replace "HCOMFYUI" by your Houdini_ComfyUI path

-Run Houdini and click on Install Dependencies (first btn in the shelf)

-Then Install Comfy (second btn)

-copy all the models to the comfyUI model directory at the correct  location

https://huggingface.co/city96/FLUX.1-dev-gguf/tree/main
https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/clip_l.safetensors
https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/t5xxl_fp8_e4m3fn.safetensors
https://huggingface.co/ffxvs/vae-flux/blob/main/ae.safetensors7
https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/blob/main/control_v11f1p_sd15_depth_fp16.safetensors

-Copy all the file in the python of the Houdini_ComfyUI  to the Comfyui venv/Lib/site-packages (some library are missing like yaml)

-Run the launch_script.bat and install missing custom nodes for Flux

( ComfyUI-GGUF by City96) : https://github.com/city96/ComfyUI-GGUF

( DualClipLoader and UnetLoader)

Run Houdini !
