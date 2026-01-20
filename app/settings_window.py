import customtkinter as ctk
import requests
import threading
from .settings import settings_manager
from .region_selector import RegionSelector

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)

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

        self.performance_button = ctk.CTkButton(self.sidebar_frame, text="Performance", command=self.show_performance)
        self.performance_button.grid(row=5, column=0, padx=20, pady=10)

        self.hud_button = ctk.CTkButton(self.sidebar_frame, text="HUD / UI", command=self.show_hud_settings)
        self.hud_button.grid(row=6, column=0, padx=20, pady=10)

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

        # TTS Provider Toggle
        ctk.CTkLabel(self.current_frame, text="TTS Provider:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")
        self.provider_var = ctk.StringVar(value=settings_manager.get("audio", "tts_provider") or "local")
        self.provider_option = ctk.CTkOptionMenu(self.current_frame, values=["local", "gemini"], 
                                                variable=self.provider_var, command=self.on_provider_change)
        self.provider_option.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Provider-specific Container
        self.provider_container = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        self.provider_container.grid(row=3, column=0, sticky="nsew", pady=10)
        
        self.show_provider_settings()

        # Common Audio Settings
        # Buffering Slider
        self.buffer_val = settings_manager.get("audio", "buffer_seconds") or 4.0
        self.buffer_label = ctk.CTkLabel(self.current_frame, text=f"Playback Buffer: {self.buffer_val:.1f}s")
        self.buffer_label.grid(row=4, column=0, padx=10, pady=(20, 0), sticky="w")
        
        buffer_hint = ctk.CTkLabel(self.current_frame, text="Increases delay but prevents stuttering under high GPU/CPU usage.", 
                                     font=ctk.CTkFont(size=10, slant="italic"), wraplength=350, justify="left")
        buffer_hint.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="w")

        self.buffer_slider = ctk.CTkSlider(self.current_frame, from_=0.5, to=10.0, 
                                          command=self.update_buffer_label)
        self.buffer_slider.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        self.buffer_slider.set(self.buffer_val)
        
        save_buffer_btn = ctk.CTkButton(self.current_frame, text="Apply Buffer", command=self.save_buffer)
        save_buffer_btn.grid(row=7, column=0, padx=10, pady=10, sticky="w")

        # Playback Mode
        ctk.CTkLabel(self.current_frame, text="Playback Mode:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=8, column=0, padx=10, pady=(20, 5), sticky="w")

        playback_hint = ctk.CTkLabel(self.current_frame, text="'Pre-generate' waits for full audio. Fixes stutter on slow GPUs but increases latency.",
                                     font=ctk.CTkFont(size=10, slant="italic"), wraplength=350, justify="left")
        playback_hint.grid(row=9, column=0, padx=10, pady=(0, 5), sticky="w")

        self.playback_mode_var = ctk.StringVar(value=settings_manager.get("audio", "playback_mode"))
        self.playback_mode_option = ctk.CTkOptionMenu(self.current_frame,
                                                      values=["stream", "pre-generate"],
                                                      variable=self.playback_mode_var,
                                                      command=self.save_audio_playback_mode)
        self.playback_mode_option.grid(row=10, column=0, padx=10, pady=5, sticky="w")

    def on_provider_change(self, selected_provider):
        settings_manager.set("audio", "tts_provider", selected_provider)
        self.show_provider_settings()

    def show_provider_settings(self):
        # Clear container
        for widget in self.provider_container.winfo_children():
            widget.destroy()

        provider = self.provider_var.get()
        if provider == "local":
            voice_label = ctk.CTkLabel(self.provider_container, text="Local Voice Preset:")
            voice_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            self.voice_option = ctk.CTkOptionMenu(self.provider_container, values=["Loading..."], command=self.save_audio_local)
            self.voice_option.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            self.voice_option.set(settings_manager.get("audio", "voice_key"))

            # Fetch voices from server in background
            threading.Thread(target=self.fetch_voices, daemon=True).start()
        
        elif provider == "gemini":
            ctk.CTkLabel(self.provider_container, text="Gemini Cloud Model:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            self.cloud_model_entry = ctk.CTkEntry(self.provider_container, width=200)
            self.cloud_model_entry.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            self.cloud_model_entry.insert(0, settings_manager.get("audio", "cloud_model") or "gemini-2.5-flash-preview-tts")
            
            ctk.CTkLabel(self.provider_container, text="Gemini Voice Name:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.cloud_voice_option = ctk.CTkOptionMenu(self.provider_container, 
                                                        values=["Puck", "Charon", "Kore", "Fenrir", "Aoede"],
                                                        command=self.save_audio_cloud)
            self.cloud_voice_option.grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.cloud_voice_option.set(settings_manager.get("audio", "cloud_voice") or "Puck")

            self.cloud_model_entry.bind("<FocusOut>", lambda e: self.save_audio_cloud())
            self.cloud_model_entry.bind("<Return>", lambda e: self.save_audio_cloud())

    def save_audio_local(self, selected_voice):
        settings_manager.set("audio", "voice_key", selected_voice)

    def save_audio_cloud(self, _=None):
        settings_manager.set("audio", "cloud_model", self.cloud_model_entry.get().strip())
        settings_manager.set("audio", "cloud_voice", self.cloud_voice_option.get())

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

    def save_audio_playback_mode(self, selected_mode):
        settings_manager.set("audio", "playback_mode", selected_mode)

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

    def show_performance(self):
        self.clear_content()
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        label = ctk.CTkLabel(self.current_frame, text="Performance Mode", font=ctk.CTkFont(size=16, weight="bold"))
        label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")

        # Master Toggle
        self.perf_enabled_var = ctk.BooleanVar(value=settings_manager.get("performance_mode", "enabled"))
        self.perf_switch = ctk.CTkSwitch(self.current_frame, text="Enable Performance Mode", 
                                        variable=self.perf_enabled_var, command=self.save_performance)
        self.perf_switch.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        desc = ctk.CTkLabel(self.current_frame, text="Optimizes VRAM and Process Priority for gaming.\nRecommended for RTX 3060/4060 and below.", 
                           justify="left", text_color="gray")
        desc.grid(row=2, column=0, padx=35, pady=(0, 20), sticky="w")

        # Quantization (Visual Only for now, controlled by Master Toggle effectively)
        ctk.CTkLabel(self.current_frame, text="Quantization Strategy:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.quant_option = ctk.CTkOptionMenu(self.current_frame, values=["4bit (Low VRAM)", "8bit", "None (FP16)"],
                                             command=lambda _: self.save_performance())
        self.quant_option.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        # Map stored value to display value
        current_quant = settings_manager.get("performance_mode", "quantization")
        display_map = {"4bit": "4bit (Low VRAM)", "8bit": "8bit", "none": "None (FP16)"}
        self.quant_option.set(display_map.get(current_quant, "4bit (Low VRAM)"))

        # Priority
        ctk.CTkLabel(self.current_frame, text="Force Process Priority:").grid(row=5, column=0, padx=10, pady=(15, 5), sticky="w")
        self.perf_priority_option = ctk.CTkOptionMenu(self.current_frame, values=["Normal", "Above_Normal", "High"],
                                                     command=lambda _: self.save_performance())
        self.perf_priority_option.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.perf_priority_option.set((settings_manager.get("performance_mode", "process_priority") or "high").capitalize())

        # Restart Warning
        warning_label = ctk.CTkLabel(self.current_frame, text="⚠️ Changes require app restart to take full effect.", 
                                    text_color="#FF5555", font=ctk.CTkFont(size=12, weight="bold"))
        warning_label.grid(row=7, column=0, padx=10, pady=30, sticky="w")

    def save_performance(self):
        settings_manager.set("performance_mode", "enabled", self.perf_enabled_var.get())
        
        # Map display value back to storage key
        display_val = self.quant_option.get()
        reverse_map = {"4bit (Low VRAM)": "4bit", "8bit": "8bit", "None (FP16)": "none"}
        settings_manager.set("performance_mode", "quantization", reverse_map.get(display_val, "4bit"))
        
        settings_manager.set("performance_mode", "process_priority", self.perf_priority_option.get().lower())

    def show_hud_settings(self):
        self.clear_content()
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        label = ctk.CTkLabel(self.current_frame, text="HUD / UI Settings", font=ctk.CTkFont(size=16, weight="bold"))
        label.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")

        # Enable HUD
        self.hud_enabled_var = ctk.BooleanVar(value=settings_manager.get("hud", "enabled"))
        hud_check = ctk.CTkSwitch(self.current_frame, text="Enable Banter HUD", 
                                  variable=self.hud_enabled_var, command=self.save_hud_settings)
        hud_check.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Opacity Slider
        self.opacity_val = settings_manager.get("hud", "opacity")
        if self.opacity_val is None: self.opacity_val = 0.9
        
        self.opacity_label = ctk.CTkLabel(self.current_frame, text=f"Opacity: {int(self.opacity_val * 100)}%")
        self.opacity_label.grid(row=2, column=0, padx=10, pady=(15, 5), sticky="w")
        
        self.opacity_slider = ctk.CTkSlider(self.current_frame, from_=0.1, to=1.0, 
                                            command=self.update_opacity_label)
        self.opacity_slider.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.opacity_slider.set(self.opacity_val)
        
        save_opacity_btn = ctk.CTkButton(self.current_frame, text="Apply Opacity", command=self.save_hud_settings)
        save_opacity_btn.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Steal Focus
        ctk.CTkLabel(self.current_frame, text="Focus Behavior:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, padx=10, pady=(20, 5), sticky="w")
        
        self.steal_focus_var = ctk.BooleanVar(value=settings_manager.get("hud", "steal_focus"))
        steal_check = ctk.CTkCheckBox(self.current_frame, text="Steal Focus (Force Topmost)", 
                                      variable=self.steal_focus_var, command=self.save_hud_settings)
        steal_check.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        
        hint = ctk.CTkLabel(self.current_frame, text="Warning: 'Steal Focus' may minimize exclusive fullscreen games.\nUse only if HUD is not appearing.", 
                            text_color="gray", font=ctk.CTkFont(size=10))
        hint.grid(row=7, column=0, padx=35, pady=(0, 10), sticky="w")

    def update_opacity_label(self, val):
        self.opacity_label.configure(text=f"Opacity: {int(val * 100)}%")

    def save_hud_settings(self):
        settings_manager.set("hud", "enabled", self.hud_enabled_var.get())
        settings_manager.set("hud", "opacity", self.opacity_slider.get())
        settings_manager.set("hud", "steal_focus", self.steal_focus_var.get())
        
        # If running, try to apply opacity immediately if possible (requires reference to HUD which we have via master)
        if self.master and hasattr(self.master, "attributes"):
            try:
                self.master.attributes("-alpha", self.opacity_slider.get())
            except:
                pass

if __name__ == "__main__":
    app = SettingsWindow()
    app.mainloop()
