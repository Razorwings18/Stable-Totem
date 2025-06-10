# WARNING!
This project is an UNMAINTAINED, UNPOLISHED work in progress.

# Stable Totem - A GUI for Diffusion Models

Stable Totem is a user-friendly desktop application for generating images from text prompts using diffusion models like Stable Diffusion. It provides a simple, intuitive interface for beginners while offering a few, more advanced options.

The goal is to streamline the image generation process, manage model presets, and keep your generated art organized, all within a single, self-contained application.

![screenshot](https://github.com/user-attachments/assets/aa03acfb-410e-4672-b23f-59c059979962)

## Features

-   **Intuitive User Interface:** A clean layout designed to make generating images straightforward.
-   **Model Preset Management:** Easily add, configure, and switch between different Stable Diffusion models (e.g., SD 1.5, SDXL, custom-trained models).
-   **Full Parameter Control:** Adjust seed, inference steps, guidance scale, image dimensions, and schedulers.
-   **Advanced Prompting:** Utilizes `compel` for prompt weighting (e.g., `(word)++` for emphasis).
-   **Prompt Preset System:** Save and load collections of frequently used positive or negative prompts to speed up your workflow.
-   **Image Gallery:** Automatically displays a history of your generated images as thumbnails, allowing you to easily view and reload their generation data.
-   **Click-to-Load:** Simply click a previously generated image to load its seed, prompt, and all other parameters back into the UI.

## Installation

Follow these steps to get Stable Totem running on your local machine.

### Step 1: Clone the Repository

First, clone this repository to your computer using Git.

```bash
git clone https://github.com/your-username/stable-totem.git
cd stable-totem
```

### Step 2: Set Up a Python Environment

It is highly recommended to use a virtual environment to manage dependencies and avoid conflicts with other Python projects.

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

This application requires several Python libraries, most importantly PyTorch with CUDA support for GPU acceleration.

1.  **Install PyTorch:** Visit the official [PyTorch website](https://pytorch.org/get-started/locally/) and find the correct command for your system (Windows/Linux, Pip, and your CUDA version). An example command for CUDA 12.1 is:
    ```bash
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```

2.  **Install Other Required Libraries:** Once PyTorch is installed, install the rest of the dependencies from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
    This will install libraries such as `diffusers`, `customtkinter`, `compel`, and `Pillow`.

### Step 4: Set up your HuggingFace token

Edit **authtoken.py** and enter your HuggingFace token. You can find a link on how to get your own in that file.

### Step 5: Run the Application

Once all dependencies are installed, you can launch the application by running the `app.py` script.

```bash
python app.py
```

## Setup: Adding Models

The application is just an interface; you need to provide the actual diffusion models for it to work.

### 1. Download a Model

You can download pre-trained models from a source like [Hugging Face](https://huggingface.co/). For example, to get the base Stable Diffusion XL 1.0 model, you would download all of its files.

### 2. Place the Model in the Correct Folder

The application expects models to be located in the `models` directory. Create a subfolder for each model.

Your file structure should look like this:

```
stable-totem/
├── models/
│   ├── stable-diffusion-xl-base-1.0/   <-- Place all model files here
│   │   ├── model_index.json
│   │   ├── text_encoder/
│   │   ├── unet/
│   │   └── ...and so on
│   └── (other models can be added here in their own folders)
├── generated images/
├── app.py
└── ...
```

### 3. Configure the Model in the Application

After placing the model files, you must tell Stable Totem about it.

1.  Launch the application (`python app.py`).
2.  Click the **SETTINGS** button in the top bar.
3.  In the settings window, ensure you are on the **Model** -> **Text to Image** tab.
4.  Click the **New File** icon to create a new model preset.
5.  In the right-hand panel:
    -   **Model preset name:** Give your preset a memorable name (e.g., "SDXL 1.0 Base").
    -   **Main model path:** Click the **Browse** icon and navigate to the folder where you placed your model (e.g., `stable-totem/models/stable-diffusion-xl-base-1.0`).
    -   **Options:** Check the box `This preset is for SDXL models` if you are using an SDXL model. Configure other optimizations as needed.
6.  Click **Apply**.
7.  Close the settings window.

Your model is now configured and ready to use!

## How to Generate Your First Image

1.  On the main screen, click the **Model Preset** dropdown menu and select the preset you just configured (e.g., "SDXL 1.0 Base").
2.  Click the **Load** icon next to the dropdown to load the model into memory.
3.  In the **Prompt** text box, type a description of the image you want to create (e.g., `a majestic lion in a futuristic city, cinematic lighting`).
4.  (Optional) In the **Negative Prompt** box, type things you want to avoid (e.g., `blurry, cartoon, watermark`).
5.  Click the large **Generate!** button at the bottom.

After a moment, your generated image will appear in the center of the screen, and a thumbnail will be added to the gallery on the right. You can now save the image, or click its thumbnail later to reload all its settings.

---

This application was created by **Diego Wasser** (Razorwings18).  
[GitHub Profile](https://github.com/razorwings18)
