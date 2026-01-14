import customtkinter as ctk
import requests
import threading
from .settings import settings_manager

class SettingsWindow(ctk.CTK):
    def __init__(self):
        super().__init__()

        self.title("ScreenBanter Settings")
        self.geometry("600x500")
        
        # Appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar for navigation
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ScreenBanter", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.general_button = ctk.CTkButton(self.sidebar_frame, text="General", command=self.show_general)
        self.general_button.grid(row=1, column=0, padx=20, pady=10)

        self.audio_button = ctk.CTkButton(self.sidebar_frame, text="Audio", command=self.show_audio)
        self.audio_button.grid(row=2, column=0, padx=20, pady=10)

        self.hotkeys_button = ctk.CTkButton(self.sidebar_frame, text="Hotkeys", command=self.show_hotkeys)
        self.hotkeys_button.grid(row=3, column=0, padx=20, pady=10)

        # Content areas
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.current_frame = None
        self.show_general()

    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_general(self):
        self.clear_content()
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        label = ctk.CTkLabel(self.current_frame, text="General Settings", font=ctk.CTkFont(size=16, weight="bold"))
        label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")

        # Startup Sound
        self.startup_sound_var = ctk.BooleanVar(value=settings_manager.get("system", "play_startup_sound"))
        startup_check = ctk.CTkCheckBox(self.current_frame, text="Play startup sound", 
                                        variable=self.startup_sound_var, command=self.save_general)
        startup_check.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Minimize to Tray
        self.minimize_var = ctk.BooleanVar(value=settings_manager.get("system", "minimize_to_tray"))
        minimize_check = ctk.CTkCheckBox(self.current_frame, text="Minimize to system tray on close", 
                                         variable=self.minimize_var, command=self.save_general)
        minimize_check.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    def save_general(self):
        settings_manager.set("system", "play_startup_sound", self.startup_sound_var.get())
        settings_manager.set("system", "minimize_to_tray", self.minimize_var.get())

    def show_audio(self):
        self.clear_content()
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        label = ctk.CTkLabel(self.current_frame, text="Audio Settings", font=ctk.CTkFont(size=16, weight="bold"))
        label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")

        # Voice Selection
        voice_label = ctk.CTkLabel(self.current_frame, text="Voice Preset:")
        voice_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.voice_option = ctk.CTkOptionMenu(self.current_frame, values=["Loading..."], command=self.save_audio)
        self.voice_option.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.voice_option.set(settings_manager.get("audio", "voice_key"))

        # Fetch voices from server in background
        threading.Thread(target=self.fetch_voices, daemon=True).start()

    def fetch_voices(self):
        try:
            resp = requests.get("http://localhost:8000/v1/voices", timeout=2)
            if resp.status_code == 200:
                voices = resp.json().get("voices", [])
                if voices:
                    self.voice_option.configure(values=voices)
                    current_voice = settings_manager.get("audio", "voice_key")
                    if current_voice in voices:
                        self.voice_option.set(current_voice)
        except:
            self.voice_option.configure(values=["Server Offline", settings_manager.get("audio", "voice_key")])

    def save_audio(self, selected_voice):
        settings_manager.set("audio", "voice_key", selected_voice)

    def show_hotkeys(self):
        self.clear_content()
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        label = ctk.CTkLabel(self.current_frame, text="Hotkey Settings", font=ctk.CTkFont(size=16, weight="bold"))
        label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")
        
        hint = ctk.CTkLabel(self.current_frame, text="Format: control+alt+s, f10, etc.", font=ctk.CTkFont(size=10, slant="italic"))
        hint.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        # Trigger
        ctk.CTkLabel(self.current_frame, text="Instant Trigger:").grid(row=2, column=0, padx=10, pady=2, sticky="w")
        self.trigger_entry = ctk.CTkEntry(self.current_frame, width=200)
        self.trigger_entry.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")
        self.trigger_entry.insert(0, settings_manager.get_hotkey("trigger"))

        # Queue
        ctk.CTkLabel(self.current_frame, text="Queue Screenshot:").grid(row=4, column=0, padx=10, pady=2, sticky="w")
        self.queue_entry = ctk.CTkEntry(self.current_frame, width=200)
        self.queue_entry.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")
        self.queue_entry.insert(0, settings_manager.get_hotkey("queue"))

        # Process
        ctk.CTkLabel(self.current_frame, text="Process Queue:").grid(row=6, column=0, padx=10, pady=2, sticky="w")
        self.process_entry = ctk.CTkEntry(self.current_frame, width=200)
        self.process_entry.grid(row=7, column=0, padx=10, pady=(0, 10), sticky="w")
        self.process_entry.insert(0, settings_manager.get_hotkey("process"))

        save_btn = ctk.CTkButton(self.current_frame, text="Save Hotkeys", command=self.save_hotkeys)
        save_btn.grid(row=8, column=0, padx=10, pady=20, sticky="w")

    def save_hotkeys(self):
        settings_manager.set("hotkeys", "trigger", self.trigger_entry.get().strip())
        settings_manager.set("hotkeys", "queue", self.queue_entry.get().strip())
        settings_manager.set("hotkeys", "process", self.process_entry.get().strip())
        
        info_label = ctk.CTkLabel(self.current_frame, text="Hotkeys saved! (Restart app to apply)", text_color="green")
        info_label.grid(row=9, column=0, padx=10, pady=0, sticky="w")
        self.after(3000, info_label.destroy)

if __name__ == "__main__":
    app = SettingsWindow()
    app.mainloop()
