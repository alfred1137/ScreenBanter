import customtkinter as ctk
import requests
import threading
from .settings import settings_manager
from .region_selector import RegionSelector

class SettingsWindow(ctk.CTk):
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

        self.capture_button = ctk.CTkButton(self.sidebar_frame, text="Capture", command=self.show_capture)
        self.capture_button.grid(row=2, column=0, padx=20, pady=10)

        self.audio_button = ctk.CTkButton(self.sidebar_frame, text="Audio", command=self.show_audio)
        self.audio_button.grid(row=3, column=0, padx=20, pady=10)

        self.hotkeys_button = ctk.CTkButton(self.sidebar_frame, text="Hotkeys", command=self.show_hotkeys)
        self.hotkeys_button.grid(row=4, column=0, padx=20, pady=10)

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

        # Process Priority
        priority_label = ctk.CTkLabel(self.current_frame, text="Process Priority (OS Scheduling):")
        priority_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        
        priority_hint = ctk.CTkLabel(self.current_frame, text="Higher priority reduces stuttering under load.", 
                                     font=ctk.CTkFont(size=10, slant="italic"))
        priority_hint.grid(row=4, column=0, padx=10, pady=(0, 5), sticky="w")

        self.priority_option = ctk.CTkOptionMenu(self.current_frame, 
                                                values=["Normal", "Above_Normal", "High"],
                                                command=lambda _: self.save_general())
        self.priority_option.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        current_priority = settings_manager.get("system", "priority") or "above_normal"
        self.priority_option.set(current_priority.capitalize())

    def save_general(self):
        settings_manager.set("system", "play_startup_sound", self.startup_sound_var.get())
        settings_manager.set("system", "minimize_to_tray", self.minimize_var.get())
        settings_manager.set("system", "priority", self.priority_option.get().lower())

    def show_capture(self):
        self.clear_content()
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        label = ctk.CTkLabel(self.current_frame, text="Capture Settings", font=ctk.CTkFont(size=16, weight="bold"))
        label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")

        # Toggle Region Capture
        self.use_region_var = ctk.BooleanVar(value=settings_manager.get("capture", "use_region"))
        self.region_check = ctk.CTkCheckBox(self.current_frame, text="Use Custom Capture Region", 
                                       variable=self.use_region_var, command=self.toggle_region_use)
        self.region_check.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Region Info & Select Button
        self.region_info = ctk.CTkLabel(self.current_frame, text=self._get_region_text())
        self.region_info.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.select_btn = ctk.CTkButton(self.current_frame, text="Select New Region", command=self.select_new_region)
        self.select_btn.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # Enable/Disable select based on toggle
        self.toggle_region_use()

    def _get_region_text(self):
        region = settings_manager.get("capture", "region")
        if region:
            return f"Current Region: {region}"
        return "Current Region: Fullscreen (None selected)"

    def toggle_region_use(self):
        val = self.use_region_var.get()
        settings_manager.set("capture", "use_region", val)
        
        if val:
            self.select_btn.configure(state="normal")
        else:
            self.select_btn.configure(state="disabled")

    def select_new_region(self):
        # Minimize settings window to allow clear selection
        self.iconify()
        
        # Open selector
        selector = RegionSelector(master=self)
        region = selector.select_region()
        
        # Restore settings window
        self.deiconify()
        self.lift()
        
        if region:
            settings_manager.set("capture", "region", region)
            # Auto-enable usage if a region is picked
            self.use_region_var.set(True)
            settings_manager.set("capture", "use_region", True)
            
            self.region_info.configure(text=self._get_region_text())
            self.select_btn.configure(state="normal")

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

        # Buffering Slider
        self.buffer_val = settings_manager.get("audio", "buffer_seconds") or 4.0
        self.buffer_label = ctk.CTkLabel(self.current_frame, text=f"Playback Buffer: {self.buffer_val:.1f}s")
        self.buffer_label.grid(row=3, column=0, padx=10, pady=(20, 0), sticky="w")
        
        buffer_hint = ctk.CTkLabel(self.current_frame, text="Increases delay but prevents stuttering under high GPU/CPU usage.", 
                                     font=ctk.CTkFont(size=10, slant="italic"), wraplength=350, justify="left")
        buffer_hint.grid(row=4, column=0, padx=10, pady=(0, 5), sticky="w")

        self.buffer_slider = ctk.CTkSlider(self.current_frame, from_=0.5, to=10.0, 
                                          command=self.update_buffer_label)
        self.buffer_slider.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.buffer_slider.set(self.buffer_val)
        
        save_buffer_btn = ctk.CTkButton(self.current_frame, text="Apply Buffer", command=self.save_buffer)
        save_buffer_btn.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        # Fetch voices from server in background
        threading.Thread(target=self.fetch_voices, daemon=True).start()

    def update_buffer_label(self, val):
        self.buffer_label.configure(text=f"Playback Buffer: {float(val):.1f}s")

    def save_buffer(self):
        val = round(float(self.buffer_slider.get()), 1)
        settings_manager.set("audio", "buffer_seconds", val)
        # Inform user
        info = ctk.CTkLabel(self.current_frame, text=f"Buffer updated to {val}s", text_color="green")
        info.grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.after(2000, info.destroy)

    def fetch_voices(self):
        try:
            resp = requests.get("http://localhost:8000/v1/voices", timeout=2)
            if resp.status_code == 200:
                voices = resp.json().get("voices", [])
                if voices:
                    # Schedule UI update on main thread
                    self.after(0, lambda: self._update_voice_options(voices))
        except:
            # Schedule UI update on main thread
            self.after(0, lambda: self._update_voice_options(["Server Offline"], error=True))

    def _update_voice_options(self, values, error=False):
        # Check if the widget still exists before updating
        try:
            if not self.voice_option.winfo_exists():
                return
                
            if error:
                # Keep current value if possible, or show offline
                current = settings_manager.get("audio", "voice_key")
                self.voice_option.configure(values=["Server Offline", current])
            else:
                self.voice_option.configure(values=values)
                current_voice = settings_manager.get("audio", "voice_key")
                if current_voice in values:
                    self.voice_option.set(current_voice)
        except Exception as e:
            print(f"Error updating voice options: {e}")

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
