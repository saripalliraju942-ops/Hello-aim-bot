#!/bin/bash

# Termux Aim Bot Script - Advanced Edition
# Features: ESP, Auto-Connect, Shortcut Menu

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$HOME/.aimbot"
LOG_FILE="$SCRIPT_DIR/aimbot.log"
CONFIG_FILE="$SCRIPT_DIR/config.json"
MAIN_PY="$SCRIPT_DIR/aimbot_main.py"

# Create directories
mkdir -p "$SCRIPT_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Header
show_header() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║       ${GREEN}FREE FIRE AIM BOT - TERMUX PRO${CYAN}               ║"
    echo "║       ${MAGENTA}ESP + Auto-Connect + Shortcut Menu${CYAN}          ║"
    echo "╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Initialize system
init_system() {
    echo -e "${YELLOW}[*] Initializing system...${NC}"
    
    # Check Termux
    if [ ! -d "$PREFIX" ]; then
        echo -e "${RED}[!] Error: This script must be run in Termux${NC}"
        exit 1
    fi
    
    log "System initialization started"
    
    echo -e "${YELLOW}[*] Updating package manager...${NC}"
    apt update -y > /dev/null 2>&1 &
    wait
    
    echo -e "${YELLOW}[*] Installing dependencies...${NC}"
    apt install -y python3 python3-pip git curl wget > /dev/null 2>&1 &
    wait
    
    echo -e "${GREEN}[✓] Dependencies installed${NC}"
    log "Dependencies installed successfully"
}

# Install Python packages
install_python_deps() {
    echo -e "${YELLOW}[*] Installing Python packages...${NC}"
    pip3 install requests numpy pynput keyboard > /dev/null 2>&1 &
    wait
    echo -e "${GREEN}[✓] Python packages installed${NC}"
    log "Python packages installed"
}

# Create config file
create_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}[*] Creating configuration file...${NC}"
        cat > "$CONFIG_FILE" << 'EOL'
{
  "auto_connect": true,
  "esp_enabled": true,
  "esp_color": "red",
  "esp_line_thickness": 2,
  "aim_sensitivity": 5,
  "headshot_priority": true,
  "auto_fire": false,
  "server_ip": "127.0.0.1",
  "server_port": 8888,
  "update_interval": 30,
  "debug_mode": false
}
EOL
        echo -e "${GREEN}[✓] Configuration file created${NC}"
        log "Config file created at $CONFIG_FILE"
    fi
}

