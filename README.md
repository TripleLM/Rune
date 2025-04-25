# Rune - Offline Local AI Assistant

Rune is an open-source, completely offline AI voice assistant that runs on a Raspberry Pi CM5. It's designed to respect privacy by operating entirely locally without sending any data to external servers.

## Features

- **100% Offline Operation**: All processing happens on-device
- **Voice Interaction**: Natural voice input and output
- **Single Button Interface**: Simple push-to-talk operation
- **Morse Code Support**: Can interpret and generate morse code
- **Open Source**: Fully customizable and transparent

## Hardware Requirements

- Raspberry Pi Compute Module 5 (8GB RAM model)
- 64GB storage
- Microphone
- Speaker
- Push-to-talk button
- Power button
- Case/enclosure

## Getting Started

### Prerequisites

- Raspberry Pi OS (64-bit recommended)
- Python 3.9+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/TripleLM/Rune.git
cd Rune

# Install dependencies
pip install -r requirements.txt

# Configure the device
python setup.py

# Run the assistant
python src/rune.py
```

## Project Structure

- `src/`: Core source code
  - `audio/`: Audio processing components
  - `morse/`: Morse code interpreter and generator
  - `assistant/`: AI assistant modules
  - `interface/`: Button interface and interaction logic
- `config/`: Configuration files
- `models/`: Local AI models
- `docs/`: Documentation
- `scripts/`: Helper scripts
- `tests/`: Test suite

## Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 
