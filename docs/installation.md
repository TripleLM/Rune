# Rune Installation Guide

This guide will help you set up Rune on your Raspberry Pi CM5.

## Hardware Requirements

Before starting the installation, make sure you have the following hardware:

- Raspberry Pi Compute Module 5 (8GB RAM recommended)
- Compatible carrier board
- MicroSD card (64GB recommended)
- Microphone (USB or I2S)
- Speaker or audio output device
- Push-to-talk button
- Power button
- Case/enclosure (optional but recommended)

## Software Prerequisites

- Raspberry Pi OS (64-bit recommended)
- Python 3.9 or higher
- Git

## Step 1: Prepare the Raspberry Pi

1. Flash Raspberry Pi OS to your MicroSD card.
2. Boot the Raspberry Pi and complete the initial setup.
3. Open a terminal and update the system:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

## Step 2: Install Dependencies

Install the required system dependencies:

```bash
sudo apt install -y python3-pip python3-venv python3-dev git portaudio19-dev
```

## Step 3: Clone the Repository

```bash
git clone https://github.com/TripleLM/Rune.git
cd Rune
```

## Step 4: Run the Setup Script

The setup script will install Python dependencies, download required AI models, and configure the system:

```bash
python3 setup.py
```

This process may take some time as it downloads and sets up the AI models.

## Step 5: Configure Hardware

### Microphone

Make sure your microphone is properly connected and recognized by the system:

```bash
arecord -l
```

You should see your microphone listed. If needed, adjust the configuration in `config/default.yml` to specify the correct input device.

### Speaker

Test the speaker output:

```bash
aplay -l
speaker-test -t wav
```

### Push-to-Talk Button

Connect the push-to-talk button to GPIO pin 17 (by default). The button should connect the GPIO pin to ground when pressed.

## Step 6: Set Up Autostart (Optional)

To make Rune start automatically when the Raspberry Pi boots:

```bash
sudo cp rune.service /etc/systemd/system/
sudo systemctl enable rune.service
sudo systemctl start rune.service
```

## Step 7: Test the System

Start Rune manually to test if everything is working correctly:

```bash
python3 src/rune.py
```

Press the push-to-talk button and speak. Rune should respond either with voice or Morse code output.

## Troubleshooting

### Audio Issues

If you have issues with audio input or output:

1. Check that your devices are properly connected
2. Make sure they're not muted in the system
3. Try running `pavucontrol` to check audio levels

### GPIO Issues

If the push-to-talk button isn't working:

1. Check the wiring connections
2. Make sure the proper GPIO pin is specified in the config
3. Test the button with a simple GPIO test script

### Performance Issues

If the AI assistant is running slowly:

1. Make sure you're using a Raspberry Pi with sufficient RAM (8GB recommended)
2. Consider using a lower-footprint AI model in the configuration
3. Close other applications to free up system resources 