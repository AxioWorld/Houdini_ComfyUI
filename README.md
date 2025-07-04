# Houdini_ComfyUI

Open source Bridge Houdini and comfyUI by https://github.com/NXStorm and https://github.com/Caremba

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
10. You can close all windows and run Houdini !

## DEMO

https://github.com/user-attachments/assets/fe140d06-0c8a-42b5-b76f-4c92c5ef95ef



## Current Nodes

- **depth_map**: Generates a depth map using camera and object input parameters.
- **Comfy_Houdini**: TOPNET node. ComfyUI bridge node with full parameter support for Text-to-image or Image-to-image
- **image_preview**: TOPNET node. Transfers rendered images to Houdini's Composite Viewer.Double-click the tile checkbox to refresh the image.**Cook the node to start/re-run the process**
  
## To-Do
#### Comfy_UI node
- [x] Implement FluxGGUF texte to image
- [ ] Implement FluxGGUF image to image
- [ ] Implement Lora
- [ ] Implement more controlnet
- [ ] Implement WAN
- [ ] Implement SDXL
- [ ] Implement Flux Kontext

#### Shelf button
- [x] Auto install Dependencies
- [x] Auto install ComfyUI
- [ ] Automatically install models from linked

#### Code fix
- [x] Launch ComfyUI automatically with the ComfyUI node
- [ ] Load all workflows on startup
- [ ] Auto-load all model checkpoints
- [ ] Increase ComfyUI startup timeout to prevent errors

## Note
- Before generate image , select the output path tab in comfyui node ➝ Export
- Same for the Image Preview node output
- The first time you launch the process, you may encounter the error: "ComfyUI not launched normally". This is normal because ComfyUI starts in the background (you can check the CMD window). Once ComfyUI finishes loading, you can re-cook the process!

 ## Project References
- https://github.com/proceduralit/StableDiffusion_Houdini
- https://github.com/vinavfx/ComfyUI-for-Nuke
- https://github.com/stassius/StableHoudini
