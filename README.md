# Mammo Lingua - Name Entity Recognition and BIRADS Classification Program




https://github.com/user-attachments/assets/c75f9f98-d676-4402-bddd-23fa06dae3dd




<img align="right" width="250" height="250" src="https://github.com/ahmetcangunay/mammo_lingua/blob/main/assets/doctor.png">



# Introduction
**Mammo Lingua** is a GUI application for Name Entity Recognition (NER) and BIRADS Classification. The application is built using Python with PyQt5 for the GUI and SpaCy for NER. The goal is to provide a tool that can analyze medical texts, identify named entities, and classify BIRADS categories.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)
- [License](#license)

## Installation

### Prerequisites
- Python 3.10+

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/mammo-lingua.git
   cd mammo-lingua
   bash app.sh

***All other installation procedures will be completed automatically with app.sh and Makefile files. The other procedures are listed as follows.***

* **Virtual Environment Setup:** With the app.sh file, an environment named “.venv” is created in the current location where the main file is located and all modules in requirements.txt are transferred to this structure.
* **Makefile Setup Operations:** With the help of the Makefile file, the following operations are performed respectively:
  - **Loading LLM models:** In order to use the program, the NLP models embedded in Huggingface need to be integrated into the system. At this point, the “install_models” method in the Makefile will download the [Name Entity Recognition](https://huggingface.co/ahmet1338/MammoTagger) and [Birads Classification](https://huggingface.co/ahmet1338/MammoBiradsScore) methods from Huggingface and complete their installation.
  - **Creation of a desktop shortcut:** The “create_shortcut” method in the Makefile allows users to easily create a shortcut on the desktop.
 
## Usage
### Run the application

To start the application, you can use the .desktop shortcut in your desktop.

### Uploading and Processing Files
1. Click on Upload File to upload a text file for analysis.
2. Once the file is uploaded, click Show Results to view the NER and BIRADS classification results.
3. You can also Save Results to export the analysis as a JSON file.

## Features

* **Custom GUI:** A modern, dark-themed user interface built with PyQt5.
* **NER Analysis:** Automatically extracts medical entities (e.g., anatomy, observations) from the text.
* **BIRADS Classification:** Classifies the text based on BIRADS categories using a pre-trained model.
* **File Upload and Save:** Upload medical text files for analysis and save the results in JSON format.
* **Dark Mode:** Dark theme for enhanced readability.

## Dependencies

This project relies on the following Python packages:

    PyQt5==5.15.11
    spacy==3.7.6
    transformers==4.36.2
    torch==2.4.1
    requests==2.32.3
    # More dependencies can be found in requirements.txt

For a full list, refer to the requirements.txt file.

## Configuration
* **Model Paths:** The application expects the NER and BIRADS models to be located in `data/nlp_models/`. You can update the paths in `main.py` if needed:
```
birads_model_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "data/nlp_models/classification_model")
ner_model_path = ner_model_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "data/nlp_models/ner_model")
```

## Examples

Here's an example of how to use the tool:

1. Start the application.
2. Upload a medical text file (e.g., a report).
3. View the identified entities and BIRADS classification.
4. Save the results as a JSON file for further analysis.

## Troubleshooting

* **Models not loading:** Ensure the NER and BIRADS models are correctly placed in the `data/nlp_models/` folder.
* **Dependencies issues:** Double-check that all dependencies listed in `requirements.txt` are installed correctly.

## Contributors
[Ahmet Can GÜNAY](https://github.com/ahmetcangunay) :shipit:

## License
> [!IMPORTANT]
> This project is licensed under the CC BY-NC-SA 4.0 License. See the [LICENSE](https://creativecommons.org/licenses/by-nc-sa/4.0/) file for details.
