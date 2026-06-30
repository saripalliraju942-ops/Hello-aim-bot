"""
FREE FIRE AIM BOT - ANDROID FLOATING OVERLAY
Version: 2.0 - Kivy Framework Edition
Floating Menu + Overlay System
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
import json
import os
from datetime import datetime
import threading
import socket

# Set window properties
Window.size = (400, 600)
Window.borderless = True
Window.clearcolor = (0.1, 0.1, 0.1, 0.9)

class Config:
    """Configuration Manager"""
    def __init__(self):
        self.settings = {
            'esp_enabled': True,
            'auto_connect': True,
            'aim_sensitivity': 5,
            'headshot_priority': True,
            'auto_fire': False,
            'server_ip': '127.0.0.1',
            'server_port': 8888,
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        config_path = os.path.expanduser('~/.aimbot_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.settings.update(json.load(f))
            except:
                pass
    
    def save_config(self):
        """Save configuration to file"""
        config_path = os.path.expanduser('~/.aimbot_config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass

class ESPOverlay(Widget):
    """ESP Overlay Drawing System"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.players = []
        self.canvas_drawn = False
    
    def draw_esp(self, players):
        """Draw ESP lines and targets"""
        self.players = players
        self.canvas.clear()
        
        with self.canvas:
            # Draw ESP lines for each player
            Color(1, 0, 0, 0.8)  # Red color
            for player in players:
                # Draw line from body to head
                Line(points=[
                    player['x'], player['y'],
                    player['hx'], player['hy']
                ], width=2)
                
                # Draw circle at head location
                Color(1, 0, 0, 0.5)
                Ellipse(pos=(player['hx']-10, player['hy']-10), size=(20, 20))

