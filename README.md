# Vision

The unified computer vision server based on the AES 5 Domains Architecture.

## Architecture
The server is structured into modular domains (Max Depth 5):
- `src/taxonomy/`: Data models (DNA)
- `src/capabilities/`: Business logic slice endpoints
- `src/infrastructure/`: Technology adapters (OpenCV, FFmpeg, Tesseract)
- `src/surfaces/`: MCP Interface for the agent
- `src/main.py`: Bootstrap wiring and initialization
