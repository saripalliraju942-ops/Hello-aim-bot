#!/usr/bin/env python3
"""
FREE FIRE AIM BOT - TERMUX EDITION
ESP + Auto-Connect + Shortcut Menu
Version: 1.0
"""

import os
import sys
import json
import time
import threading
import socket
from datetime import datetime

# Color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    WHITE = '\033[0;37m'
    NC = '\033[0m'  # No Color

class ESPDisplay:
    """ESP System for detecting and displaying enemy locations"""
    
    def __init__(self):
        self.enabled = True
        self.color = "red"
        self.line_thickness = 2
        self.positions = []
    
    def draw_esp_line(self, x1, y1, x2, y2):
        """Draw ESP line from position to head"""
        return f"ESP_LINE({x1},{y1})-({x2},{y2})"
    
    def update_positions(self, players):
        """Update ESP positions for players"""
        self.positions = players
    
    def render(self):
        """Render ESP display"""
        print(f"\n{Colors.CYAN}[ESP] Scanning for targets...{Colors.NC}")
        if not self.positions:
            print(f"{Colors.YELLOW}[!] No targets found{Colors.NC}")
            return
        
        for i, player in enumerate(self.positions, 1):
            line = self.draw_esp_line(player['x'], player['y'], player['hx'], player['hy'])
            print(f"{Colors.GREEN}[{i}] {player['name']}{Colors.NC} @ ({player['x']}, {player['y']}) | Head: ({player['hx']}, {player['hy']})")
            print(f"    {Colors.CYAN}{line}{Colors.NC}")

