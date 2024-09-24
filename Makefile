# Model Repository: https://huggingface.co/ahmet1338
NER_MODEL_REPO = ahmet1338/MammoTagger
BIRADS_MODEL_REPO = ahmet1338/MammoBiradsScore
# Python environment settings
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Hugging Face models paths
NER_MODEL_PATH = data/nlp_models/ner_model
BIRADS_MODEL_PATH = data/nlp_models/classification_model

# PyInstaller settings
PYINSTALLER = $(VENV)/bin/pyinstaller
APP_NAME = mammo_lingua
MAIN_FILE = main.py

# Default target
all: venv install_requirements install_models run

# Create virtual environment
venv:
	python3 -m venv $(VENV)

# Install required Python packages
install_requirements:
	$(PIP) install -r requirements.txt
	$(PIP) install pyinstaller

# Download Hugging Face models and save them to the correct paths
install_models:
	$(PYTHON) -c "\
	from huggingface_hub import snapshot_download; \
	snapshot_download(repo_id='$(NER_MODEL_REPO)', local_dir= '$(NER_MODEL_PATH)', ignore_patterns='*.whl'); \
	snapshot_download(repo_id='$(BIRADS_MODEL_REPO)', local_dir= '$(BIRADS_MODEL_PATH)', ignore_patterns='*.whl'); \
	"

# Build the executable using PyInstaller
build: install_models
	$(PYINSTALLER) --onefile \
	--add-data "$(NER_MODEL_PATH):data/nlp_models/ner_model" \
	--add-data "$(BIRADS_MODEL_PATH):data/nlp_models/classification_model" \
	--name $(APP_NAME) $(MAIN_FILE)

# Clean the build directory
clean:
	rm -rf build dist *.spec $(VENV)

# Clean only build files (but keep virtual environment)
clean_build:
	rm -rf build dist *.spec

# Run the app locally (for testing in venv)
run:
	$(PYTHON) $(MAIN_FILE)

.PHONY: all venv install_requirements install_models build clean clean_build run
