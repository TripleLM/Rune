#!/usr/bin/env python3
"""
Setup script for Rune
"""
import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("setup")

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        logger.error("Python 3.9 or higher is required")
        return False
    
    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.error("pip is not installed or not working")
        return False
    
    return True

def install_requirements():
    """Install required packages"""
    logger.info("Installing requirements...")
    
    req_path = Path("requirements.txt")
    if not req_path.exists():
        logger.error("requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_path)])
        logger.info("Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        return False

def download_models():
    """Download required AI models"""
    logger.info("Setting up AI models...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # TODO: Implement actual model downloading
    # This would download compact LLMs suitable for Raspberry Pi
    
    logger.info("Models setup complete")
    return True

def configure_device():
    """Configure the device"""
    logger.info("Configuring device...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Ensure default config exists
    default_config = config_dir / "default.yml"
    if not default_config.exists():
        logger.error("Default configuration file not found")
        return False
    
    # TODO: Auto-detect hardware and update configuration
    
    logger.info("Device configuration complete")
    return True

def setup_autostart():
    """Set up autostart on boot"""
    logger.info("Setting up autostart...")
    
    # Create systemd service file
    service_content = """[Unit]
Description=Rune AI Assistant
After=network.target

[Service]
ExecStart=/usr/bin/python3 {}/src/rune.py
WorkingDirectory={}
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
""".format(os.path.abspath("."), os.path.abspath("."))
    
    # Write service file
    service_path = Path("rune.service")
    with open(service_path, "w") as f:
        f.write(service_content)
    
    logger.info(f"Created service file at {service_path}")
    logger.info("To enable autostart, run:")
    logger.info(f"  sudo cp {service_path} /etc/systemd/system/")
    logger.info("  sudo systemctl enable rune.service")
    
    return True

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Rune setup script")
    parser.add_argument("--skip-dependencies", action="store_true", help="Skip dependency checks")
    parser.add_argument("--skip-requirements", action="store_true", help="Skip installing requirements")
    parser.add_argument("--skip-models", action="store_true", help="Skip downloading models")
    parser.add_argument("--skip-config", action="store_true", help="Skip device configuration")
    parser.add_argument("--skip-autostart", action="store_true", help="Skip autostart setup")
    args = parser.parse_args()
    
    logger.info("Starting Rune setup...")
    
    # Run setup steps
    steps = [
        ("Checking dependencies", check_dependencies, args.skip_dependencies),
        ("Installing requirements", install_requirements, args.skip_requirements),
        ("Downloading models", download_models, args.skip_models),
        ("Configuring device", configure_device, args.skip_config),
        ("Setting up autostart", setup_autostart, args.skip_autostart)
    ]
    
    all_success = True
    for step_name, step_func, skip in steps:
        if skip:
            logger.info(f"Skipping: {step_name}")
            continue
        
        logger.info(f"Running: {step_name}")
        success = step_func()
        if not success:
            logger.error(f"Step failed: {step_name}")
            all_success = False
            break
    
    if all_success:
        logger.info("Setup completed successfully!")
        logger.info("To start Rune, run: python src/rune.py")
    else:
        logger.error("Setup failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 