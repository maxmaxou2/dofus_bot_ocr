# Dofus Bot OCR

An automated bot for Dofus 2 treasure hunts using OCR (Optical Character Recognition) and image pattern recognition. This bot can automatically navigate through treasure hunts, fight treasure chests, and handle various game mechanics.

## Features

- Automatic treasure hunt navigation
- OCR-based position detection and map reading
- Image pattern recognition for game elements
- Automated combat with treasure chests
- Phorreur detection and handling
- Automatic zaap (teleport) usage
- Smart pathfinding based on in-game clues
- Handles special map cases (stairs, split maps)

## Requirements

- Python 3.x
- Tesseract OCR
- Windows OS (tested on Windows 10)
- Dofus 2.x client

### Python Dependencies

```
opencv-python
numpy
mss
Pillow
pyautogui
pytesseract
pywin32
pyperclip
```

## Setup

1. Install Tesseract OCR:
   - Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
   - Default installation path should be: `C:\Program Files\Tesseract-OCR\`

2. Install Python dependencies:
   ```bash
   pip install opencv-python numpy mss Pillow pyautogui pytesseract pywin32 pyperclip
   ```

3. Configure your game:
   - Set Dofus client to windowed mode
   - Ensure the game window is visible and not minimized
   - Position the window appropriately (the bot will handle window positioning)

## Usage

1. Start Dofus and log into your character
2. Navigate to a location where you can start treasure hunts
3. Run the main script:
   ```bash
   python treasure_hunt.py
   ```

The bot will:
1. Position the Dofus window
2. Start the treasure hunt sequence
3. Automatically navigate through maps
4. Handle combat with treasure chests
5. Repeat the process for new treasure hunts

## Project Structure

- `treasure_hunt.py`: Main bot logic and window management
- `ocr.py`: OCR-related functions for reading game text
- `move.py`: Movement and navigation functions
- `clues.py`: Treasure hunt clue interpretation
- `patternReck.py`: Pattern recognition for map elements
- `mineralReck.py`: Resource gathering functionality
- `proxy.py`: Proxy handling for network operations
- `windowsData.py`: Windows-specific window management
- `images/`: Directory containing reference images for pattern matching

## Important Notes

- This bot is for educational purposes only
- Use at your own risk - botting may be against game terms of service
- The bot requires specific window positioning and game settings
- Some features may need adjustment based on your screen resolution
- Make sure to test in safe areas first

## Troubleshooting

- If OCR fails, check Tesseract installation and path
- If image recognition fails, verify game resolution matches bot settings
- Window positioning issues can be adjusted in windowsData.py
- Combat issues may require adjusting timing parameters

## Contributing

Feel free to submit issues and enhancement requests. PRs are welcome.

## License

This project is provided as-is for educational purposes.