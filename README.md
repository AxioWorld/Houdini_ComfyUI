# Houdini_ComfyUI

Open source Bridge Houdini and comfyUI

![CUIxHou](https://github.com/user-attachments/assets/023f25e5-3344-4e1e-844b-d42d01563cd8)


# Installation

1. Download Zip file or git clone the repository
2. Move Houdini_ComfyUI.json to `C:\Users\[YourUserName]\Documents\houdini20.5\packages`
(If you don't see the packages folder, create it.)
3. Replace "HCOMFYUI" with your Houdini_ComfyUI path
4. Run Houdini and search in the Shelf tab for the "ComfyHUI" shelf
5. Click on the first button to Install Dependencies
6. Then install ComfyUI with the second button
7. Copy all the models to the ComfyUI model directory in the correct location:


https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/v1-5-pruned-emaonly.ckpt 
**to** `...\ComfyUI\models\checkpoints`

https://huggingface.co/city96/FLUX.1-dev-gguf/tree/main 
**to** `...\ComfyUI\models\unet`

https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/clip_l.safetensors 
**to** `...\ComfyUI\models\text_encoders`

https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/t5xxl_fp8_e4m3fn.safetensors 
**to**`...\ComfyUI\models\text_encoders`

https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/blob/main/split_files/vae/ae.safetensors 
**to**`...\ComfyUI\models\vae`

https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/blob/main/control_v11f1p_sd15_depth_fp16.safetensors 
**to**`\ComfyUI\models\controlnet`

8. Copy **all** files in the python of the Houdini_ComfyUI to the Comfyui venv/Lib/site-packages (some library are missing like yaml)
9. Run the launch_script.bat and install custom nodes for FluxGGUF ( ComfyUI-GGUF by City96)
( DualClipLoader and UnetLoader)
10. Run Houdini !

## Current Nodes
