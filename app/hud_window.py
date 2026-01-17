import customtkinter as ctk
import time
import threading
import ctypes
from typing import Optional
from .settings_window import SettingsWindow
from .settings import settings_manager

try:
    import win32gui
    import win32con
    import win32api
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False
    print("Warning: pywin32 not found. HUD focus features may not work.")

class BanterHUD(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("ScreenBanter HUD")
        self.geometry("600x150")
        self.overrideredirect(True) # Frameless
        self.attributes("-topmost", True)
        
        opacity = settings_manager.get("hud", "opacity")
        if opacity is None: opacity = 0.9
        self.attributes("-alpha", opacity)
        
        # Positioning (Bottom Center)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = screen_height - 250 # 250px from bottom
        self.geometry(f"600x150+{x}+{y}")
        
        # Style
        self.configure(fg_color="#1a1a1a")
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Content expands
        
        # Header / Status
        self.status_label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaaaaa")
        self.status_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Main Content (OCR Text)
        self.text_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16), wraplength=560, justify="left")
        self.text_label.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        
        # Footer / Progress
        self.progress_bar = ctk.CTkProgressBar(self, height=4, width=560)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=(0, 15))
        self.progress_bar.set(0)
        
        # Win32 Tweaks for "No Activate" (Don't steal focus)
        self.apply_window_styles()
        
        self.hide_timer: Optional[threading.Timer] = None
        self.settings_window = None
        
        self.withdraw() # Start hidden

    def apply_window_styles(self):
        """
        Applies Windows-specific styles to ensure the HUD stays on top 
        but does not steal focus from the game.
        """
        if not HAS_PYWIN32:
            return
            
        try:
            hwnd = win32gui.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
                
            # Get current styles
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            # Add WS_EX_NOACTIVATE (0x08000000) and WS_EX_TOPMOST (0x00000008)
            new_style = ex_style | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST
            
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
        except Exception as e:
            print(f"HUD Style Error: {e}")

    def safe_show_message(self, text: str, status: str = "Speaking..."):
        """Thread-safe wrapper for show_message"""
        self.after(0, lambda: self._show_message_impl(text, status))

    def _show_message_impl(self, text: str, status: str):
        self.deiconify()
        self.apply_window_styles() # Re-apply in case it was lost
        
        if settings_manager.get("hud", "steal_focus"):
            self.focus_force()
        
        self.status_label.configure(text=status)
        self.text_label.configure(text=text)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Cancel any pending hide
        if self.hide_timer:
            self.hide_timer.cancel()
            
    def safe_update_status(self, status: str):
        self.after(0, lambda: self.status_label.configure(text=status))

    def safe_dismiss(self, delay=2.0):
        self.after(0, lambda: self._dismiss_impl(delay))

    def _dismiss_impl(self, delay):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self.status_label.configure(text="Finished")
        
        if self.hide_timer:
            self.hide_timer.cancel()
            
        self.hide_timer = threading.Timer(delay, lambda: self.after(0, self.withdraw))
        self.hide_timer.start()

    def open_settings(self):
        """Opens the settings window as a Toplevel."""
        self.after(0, self._open_settings_impl)

    def _open_settings_impl(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.focus()
            self.settings_window.lift()