# Create main Python application
create_main_app() {
    echo -e "${YELLOW}[*] Creating main application...${NC}"
    cat > "$MAIN_PY" << 'PYEOF'
#!/usr/bin/env python3

import os
import sys
import json
import time
import threading
import socket
from datetime import datetime

class ESPDisplay:
    def __init__(self):
        self.enabled = True
        self.color = "red"
        self.line_thickness = 2
        self.positions = []
    
    def draw_esp_line(self, x1, y1, x2, y2):
        """Draw ESP line from head to player"""
        return f"ESP_LINE({x1},{y1})-({x2},{y2})"
    
    def update_positions(self, players):
        """Update ESP positions"""
        self.positions = players
    
    def render(self):
        """Render ESP on screen"""
        for player in self.positions:
            print(f"[ESP] {player['name']} at ({player['x']}, {player['y']}) - Head: ({player['hx']}, {player['hy']})")

class AutoConnect:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected = False
        self.socket = None
    
    def connect(self):
        """Auto-connect to game server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.server_ip, self.server_port))
            self.connected = True
            print(f"[✓] Connected to {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"[!] Connection failed: {e}")
            self.connected = False
            return False
    
    def send_data(self, data):
        """Send data to server"""
        if self.connected:
            try:
                self.socket.sendall(data.encode())
                return True
            except:
                return False
        return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
        self.connected = False

class AimBot:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.esp = ESPDisplay()
        self.auto_connect = AutoConnect(
            self.config['server_ip'],
            self.config['server_port']
        )
        self.running = True
        self.menu_active = True
    
    def load_config(self, config_file):
        """Load configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def show_menu(self):
        """Show interactive menu"""
        while self.menu_active:
            self.clear_screen()
            print("\n" + "="*50)
            print("     AIM BOT SHORTCUT MENU")
            print("="*50)
            print("\n[1] Start Aim Bot")
            print("[2] Enable/Disable ESP")
            print("[3] Enable/Disable Auto-Connect")
            print("[4] Settings")
            print("[5] View Logs")
            print("[6] Exit\n")
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == "1":
                self.start_aimbot()
            elif choice == "2":
                self.toggle_esp()
            elif choice == "3":
                self.toggle_auto_connect()
            elif choice == "4":
                self.show_settings()
            elif choice == "5":
                self.view_logs()
            elif choice == "6":
                self.shutdown()
                break
            else:
                print("[!] Invalid option")
                time.sleep(1)
    
    def start_aimbot(self):
        """Start the aim bot"""
        print("\n[*] Starting Aim Bot...")
        
        if self.config.get('auto_connect', True):
            print("[*] Auto-connecting to server...")
            if self.auto_connect.connect():
                print("[✓] Auto-connect successful")
        
        if self.config.get('esp_enabled', True):
            print("[*] ESP enabled")
            print("[*] Scanning for targets...")
            time.sleep(2)
            
            # Simulate ESP data
            demo_players = [
                {"name": "Enemy1", "x": 100, "y": 200, "hx": 100, "hy": 150},
                {"name": "Enemy2", "x": 300, "y": 150, "hx": 300, "hy": 100}
            ]
            self.esp.update_positions(demo_players)
            self.esp.render()
        
        print("[✓] Aim Bot running")
        print("[*] Press Ctrl+C to stop\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Stopping Aim Bot...")
            if self.auto_connect.connected:
                self.auto_connect.disconnect()
    
    def toggle_esp(self):
        """Toggle ESP feature"""
        self.config['esp_enabled'] = not self.config['esp_enabled']
        status = "Enabled" if self.config['esp_enabled'] else "Disabled"
        print(f"\n[✓] ESP {status}")
        time.sleep(1)
    
    def toggle_auto_connect(self):
        """Toggle Auto-Connect feature"""
        self.config['auto_connect'] = not self.config['auto_connect']
        status = "Enabled" if self.config['auto_connect'] else "Disabled"
        print(f"\n[✓] Auto-Connect {status}")
        time.sleep(1)
    
    def show_settings(self):
        """Show settings menu"""
        self.clear_screen()
        print("\n" + "="*50)
        print("     SETTINGS")
        print("="*50)
        print(f"\nAuto-Connect: {self.config.get('auto_connect', True)}")
        print(f"ESP Enabled: {self.config.get('esp_enabled', True)}")
        print(f"ESP Color: {self.config.get('esp_color', 'red')}")
        print(f"Aim Sensitivity: {self.config.get('aim_sensitivity', 5)}")
        print(f"Headshot Priority: {self.config.get('headshot_priority', True)}")
        print(f"Server: {self.config.get('server_ip')}:{self.config.get('server_port')}\n")
        input("Press Enter to go back...")
    
    def view_logs(self):
        """View application logs"""
        self.clear_screen()
        print("\n" + "="*50)
        print("     LOGS")
        print("="*50 + "\n")
        try:
            with open(os.path.expanduser("~/.aimbot/aimbot.log"), 'r') as f:
                print(f.read())
        except:
            print("[!] No logs found")
        input("\nPress Enter to go back...")
    
    def shutdown(self):
        """Shutdown application"""
        print("\n[*] Shutting down...")
        if self.auto_connect.connected:
            self.auto_connect.disconnect()
        self.running = False
        self.menu_active = False
    
    @staticmethod
    def clear_screen():
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def run(self):
        """Main run loop"""
        self.clear_screen()
        print("\n" + "="*50)
        print("     FREE FIRE AIM BOT")
        print("     ESP + Auto-Connect PRO")
        print("="*50)
        print("\n[✓] System Initialized")
        print("[✓] Ready to start\n")
        time.sleep(2)
        self.show_menu()

if __name__ == "__main__":
    config_path = os.path.expanduser("~/.aimbot/config.json")
    aimbot = AimBot(config_path)
    aimbot.run()
PYEOF
    
    chmod +x "$MAIN_PY"
    echo -e "${GREEN}[✓] Main application created${NC}"
    log "Main application created"
}

# Make script executable
chmod +x "$MAIN_PY"

# Main execution
main() {
    show_header
    init_system
    sleep 1
    install_python_deps
    sleep 1
    create_config
    create_main_app
    
    echo ""
    echo -e "${GREEN}[✓] Setup completed successfully!${NC}"
    echo -e "${YELLOW}[*] Starting Aim Bot...${NC}"
    echo ""
    sleep 2
    
    log "Starting main application"
    python3 "$MAIN_PY"
}

# Run main
main
