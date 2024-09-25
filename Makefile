.ONESHELL:
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
MAIN_FILE = main.py
ICON_NAME = assets/doctor.png

# Default target
all: install_requirements install_models create_shortcut run

# Install required Python packages
install_requirements: requirements.txt
	$(PIP) install -r requirements.txt
	
# Download Hugging Face models and save them to the correct paths
install_models: install_requirements
	$(PYTHON) -c "\
	from huggingface_hub import snapshot_download; \
	snapshot_download(repo_id='$(NER_MODEL_REPO)', local_dir= '$(NER_MODEL_PATH)', ignore_patterns='*.whl'); \
	snapshot_download(repo_id='$(BIRADS_MODEL_REPO)', local_dir= '$(BIRADS_MODEL_PATH)', ignore_patterns='*.whl'); \
	"

# Create a desktop shortcut for the app
create_shortcut: chmod_main_py create_launcher_desktop chmod_launcher

# Make main.py executable
chmod_main_py:
	chmod +x $(MAIN_FILE)

# Create launcher.desktop file
create_launcher_desktop:
	touch launcher.desktop
	echo "[Desktop Entry]" > launcher.desktop
	echo "Type=Application" >> launcher.desktop
	echo "Name=Mammo Lingua" >> launcher.desktop
	echo "Exec=$(shell which python) $(shell readlink -f main.py)" >> launcher.desktop
	echo "Icon=$(shell readlink -f $(ICON_NAME))" >> launcher.desktop
	echo "Terminal=false" >> launcher.desktop
	echo "Categories=Utility;" >> launcher.desktop
	mv launcher.desktop ~/Desktop

# Make launcher.desktop executable
chmod_launcher:
	gio set ~/Desktop/launcher.desktop metadata::trusted true
	chmod a+x ~/Desktop/launcher.desktop
	
.PHONY: all venv install_requirements install_models build clean clean_build run create_shortcut chmod_main_py create_launcher_desktop chmod_launcher
