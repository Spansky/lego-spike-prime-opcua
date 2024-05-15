# Makefile for Python Project and Systemd Service

# Variables
VENV_DIR = .venv
PYTHON = python
PIP = $(VENV_DIR)/bin/pip
ACTIVATE = $(VENV_DIR)/bin/activate
REQUIREMENTS = requirements.txt
REQUIREMENTS_TIMESTAMP = .requirements_installed
SERVICE_NAME = lego-spike-prime-opcua
SERVICE_FILE_DEST = /etc/systemd/system/$(SERVICE_NAME).service
SRC_DIR = src
REPO_PATH = $(CURDIR)
EXEC_START = $(REPO_PATH)/$(VENV_DIR)/bin/python $(REPO_PATH)/$(SRC_DIR)/main.py

# Default target
all: install

# Create virtual environment
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)

# Install dependencies only if requirements.txt has changed
$(REQUIREMENTS_TIMESTAMP): $(REQUIREMENTS) $(VENV_DIR)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(REQUIREMENTS_TIMESTAMP)

# Install target depends on the timestamp file
install: $(REQUIREMENTS_TIMESTAMP)

# Run the application
run: install
	bash -c 'source $(ACTIVATE) && $(PYTHON) $(SRC_DIR)/main.py'

# Lint the project
lint: install
	$(PIP) install flake8
	bash -c 'source $(ACTIVATE) && flake8 $(SRC_DIR)/.'

# Clean the project
clean:
	rm -rf $(VENV_DIR) $(REQUIREMENTS_TIMESTAMP)

# Remove Python bytecode files
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

# Clean all
clean-all: clean clean-pyc

# Create systemd service file
$(SERVICE_FILE_DEST):
	@echo "[Unit]" | sudo tee $(SERVICE_FILE_DEST)
	@echo "Description=OPCUA Server for Lego Spike Prime" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "After=multi-user.target" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "[Service]" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "Type=simple" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "Restart=always" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "ExecStart=$(EXEC_START)" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "[Install]" | sudo tee -a $(SERVICE_FILE_DEST)
	@echo "WantedBy=multi-user.target" | sudo tee -a $(SERVICE_FILE_DEST)
	sudo systemctl daemon-reload

# Enable the service
enable-service: $(SERVICE_FILE_DEST)
	sudo systemctl enable $(SERVICE_NAME)

# Start the service
start-service: $(SERVICE_FILE_DEST)
	sudo systemctl start $(SERVICE_NAME)

# Stop the service
stop-service:
	sudo systemctl stop $(SERVICE_NAME)

# Restart the service
restart-service: $(SERVICE_FILE_DEST)
	sudo systemctl restart $(SERVICE_NAME)

# Uninstall the service
uninstall-service: stop-service
	sudo systemctl disable $(SERVICE_NAME)
	sudo rm -f $(SERVICE_FILE_DEST)
	sudo systemctl daemon-reload

.PHONY: all install run lint clean clean-pyc clean-all enable-service start-service stop-service restart-service uninstall-service