class AutoConnectThread(threading.Thread):
    """Auto-connect to server thread"""
    def __init__(self, host, port, callback):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.callback = callback
        self.running = True
    
    def run(self):
        """Run connection thread"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.host, self.port))
            self.callback(True, "Connected!")
        except:
            self.callback(False, "Connection Failed")

class AimBotApp(App):
    """Main Aim Bot Application"""
    
    def build(self):
        self.config_manager = Config()
        self.title = 'Free Fire Aim Bot - Overlay'
        self.aimbot_running = False
        self.esp_enabled = self.config_manager.settings['esp_enabled']
        self.auto_connect_enabled = self.config_manager.settings['auto_connect']
        
        # Main floating layout
        main_layout = FloatLayout()
        
        # Create main menu button (floating)
        self.menu_button = Button(
            text='☰ MENU',
            size_hint=(0.2, 0.08),
            pos_hint={'right': 0.98, 'top': 0.98},
            background_color=(0.2, 0.6, 1, 1),
            font_size='14sp'
        )
        self.menu_button.bind(on_press=self.show_main_menu)
        main_layout.add_widget(self.menu_button)
        
        # Status label
        self.status_label = Label(
            text='Ready',
            size_hint=(0.5, 0.06),
            pos_hint={'center_x': 0.5, 'top': 0.92},
            color=(0, 1, 0, 1),
            font_size='12sp'
        )
        main_layout.add_widget(self.status_label)
        
        # Quick toggle buttons
        quick_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.85},
            spacing=5
        )
        
        self.esp_toggle = ToggleButton(
            text='ESP: ON' if self.esp_enabled else 'ESP: OFF',
            size_hint_x=0.5,
            background_color=(0, 1, 0, 1) if self.esp_enabled else (1, 0, 0, 1)
        )
        self.esp_toggle.bind(on_press=self.toggle_esp)
        quick_layout.add_widget(self.esp_toggle)
        
        self.connect_toggle = ToggleButton(
            text='CONNECT: ON' if self.auto_connect_enabled else 'CONNECT: OFF',
            size_hint_x=0.5,
            background_color=(0, 1, 0, 1) if self.auto_connect_enabled else (1, 0, 0, 1)
        )
        self.connect_toggle.bind(on_press=self.toggle_auto_connect)
        quick_layout.add_widget(self.connect_toggle)
        
        main_layout.add_widget(quick_layout)
        
        # Start button (large)
        start_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.75},
            spacing=5
        )
        
        self.start_button = Button(
            text='▶ START BOT',
            background_color=(0, 1, 0, 1),
            font_size='16sp'
        )
        self.start_button.bind(on_press=self.start_aimbot)
        start_layout.add_widget(self.start_button)
        
        self.stop_button = Button(
            text='⏹ STOP',
            background_color=(1, 0, 0, 1),
            font_size='16sp'
        )
        self.stop_button.bind(on_press=self.stop_aimbot)
        start_layout.add_widget(self.stop_button)
        
        main_layout.add_widget(start_layout)
        
        # Info display
        self.info_label = Label(
            text='[Status]\nBot: STOPPED\nESP: ' + ('ON' if self.esp_enabled else 'OFF') + '\nAuto-Connect: ' + ('ON' if self.auto_connect_enabled else 'OFF'),
            size_hint=(0.95, 0.5),
            pos_hint={'center_x': 0.5, 'top': 0.6},
            color=(0.7, 1, 0.7, 1),
            font_size='12sp',
            markup=True
        )
        main_layout.add_widget(self.info_label)
        
        # Bottom action buttons
        bottom_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            spacing=5
        )
        
        settings_btn = Button(
            text='⚙ SETTINGS',
            background_color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.5
        )
        settings_btn.bind(on_press=self.show_settings)
        bottom_layout.add_widget(settings_btn)
        
        exit_btn = Button(
            text='✕ EXIT',
            background_color=(1, 0.3, 0.3, 1),
            size_hint_x=0.5
        )
        exit_btn.bind(on_press=self.exit_app)
        bottom_layout.add_widget(exit_btn)
        
        main_layout.add_widget(bottom_layout)
        
        # Update timer
        Clock.schedule_interval(self.update_status, 1)
        
        return main_layout
    
    def show_main_menu(self, instance):
        """Show main menu popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        title = Label(
            text='[b]MAIN MENU[/b]',
            size_hint_y=0.15,
            markup=True,
            font_size='16sp',
            color=(0, 1, 0, 1)
        )
        content.add_widget(title)
        
        # Menu buttons
        menu_buttons = BoxLayout(orientation='vertical', spacing=8, size_hint_y=0.7)
        
        buttons_data = [
            ('🎯 Start Aim Bot', self.start_aimbot),
            ('🛑 Stop Aim Bot', self.stop_aimbot),
            ('👁 Toggle ESP', self.toggle_esp),
            ('🔌 Toggle Auto-Connect', self.toggle_auto_connect),
            ('⚙ Settings', self.show_settings),
            ('📊 Status', self.show_status),
        ]
        
        for btn_text, btn_callback in buttons_data:
            btn = Button(
                text=btn_text,
                size_hint_y=None,
                height='40sp',
                background_color=(0.3, 0.3, 0.8, 1)
            )
            btn.bind(on_press=btn_callback)
            menu_buttons.add_widget(btn)
        
        content.add_widget(menu_buttons)
        
        # Close button
        close_btn = Button(
            text='Close',
            size_hint_y=0.15,
            background_color=(1, 0.5, 0, 1)
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='FREE FIRE AIM BOT',
            content=content,
            size_hint=(0.9, 0.7)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def start_aimbot(self, instance=None):
        """Start the aim bot"""
        self.aimbot_running = True
        self.status_label.text = '[color=00ff00]BOT RUNNING[/color]'
        self.status_label.markup = True
        self.start_button.disabled = True
        self.stop_button.disabled = False
        
        # Auto-connect if enabled
        if self.auto_connect_enabled:
            thread = AutoConnectThread(
                self.config_manager.settings['server_ip'],
                self.config_manager.settings['server_port'],
                self.on_connect_result
            )
            thread.start()
        
        self.update_info()
    
    def stop_aimbot(self, instance=None):
        """Stop the aim bot"""
        self.aimbot_running = False
        self.status_label.text = '[color=ff0000]BOT STOPPED[/color]'
        self.status_label.markup = True
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        self.update_info()
    
    def toggle_esp(self, instance=None):
        """Toggle ESP feature"""
        self.esp_enabled = not self.esp_enabled
        self.config_manager.settings['esp_enabled'] = self.esp_enabled
        self.config_manager.save_config()
        
        self.esp_toggle.text = 'ESP: ON' if self.esp_enabled else 'ESP: OFF'
        self.esp_toggle.background_color = (0, 1, 0, 1) if self.esp_enabled else (1, 0, 0, 1)
        
        self.update_info()
    
    def toggle_auto_connect(self, instance=None):
        """Toggle auto-connect feature"""
        self.auto_connect_enabled = not self.auto_connect_enabled
        self.config_manager.settings['auto_connect'] = self.auto_connect_enabled
        self.config_manager.save_config()
        
        self.connect_toggle.text = 'CONNECT: ON' if self.auto_connect_enabled else 'CONNECT: OFF'
        self.connect_toggle.background_color = (0, 1, 0, 1) if self.auto_connect_enabled else (1, 0, 0, 1)
        
        self.update_info()
    
    def on_connect_result(self, success, message):
        """Handle connection result"""
        if success:
            self.status_label.text = '[color=00ff00]CONNECTED[/color]'
        else:
            self.status_label.text = '[color=ffff00]CONNECTION FAILED[/color]'
        self.status_label.markup = True
    
    def show_settings(self, instance=None):
        """Show settings popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        title = Label(
            text='[b]SETTINGS[/b]',
            size_hint_y=0.1,
            markup=True,
            color=(0, 1, 0, 1)
        )
        content.add_widget(title)
        
        # Settings list
        scroll = ScrollView(size_hint=(1, 0.8))
        settings_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        for key, value in self.config_manager.settings.items():
            setting_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='40sp', spacing=10)
            
            label = Label(text=key.replace('_', ' ').title(), size_hint_x=0.5, color=(1, 1, 1, 1))
            value_label = Label(text=str(value), size_hint_x=0.5, color=(0, 1, 1, 1))
            
            setting_box.add_widget(label)
            setting_box.add_widget(value_label)
            settings_layout.add_widget(setting_box)
        
        scroll.add_widget(settings_layout)
        content.add_widget(scroll)
        
        close_btn = Button(text='Close', size_hint_y=0.1, background_color=(1, 0.5, 0, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title='Settings', content=content, size_hint=(0.9, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_status(self, instance=None):
        """Show status popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        status_text = f"""[b]SYSTEM STATUS[/b]

Bot Status: {'[color=00ff00]RUNNING[/color]' if self.aimbot_running else '[color=ff0000]STOPPED[/color]'}
ESP: {'[color=00ff00]ENABLED[/color]' if self.esp_enabled else '[color=ff0000]DISABLED[/color]'}
Auto-Connect: {'[color=00ff00]ENABLED[/color]' if self.auto_connect_enabled else '[color=ff0000]DISABLED[/color]'}
Time: {datetime.now().strftime('%H:%M:%S')}
Aim Sensitivity: {self.config_manager.settings['aim_sensitivity']}
Headshot Priority: {'ON' if self.config_manager.settings['headshot_priority'] else 'OFF'}
"""
        
        status_label = Label(
            text=status_text,
            markup=True,
            size_hint_y=0.8,
            color=(0.7, 1, 0.7, 1)
        )
        content.add_widget(status_label)
        
        close_btn = Button(text='Close', size_hint_y=0.2, background_color=(1, 0.5, 0, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title='Status', content=content, size_hint=(0.85, 0.7))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def update_info(self):
        """Update info display"""
        info_text = f"""[b][color=00ff00]FREE FIRE AIM BOT[/color][/b]

[color=ffff00]Bot Status:[/color] {'[color=00ff00]RUNNING[/color]' if self.aimbot_running else '[color=ff0000]STOPPED[/color]'}
[color=ffff00]ESP:[/color] {'[color=00ff00]ENABLED[/color]' if self.esp_enabled else '[color=ff0000]DISABLED[/color]'}
[color=ffff00]Auto-Connect:[/color] {'[color=00ff00]ENABLED[/color]' if self.auto_connect_enabled else '[color=ff0000]DISABLED[/color]'}
[color=ffff00]Sensitivity:[/color] {self.config_manager.settings['aim_sensitivity']}
[color=ffff00]Headshot Mode:[/color] {'ON' if self.config_manager.settings['headshot_priority'] else 'OFF'}

[color=00ffff]Time: {datetime.now().strftime('%H:%M:%S')}[/color]
"""
        self.info_label.text = info_text
    
    def update_status(self, dt):
        """Update status periodically"""
        self.update_info()
    
    def exit_app(self, instance=None):
        """Exit application"""
        self.stop_aimbot()
        App.get_running_app().stop()

class FreeFireAimBotApp(App):
    """Main Application"""
    
    def build(self):
        self.title = 'Free Fire Aim Bot'
        return AimBotApp().build()

if __name__ == '__main__':
    app = AimBotApp()
    app.run()
