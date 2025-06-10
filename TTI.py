# Machine Learning libraries 
import torch, string, threading, importlib, traceback
from torch import autocast
from diffusers import DiffusionPipeline, StableDiffusionPipeline, AutoencoderKL, StableDiffusionXLPipeline, AutoPipelineForText2Image
from compel import Compel, ReturnedEmbeddingsType

# Import other necessary methods
import random, time, common_functions
from collections import defaultdict

# Libraries for processing image 
from PIL import ImageTk, Image
from PIL.PngImagePlugin import PngInfo
import customtkinter as ctk
from tkinter import messagebox

# private modules 
from authtoken import auth_token

class TextToImage():
    class NoWatermark:
        def apply_watermark(self, img):
            return img
    
    def __init__(self,
                 script_path, models_path, TTImodels_path, general_settings_file
                 ) -> None:
        self._script_path = script_path
        self._models_path = models_path
        self.TTImodels_path = TTImodels_path
        self.general_settings_file = general_settings_file
        #self._model_path = f"{script_path}\\models"
        
        #self._selected_model_path = f"{self._model_path}\\stable-diffusion-v1-4\\" # can also use something like "stabilityai/stable-diffusion-2"
        #self._selected_vae_path = f"{self._model_path}\\stable-diffusion-v1-4\\vae\\"

        #self._selected_model_path = f"{self._model_path}\\stable-diffusion-v1-5\\" # can also use something like "stabilityai/stable-diffusion-2"
        #self._selected_vae_path = f"{self._model_path}\\stable-diffusion-v1-5\\vae\\"
                
        #self._selected_model_path = f"{self._model_path}\\stable-diffusion-2-1\\" # can also use something like "stabilityai/stable-diffusion-2"
        #self._selected_vae_path = f"{self._model_path}\\stable-diffusion-2-1\\vae\\"
        
        self._selected_model_path = f"{self._models_path}\\stable-diffusion-xl-base-1.0\\" # can also use something like "stabilityai/stable-diffusion-2"
        self._selected_vae_path = f"{self._models_path}\\stable-diffusion-xl-base-1.0\\vae\\"
        #self._selected_refiner_path = f"{self._model_path}\\stable-diffusion-xl-refiner-1.0\\"
        
        self._use_karras_sigmas = False
        
        # Initialize these variables for later use
        self.image = None
        self.generationThread = None

    def _GetActiveTTIModelParams(self):
        """
        Returns a dictionary with all parameters of the TTI model preset selected by the user.
        """
        # Load the general settings JSON
        settings_json = common_functions.load_json_from_file(self.general_settings_file)

        selected_model_name = ""
        if "TTI_model_preset" in settings_json:
            selected_model_name = settings_json['TTI_model_preset']
        
        if (len(selected_model_name)>0):
            # Load the models json
            models_json = common_functions.load_json_from_file(self.TTImodels_path)

            if "model" in models_json:
                # Go through the models_json elements until the one that corresponds to the selected model preset is found, 
                # and return its parameters
                for model_params in models_json['model']:
                    if (model_params['name']==selected_model_name):
                        return model_params
        return None
    
    def GetCompatibleSchedulers(self):
        # Temporarily load the pipeline so we can find out its compatible schedulers
        try:
            stable_diffusion_model= self._GetStableDiffusionPipeline()
        except OSError as e:
            error_message = str(e)
            common_functions.LogEntry(title="Error loading compatible schedulers", message="Attempting to load the compatible schedulers for the selected TTI model returned the following error:\n" + error_message, type="error", show_messagebox=True)
            return None
        except KeyError:
            common_functions.LogEntry(title="Error loading compatible schedulers", message="The active TTI model preset's settings are corrupted. Reconfigure the model preset from the SETTINGS menu.", type="error", show_messagebox=True)
            return None

        # Build the scheduler list
        compatible_dump = stable_diffusion_model.scheduler.compatibles

        compatibles = []
        for item in compatible_dump:
            compatibles.append(str(item).rsplit(".", 1)[-1].replace(">", "").replace("<", "").replace("'", ""))
        return sorted(compatibles)
    
    def _GetStableDiffusionPipeline(self):
        """
        Returns the main TTI pipeline, as per the model preset selected in the JSON files
        """
        #torch.backends.cuda.matmul.allow_tf32 = True # TensorFlow32 optimization

        # Get the active model preset's parameters
        model_params = self._GetActiveTTIModelParams()

        if model_params != None:
            use_safetensors = model_params['unet_optimizationframe_safetensors']
            if use_safetensors != True: use_safetensors = False # Do this, since model_params might contain something other than True or False

            if (model_params['general_optionframe_isSDXL']==True):
                if ("turbo" in model_params['mainmodel_entry']):
                # THIS IS TEMPORARY TO TEST SDXL TURBO!!!!! MUST DO THIS PART RIGHT by adding a model_params['general_optionframe_isSDXLturbo'] config key!!!
                #if (model_params['general_optionframe_isSDXLTurbo']==False):
                    return AutoPipelineForText2Image.from_pretrained("E:/Developments/Python Projects/Text-To-Image-With-Stable-Diffusion/models/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
                    #return AutoPipelineForText2Image.from_pretrained(str(model_params['mainmodel_entry']), variant="fp16", torch_dtype=torch.float16)
                else:
                    if model_params['unet_optimizationframe_fp16']==True:
                        return StableDiffusionXLPipeline.from_pretrained(model_params['mainmodel_entry'], variant="fp16", use_safetensors=use_safetensors, 
                                                                                        torch_dtype=torch.float16)
                    else:
                        return StableDiffusionXLPipeline.from_pretrained(model_params['mainmodel_entry'], use_safetensors=use_safetensors)
            else:
                if model_params['unet_optimizationframe_fp16']==True:
                    return DiffusionPipeline.from_pretrained(model_params['mainmodel_entry'], safety_checker=None, variant="fp16", 
                                                                                torch_dtype=torch.float16)
                else:
                    return DiffusionPipeline.from_pretrained(model_params['mainmodel_entry'], safety_checker=None)
        return None
    
    def _GetRefinerPipeline(self):
        # Get the active model preset's parameters
        model_params = self._GetActiveTTIModelParams()
        
        if model_params != None:
            use_safetensors = model_params['refiner_optimizationframe_safetensors']
            if use_safetensors != True: use_safetensors = False # Do this, since model_params might contain something other than True or False
            
            if (model_params['general_optionframe_isSDXL']==True):
                if model_params['refiner_optimizationframe_fp16']==True:
                    return StableDiffusionXLPipeline.from_pretrained(model_params['refiner_entry'], variant="fp16", 
                                                                     use_safetensors=use_safetensors, torch_dtype=torch.float16)
                else:
                    return StableDiffusionXLPipeline.from_pretrained(model_params['refiner_entry'], use_safetensors=use_safetensors)
            else:
                if model_params['refiner_optimizationframe_fp16']==True:
                    return DiffusionPipeline.from_pretrained(model_params['refiner_entry'], safety_checker=None, variant="fp16", 
                                                                                torch_dtype=torch.float16)
                else:
                    return DiffusionPipeline.from_pretrained(model_params['refiner_entry'], safety_checker=None)
        return None

    def _PromptConsolidator(self, prompt, preset_prompt_canvas):
        """
        Merges the prompt text and the preset prompts into a single prompt ready for inference or to send to compel
        """
        # Append the prompt presets to the prompt
        prompt_preset_suffix = ""
        prompt_preset_prefix = ""
        for button in preset_prompt_canvas.buttons:
            if (button.priority>0):
                if (button.priority==1):
                    prompt_preset_prefix += ", " + button._text
                else:
                    prompt_preset_prefix += ", (" + button._text + ")" + "++" * (button.priority - 1)
            else:
                prompt_preset_suffix += ", " + button._text
        # remove the first comma of the prefix, since it will always be first
        prompt_preset_prefix = prompt_preset_prefix[2:]
        # If the prompt and prefix are empty, remove the first comma of the suffix
        if (len(prompt)==0 and len(prompt_preset_prefix)==0 and len(prompt_preset_suffix)>0):
            prompt_preset_suffix = prompt_preset_suffix[2:]
        # If the prompt or suffix are not empty, add a comma to the prefix
        if (len(prompt)>0) and (len(prompt_preset_prefix)>0):
            prompt_preset_prefix += ", "
        consolidated_prompt = prompt_preset_prefix + prompt + prompt_preset_suffix
        return consolidated_prompt
    
    # Generate image from text 
    def TTI_Generate(self, target_image_object, seed_number, prompt, negative_prompt, inference_steps, guidance_scale, 
                     process_finished_callable: callable = None, progressCallable: callable = None, scheduler_name = "", 
                     width=None, height=None, preset_prompt_canvas=None, preset_negative_prompt_canvas=None):
        """
        This function generates image from a text with stable diffusion
        """
        # Get the active model preset's parameters from the JSON
        model_params = self._GetActiveTTIModelParams()

        # Handle there being no model selected
        if (model_params == None):
            process_finished_callable() # Finish the process gracefully
            return

        # Build the "consolidated" prompts (prompts including the presets)
        consolidated_prompt = self._PromptConsolidator(prompt, preset_prompt_canvas)
        consolidated_negative_prompt = self._PromptConsolidator(negative_prompt, preset_negative_prompt_canvas)

        # Create lists with current preset prompts
        prompt_preset_buttons = []
        for button in preset_prompt_canvas.buttons:
            prompt_preset_buttons.append([button._text, button.priority]) # Build list of all buttons and their priorities
        
        negative_prompt_preset_buttons = []
        for button in preset_negative_prompt_canvas.buttons:
            negative_prompt_preset_buttons.append([button._text, button.priority]) # Build list of all buttons and their priorities

        # Define the various options
        use_weighted_prompts = True
        use_vae = True if model_params['vae_optionframe_usevae'] == True else False # Do this since model_params can return something other than True or False
        activate_optimizations = defaultdict(lambda: None)
        activate_optimizations['torch_compile'] = True if model_params['unet_optimizationframe_torchcompile'] == True else False
        activate_optimizations['vae_tiling'] = True if model_params['unet_optimizationframe_vaetiling'] == True else False
        activate_optimizations['xformers'] = True if model_params['unet_optimizationframe_xformers'] == True else False
        activate_optimizations['sequential_cpu_offload'] = True if model_params['unet_optimizationframe_seqCPUoffload'] == True else False
        activate_optimizations['model_cpu_offload'] = True if model_params['unet_optimizationframe_modCPUoffload'] == True else False
        activate_optimizations['attention_slicing'] = True if model_params['unet_optimizationframe_attention'] == True else False

        # define new_seed variable
        new_seed = -1

        # define the SD pipeline
        device = "cuda"
        
        # Load the pipeline
        stable_diffusion_model = self._GetStableDiffusionPipeline()

        # Add the VAE (an enhancer that refines the output ["latent"] of the main model for a bit better quality)
        if use_vae:
            vae = AutoencoderKL.from_pretrained(model_params['vae_entry'], torch_dtype=torch.float16)
            stable_diffusion_model.vae = vae
        
        # Activate any desired optimizations
        if (activate_optimizations['torch_compile']):
            stable_diffusion_model.unet = torch.compile(stable_diffusion_model.unet, mode="reduce-overhead", fullgraph=True)
        if (activate_optimizations['vae_tiling']):
            stable_diffusion_model.enable_vae_tiling()
        if (activate_optimizations['xformers']):
            stable_diffusion_model.enable_xformers_memory_efficient_attention()
        if (activate_optimizations['sequential_cpu_offload']):
            stable_diffusion_model.enable_sequential_cpu_offload() #Lots of VRAM savings, very slow
        if (activate_optimizations['model_cpu_offload']):
            stable_diffusion_model.enable_model_cpu_offload() #Faster alternative for smaller VRAM savings. Can be coupled with attention slicing.
        if (activate_optimizations['attention_slicing']):
            stable_diffusion_model.enable_attention_slicing()
        
        # Send pipeline to GPU. Must be done AFTER optimizations are activated. Must NOT be done if model_cpu_offload is enabled.
        if (activate_optimizations['model_cpu_offload'] == False):
            stable_diffusion_model.to(device)

        # This uses the Compel library to create a weighted ("prioritized") prompt embed. In short, prompt parts
        # followed by "++"" and "--" are given more or less priority. Must be set up after pipeline.to(device) 
        # to work with the torch.float16 optimization (a.k.a. "half precision weights")
        if use_weighted_prompts:
            truncate_long_prompts= True
            if (model_params['general_optionframe_isSDXL']==True):
                compel = Compel(tokenizer=[stable_diffusion_model.tokenizer, stable_diffusion_model.tokenizer_2] , text_encoder=[stable_diffusion_model.text_encoder, stable_diffusion_model.text_encoder_2], returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED, requires_pooled=[False, True])
                weighted_prompt=[None] * 2
                weighted_negative_prompt=[None] * 2
                weighted_prompt[0], weighted_prompt[1] = compel(consolidated_prompt)
                weighted_negative_prompt[0], weighted_negative_prompt[1] = compel(consolidated_negative_prompt)
            else:
                compel = Compel(tokenizer=stable_diffusion_model.tokenizer, text_encoder=stable_diffusion_model.text_encoder,
                                truncate_long_prompts=truncate_long_prompts)
                weighted_prompt = compel(consolidated_prompt)
                weighted_negative_prompt = compel(consolidated_negative_prompt)
                if not truncate_long_prompts: [weighted_prompt, weighted_negative_prompt] = compel.pad_conditioning_tensors_to_same_length([weighted_prompt, weighted_negative_prompt])
        else:
            weighted_prompt = None
            weighted_negative_prompt = None
        
        if (scheduler_name != ""):
            # Dynamically load the scheduler
            scheduler_module_name = "diffusers"  # module name

            # Dynamically import the main module
            module = importlib.import_module(scheduler_module_name)

            # Get the specific scheduler's attribute from the main module
            scheduler_attribute = getattr(module, scheduler_name)

            # Load the specific scheduler
            try:
                scheduler = scheduler_attribute.from_config(stable_diffusion_model.scheduler.config, use_karras_sigmas=self._use_karras_sigmas)
            except ImportError as e:
                # The scheduler cannot be used for some reason, finish this process gracefully
                process_finished_callable()

                # Get the error message as a string
                #error_message = str(traceback.format_exc())
                error_message = str(e)
                common_functions.LogEntry(title="Sampler cannot be used", message="Attempting to use the sampler you selected returned the following error:\n" + error_message, type="error", show_messagebox=True)
                return
            stable_diffusion_model.scheduler = scheduler
        
        #with autocast(device): 
        #If no seed number was provided, choose one at random. Otherwise, use the provided seed.
        if len(seed_number)==0:
            new_seed = random.randint(0, 2**32 - 1)
        else:
            new_seed = int(seed_number)
        generator = torch.Generator("cuda").manual_seed(new_seed)
        
        # This generates the image
        # We'll generate the actual image in a separate thread so as to not freeze the rest of the program
        can_run = True
        if not (self.generationThread == None):
            if self.generationThread.is_alive():
                can_run = False
                print("\n\n\nA previous thread was running when it shouldn't have.")
                self.generationThread.join() # This causes the program to hang for now, which is better than not being able to terminate the process
        
        if (can_run):
            self.generationThread = threading.Thread(target=self._generateImageThread, args=(stable_diffusion_model, width, height,
                                                                    prompt, consolidated_prompt, weighted_prompt, 
                                                                    negative_prompt, consolidated_negative_prompt, 
                                                                    weighted_negative_prompt, int(inference_steps), float(guidance_scale), 
                                                                    progressCallable, 1, generator, target_image_object,
                                                                    new_seed, process_finished_callable, use_weighted_prompts,
                                                                    scheduler_name, use_vae, prompt_preset_buttons, 
                                                                    negative_prompt_preset_buttons))
            self.generationThread.daemon = True # Set this thread as a "Daemon" so that it is always terminated when the main program exits
            self.generationThread.start()
    
    def _generateImageThread(self, stable_diffusion_model, width, height, prompt, consolidated_prompt, weighted_prompt, negative_prompt, consolidated_negative_prompt, weighted_negative_prompt, num_inference_steps, guidance_scale, 
                             callback, callback_steps, generator, target_image_object, new_seed, process_finished_callable,
                             use_weighted_prompts, scheduler_name, use_vae, prompt_preset_buttons, negative_prompt_preset_buttons):
        # Get the active model preset's parameters
        model_params = self._GetActiveTTIModelParams()
        
        try:
            # Fix for the stupid red/green dots
            if model_params['general_optionframe_isSDXL']==True:
                stable_diffusion_model.watermark = self.NoWatermark() # Removes the stupid red/green dots

            # If a refiner is used (for SDXL), the image output must be a latent; otherwise, a ready-to-use PIL
            if (model_params['refiner_userefiner']==True):
                output_type = "latent"
            else:
                output_type = "pil"
            
            if use_weighted_prompts:
                if (model_params['general_optionframe_isSDXL']==True):
                        # SDXL needs 2 bits of information per prompt: the "conditioning" [0] and the "pooled" prompt [1]
                        image = stable_diffusion_model(prompt_embeds = weighted_prompt[0], pooled_prompt_embeds=weighted_prompt[1],
                                                negative_prompt_embeds = weighted_negative_prompt[0], negative_pooled_prompt_embeds=weighted_negative_prompt[1],
                                                num_inference_steps=num_inference_steps, guidance_scale=guidance_scale, 
                                                callback=callback, callback_steps=callback_steps, generator=generator, 
                                                width=width, height=height, output_type=output_type).images[0]
                else:
                    image = stable_diffusion_model(prompt_embeds = weighted_prompt,
                                                negative_prompt_embeds = weighted_negative_prompt, 
                                                num_inference_steps=num_inference_steps, guidance_scale=guidance_scale, 
                                                callback=callback, callback_steps=callback_steps, generator=generator, 
                                                width=width, height=height, output_type=output_type).images[0]
            else:
                image = stable_diffusion_model(prompt = consolidated_prompt, negative_prompt = consolidated_negative_prompt, num_inference_steps=num_inference_steps, 
                                            guidance_scale=guidance_scale, callback=callback, callback_steps=callback_steps, 
                                            generator=generator, width=width, height=height, output_type=output_type).images[0]
        except Exception as e:
            # The image generation cannot be run for some reason, finish this process gracefully
            process_finished_callable()

            # Get the error message as a string
            error_message = str(e)
            common_functions.LogEntry(title="Error generating image", message="Attempting to generate the image returned the following error:\n" + error_message, type="error", show_messagebox=True)
            common_functions.LogEntry(title="Traceback", message=traceback.format_exc(), type="error", show_messagebox=False)
            return
        
        if (model_params['refiner_userefiner']==True):
            # Run the refiner
            refiner_pipeline = self._GetRefinerPipeline()
            
            # Fix for the stupid red/green dots
            if model_params['general_optionframe_isSDXL']==True:
                refiner_pipeline.watermark = self.NoWatermark() # Removes the stupid red/green dots

            if model_params['refiner_optimizationframe_torchcompile'] == True: refiner_pipeline.unet = torch.compile(refiner_pipeline.unet, mode="reduce-overhead", fullgraph=True)
            if model_params['refiner_optimizationframe_vaetiling'] == True: refiner_pipeline.enable_vae_tiling()
            if model_params['refiner_optimizationframe_xformers'] == True: refiner_pipeline.enable_xformers_memory_efficient_attention()
            if model_params['refiner_optimizationframe_seqCPUoffload'] == True: refiner_pipeline.enable_sequential_cpu_offload() #Lots of VRAM savings, very slow
            if model_params['refiner_optimizationframe_modCPUoffload'] == True: refiner_pipeline.enable_model_cpu_offload() #Faster alternative for smaller VRAM savings. Can be coupled with attention slicing.
            if model_params['refiner_optimizationframe_attention'] == True: refiner_pipeline.enable_attention_slicing()
            
            if (model_params['refiner_optimizationframe_modCPUoffload'] != True):
                refiner_pipeline.to("cuda")
            
            image = refiner_pipeline(prompt=consolidated_prompt, negative_prompt=consolidated_negative_prompt, callback=callback, callback_steps=callback_steps,
                                     generator=generator, image=image).images
        
        torch.cuda.empty_cache() # If CUDA cache is not released, ALL generations after the first one are SUPER SLOW

        # Save the generated image
        # Create a PngInfo object to store metadata
        metadata = PngInfo()

        # Add the desired strings as text chunks in the metadata
        metadata.add_text("seed", str(new_seed))
        metadata.add_text("guidance", str(guidance_scale))
        metadata.add_text("steps", str(num_inference_steps))
        metadata.add_text("prompt", str(prompt))
        metadata.add_text("negative_prompt", str(negative_prompt))
        metadata.add_text("scheduler", scheduler_name)
        metadata.add_text("vae", str(use_vae))
        
        prompt_preset = ""
        for element in prompt_preset_buttons:
            if len(prompt_preset)>0:
                prompt_preset += "||"
            prompt_preset += str(element[0]) + "|" + str(element[1])
        metadata.add_text("prompt_preset", str(prompt_preset))
        
        negative_prompt_preset = ""
        for element in negative_prompt_preset_buttons:
            if len(negative_prompt_preset)>0:
                negative_prompt_preset += "||"
            negative_prompt_preset += str(element[0]) + "|" + str(element[1])
        metadata.add_text("negative_prompt_preset", str(negative_prompt_preset))
        
        # Finally, save the image with the metadata
        image_name = str(time.time()) # We will name this image with the current timestamp
        image.save(f"{self._script_path}\generated images\{image_name}.png", pnginfo=metadata)

        # Display the generated image on the user interface
        ## ::This line gets rid of the warning, but the current behiavior may be desirable since we want the ACTUAL image size as an
        ## ::output, so it's commented for now
        ##img = ctk.CTkImage(image)
        #img = ImageTk.PhotoImage(image)
        target_image_object.configure(image=image, seed = new_seed, guidance = guidance_scale, steps = num_inference_steps,
                                      prompt = str(prompt), prompt_preset_buttons = prompt_preset_buttons, 
                                      negative_prompt = str(negative_prompt), negative_prompt_preset_buttons = negative_prompt_preset_buttons,
                                      scheduler = scheduler_name, vae = use_vae)

        # Call the process that informs that the process ended
        if not (process_finished_callable == None):
            process_finished_callable()