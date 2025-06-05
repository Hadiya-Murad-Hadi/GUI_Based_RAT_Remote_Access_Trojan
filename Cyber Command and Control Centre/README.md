# Cyber Command and Control Centre

An educational-purpose remote management system demonstrating network programming and system administration concepts. This project implements a graphical command center (server) and remote client with advanced monitoring capabilities.

> **Note**: This software is intended for educational purposes only to demonstrate network programming concepts.

## Features

### Server (Command Center)
- Modern, cyberpunk-themed GUI with real-time status updates
- Multi-client management with live connection tracking
- Secure command transmission with length-prefixed messaging
- Enhanced logging system with color-coded messages
- Animated interface elements for better user feedback

### Client Capabilities
- System reconnaissance and information gathering
- Remote shell access with command execution
- File system management (browse, upload, download)
- Screen capture functionality
- Webcam access and control
- Audio recording and monitoring
- Automatic reconnection with exponential backoff

### Security Features
- Socket-based communication with error handling
- Threaded command processing
- Resource cleanup on disconnection
- Configurable server host/port

## Prerequisites

### Server Requirements
- Python 3.x
- tkinter (Python's standard GUI library)
- PIL (Python Imaging Library) for image processing

### Client Requirements
- Python 3.x
- OpenCV (cv2) for webcam functionality
- PyAudio for audio capture
- PIL for screenshot capability

## Installation

1. Clone or download the repository
2. Install the required Python packages:
```bash
pip install pillow        # For image processing
pip install opencv-python # For webcam functionality
pip install pyaudio      # For audio capture
```

## Usage

### Starting the Server
1. Run the server script:
```bash
python remoteServer.py
```
2. Configure the desired host and port in the GUI
3. Click "ACTIVATE SERVER" to start listening for connections

### Connecting a Client
1. Edit the client script to set the server's IP address and port:
```python
host = 'YOUR_SERVER_IP'  # Replace with your server's IP
port = 4444             # Match the server's port
```
2. Run the client script:
```bash
python remoteClient.py
```

### Command Center Features

#### System Reconnaissance
- View detailed system information
- Monitor connected clients
- Track connection status

#### Remote Control
- Execute system commands
- Browse remote file system
- Capture screenshots
- Access webcam feed
- Record audio
- Manage multiple clients

## Interface

### Server GUI
- Server Configuration Panel
- Active Targets Display
- Command Center
- System Log
- Status Indicators

### Control Features
- Start/Stop Server
- Client Selection
- Command Execution
- File Management
- Media Controls

## Development

The project is structured in two main components:

- `remoteServer.py`: The command and control center with GUI
- `remoteClient.py`: The remote client with monitoring capabilities

### Project Structure
```
Cyber Command and Control Centre/
├── remoteServer.py  # Server implementation
├── remoteClient.py  # Client implementation
└── README.md       # Documentation
```

## Technical Details

### Communication Protocol
- Socket-based client-server architecture
- JSON-formatted command and response messages
- Length-prefixed message framing
- Threading for concurrent client handling

### Security Considerations
- Input validation
- Resource cleanup
- Error handling
- Connection management

## Contributing

This project is intended for educational purposes. Contributions that improve the educational value or demonstrate additional network programming concepts are welcome.

## License

This project is provided for educational purposes only. Use responsibly and in accordance with applicable laws and regulations.

## Disclaimer

This software is created for educational purposes to demonstrate network programming and system administration concepts. Any use of this software for unauthorized access to computer systems is strictly prohibited.