class AutoConnect:
    """Auto-connect system for server communication"""
    
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected = False
        self.socket = None
    
    def connect(self):
        """Attempt to connect to game server"""
        try:
            print(f"{Colors.YELLOW}[*] Connecting to {self.server_ip}:{self.server_port}...{Colors.NC}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3)
            self.socket.connect((self.server_ip, self.server_port))
            self.connected = True
            print(f"{Colors.GREEN}[✓] Connected successfully!{Colors.NC}")
            return True
        except socket.timeout:
            print(f"{Colors.YELLOW}[!] Connection timeout (server may be offline){Colors.NC}")
            self.connected = False
            return False
        except ConnectionRefusedError:
            print(f"{Colors.YELLOW}[!] Connection refused (server not running){Colors.NC}")
            self.connected = False
            return False
        except Exception as e:
            print(f"{Colors.RED}[!] Connection error: {e}{Colors.NC}")
            self.connected = False
            return False
    
    def send_data(self, data):
        """Send data to connected server"""
        if self.connected:
            try:
                self.socket.sendall(data.encode())
                return True
            except:
                self.connected = False
                return False
        return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        print(f"{Colors.YELLOW}[*] Disconnected{Colors.NC}")

class AimBot:
    """Main Aim Bot Application"""
    
    def __init__(self):
        self.config = {
            'auto_connect': True,
            'esp_enabled': True,
            'esp_color': 'red',
            'esp_line_thickness': 2,
            'aim_sensitivity': 5,
            'headshot_priority': True,
            'auto_fire': False,
            'server_ip': '127.0.0.1',
            'server_port': 8888,
            'update_interval': 30,
            'debug_mode': False
        }
        
        self.esp = ESPDisplay()
        self.auto_connect = AutoConnect(
            self.config['server_ip'],
            self.config['server_port']
        )
        self.running = True
        self.menu_active = True
        self.aimbot_running = False
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def show_header(self):
        """Display application header"""
        self.clear_screen()
        print(f"{Colors.CYAN}")
        print("╔" + "═"*56 + "╗")
        print("║" + " "*56 + "║")
        print("║" + f"  {Colors.GREEN}FREE FIRE AIM BOT - TERMUX PRO{Colors.CYAN}".ljust(56) + "║")
        print("║" + f"  {Colors.MAGENTA}ESP + Auto-Connect + Shortcut Menu{Colors.CYAN}".ljust(56) + "║")
        print("║" + " "*56 + "║")
        print("╚" + "═"*56 + "╝")
        print(f"{Colors.NC}")
    
    def show_menu(self):
        """Display main menu"""
        while self.menu_active:
            self.show_header()
            print(f"\n{Colors.BLUE}╔════════════════════════════════════════════════════╗{Colors.NC}")
            print(f"{Colors.BLUE}║{Colors.NC}         {Colors.YELLOW}SHORTCUT MENU{Colors.NC}                            {Colors.BLUE}║{Colors.NC}")
            print(f"{Colors.BLUE}╠════════════════════════════════════════════════════╣{Colors.NC}")
            print(f"{Colors.BLUE}║{Colors.NC}")
            print(f"{Colors.BLUE}║{Colors.NC}  {Colors.GREEN}[1]{Colors.NC} Start Aim Bot")
            print(f"{Colors.BLUE}║{Colors.NC}  {Colors.GREEN}[2]{Colors.NC} Enable/Disable ESP")
            print(f"{Colors.BLUE}║{Colors.NC}  {Colors.GREEN}[3]{Colors.NC} Enable/Disable Auto-Connect")
            print(f"{Colors.BLUE}║{Colors.NC}  {Colors.GREEN}[4]{Colors.NC} Settings")
            print(f"{Colors.BLUE}║{Colors.NC}  {Colors.GREEN}[5]{Colors.NC} View Status")
            print(f"{Colors.BLUE}║{Colors.NC}  {Colors.GREEN}[6]{Colors.NC} Exit")
            print(f"{Colors.BLUE}║{Colors.NC}")
            print(f"{Colors.BLUE}╚════════════════════════════════════════════════════╝{Colors.NC}\n")
            
            choice = input(f"{Colors.CYAN}Select option (1-6): {Colors.NC}").strip()
            
            if choice == "1":
                self.start_aimbot()
            elif choice == "2":
                self.toggle_esp()
            elif choice == "3":
                self.toggle_auto_connect()
            elif choice == "4":
                self.show_settings()
            elif choice == "5":
                self.view_status()
            elif choice == "6":
                self.shutdown()
                break
            else:
                print(f"{Colors.RED}[!] Invalid option. Please try again.{Colors.NC}")
                time.sleep(1)
    
    def start_aimbot(self):
        """Start the aim bot"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}╔════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.GREEN}║{Colors.NC}  {Colors.YELLOW}STARTING AIM BOT{Colors.NC}".ljust(57) + f"{Colors.GREEN}║{Colors.NC}")
        print(f"{Colors.GREEN}╚════════════════════════════════════════════════════╝{Colors.NC}\n")
        
        self.aimbot_running = True
        
        # Auto-connect if enabled
        if self.config['auto_connect']:
            print(f"{Colors.YELLOW}[*] Auto-Connect enabled{Colors.NC}")
            if not self.auto_connect.connect():
                print(f"{Colors.YELLOW}[!] Continuing without server connection...{Colors.NC}")
        
        # Enable ESP if enabled
        if self.config['esp_enabled']:
            print(f"{Colors.GREEN}[✓] ESP Enabled{Colors.NC}")
            print(f"{Colors.CYAN}[*] Sensitivity: {self.config['aim_sensitivity']}{Colors.NC}")
            print(f"{Colors.CYAN}[*] Headshot Priority: {self.config['headshot_priority']}{Colors.NC}")
        
        print(f"\n{Colors.GREEN}[✓] Aim Bot is {Colors.YELLOW}RUNNING{Colors.GREEN}!{Colors.NC}")
        print(f"{Colors.YELLOW}[*] Press Ctrl+C to stop\n{Colors.NC}")
        
        # Simulate aim bot operation
        try:
            demo_players = [
                {"name": "Enemy_Alpha", "x": 100, "y": 200, "hx": 105, "hy": 150},
                {"name": "Enemy_Beta", "x": 300, "y": 150, "hx": 305, "hy": 100},
                {"name": "Enemy_Gamma", "x": 200, "y": 250, "hx": 205, "hy": 200}
            ]
            
            counter = 0
            while self.aimbot_running:
                counter += 1
                print(f"{Colors.CYAN}[{counter}] Scanning... {datetime.now().strftime('%H:%M:%S')}{Colors.NC}")
                
                if counter % 3 == 0 and self.config['esp_enabled']:
                    self.esp.update_positions(demo_players)
                    self.esp.render()
                
                time.sleep(2)
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[*] Stopping Aim Bot...{Colors.NC}")
            self.aimbot_running = False
            if self.auto_connect.connected:
                self.auto_connect.disconnect()
            print(f"{Colors.GREEN}[✓] Aim Bot stopped{Colors.NC}")
            time.sleep(1)
    
    def toggle_esp(self):
        """Toggle ESP feature"""
        self.clear_screen()
        self.config['esp_enabled'] = not self.config['esp_enabled']
        status = f"{Colors.GREEN}ENABLED{Colors.NC}" if self.config['esp_enabled'] else f"{Colors.RED}DISABLED{Colors.NC}"
        
        print(f"\n{Colors.BLUE}┌──────────────────────────────────────────────────┐{Colors.NC}")
        print(f"{Colors.BLUE}│{Colors.NC}  ESP Feature: {status}")
        print(f"{Colors.BLUE}└──────────────────────────────────────────────────┘{Colors.NC}\n")
        
        input(f"{Colors.YELLOW}Press Enter to go back...{Colors.NC}")
    
    def toggle_auto_connect(self):
        """Toggle Auto-Connect feature"""
        self.clear_screen()
        self.config['auto_connect'] = not self.config['auto_connect']
        status = f"{Colors.GREEN}ENABLED{Colors.NC}" if self.config['auto_connect'] else f"{Colors.RED}DISABLED{Colors.NC}"
        
        print(f"\n{Colors.BLUE}┌──────────────────────────────────────────────────┐{Colors.NC}")
        print(f"{Colors.BLUE}│{Colors.NC}  Auto-Connect: {status}")
        print(f"{Colors.BLUE}└──────────────────────────────────────────────────┘{Colors.NC}\n")
        
        input(f"{Colors.YELLOW}Press Enter to go back...{Colors.NC}")
    
    def show_settings(self):
        """Display settings"""
        self.clear_screen()
        print(f"\n{Colors.MAGENTA}╔════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.MAGENTA}║{Colors.NC}  {Colors.YELLOW}SETTINGS{Colors.NC}".ljust(57) + f"{Colors.MAGENTA}║{Colors.NC}")
        print(f"{Colors.MAGENTA}╠════════════════════════════════════════════════════╣{Colors.NC}")
        
        for key, value in self.config.items():
            print(f"{Colors.MAGENTA}║{Colors.NC}  {key.replace('_', ' ').title()}: {Colors.CYAN}{value}{Colors.NC}")
        
        print(f"{Colors.MAGENTA}╚════════════════════════════════════════════════════╝{Colors.NC}\n")
        
        input(f"{Colors.YELLOW}Press Enter to go back...{Colors.NC}")
    
    def view_status(self):
        """View current status"""
        self.clear_screen()
        print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.CYAN}║{Colors.NC}  {Colors.YELLOW}SYSTEM STATUS{Colors.NC}".ljust(57) + f"{Colors.CYAN}║{Colors.NC}")
        print(f"{Colors.CYAN}╠════════════════════════════════════════════════════╣{Colors.NC}")
        
        esp_status = f"{Colors.GREEN}ACTIVE{Colors.NC}" if self.config['esp_enabled'] else f"{Colors.RED}INACTIVE{Colors.NC}"
        connect_status = f"{Colors.GREEN}ENABLED{Colors.NC}" if self.config['auto_connect'] else f"{Colors.RED}DISABLED{Colors.NC}"
        bot_status = f"{Colors.GREEN}RUNNING{Colors.NC}" if self.aimbot_running else f"{Colors.RED}STOPPED{Colors.NC}"
        server_status = f"{Colors.GREEN}CONNECTED{Colors.NC}" if self.auto_connect.connected else f"{Colors.RED}OFFLINE{Colors.NC}"
        
        print(f"{Colors.CYAN}║{Colors.NC}  Aim Bot: {bot_status}")
        print(f"{Colors.CYAN}║{Colors.NC}  ESP: {esp_status}")
        print(f"{Colors.CYAN}║{Colors.NC}  Auto-Connect: {connect_status}")
        print(f"{Colors.CYAN}║{Colors.NC}  Server: {server_status}")
        print(f"{Colors.CYAN}║{Colors.NC}  Time: {datetime.now().strftime('%H:%M:%S')}")
        
        print(f"{Colors.CYAN}╚════════════════════════════════════════════════════╝{Colors.NC}\n")
        
        input(f"{Colors.YELLOW}Press Enter to go back...{Colors.NC}")
    
    def shutdown(self):
        """Shutdown application"""
        self.clear_screen()
        print(f"\n{Colors.RED}╔════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.RED}║{Colors.NC}  Shutting down Aim Bot...")
        print(f"{Colors.RED}╚════════════════════════════════════════════════════╝{Colors.NC}\n")
        
        if self.auto_connect.connected:
            self.auto_connect.disconnect()
        
        self.aimbot_running = False
        self.running = False
        self.menu_active = False
        
        print(f"{Colors.GREEN}[✓] Thank you for using Free Fire Aim Bot!{Colors.NC}\n")
        time.sleep(1)
    
    def run(self):
        """Main application run loop"""
        try:
            self.show_header()
            print(f"\n{Colors.GREEN}[✓] System Initialized{Colors.NC}")
            print(f"{Colors.GREEN}[✓] Ready to start{Colors.NC}")
            print(f"{Colors.YELLOW}[*] Loading...{Colors.NC}\n")
            time.sleep(2)
            
            self.show_menu()
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[*] Application interrupted{Colors.NC}")
            self.shutdown()
        except Exception as e:
            print(f"\n{Colors.RED}[!] Error: {e}{Colors.NC}")
            sys.exit(1)

def main():
    """Main entry point"""
    try:
        aimbot = AimBot()
        aimbot.run()
    except Exception as e:
        print(f"{Colors.RED}[!] Fatal Error: {e}{Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
