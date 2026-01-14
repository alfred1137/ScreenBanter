import tkinter as tk
from typing import Optional, Tuple

class RegionSelector:
    def __init__(self, master=None):
        self.master = master
        self.root = None
        self.start_x = None
        self.start_y = None
        self.cur_rect = None
        self.selection = None  # (left, top, right, bottom)
        self.is_selecting = False

    def select_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Opens a transparent fullscreen overlay to let the user select a region.
        Returns (left, top, right, bottom) or None if cancelled.
        """
        if self.master:
            self.root = tk.Toplevel(self.master)
        else:
            self.root = tk.Tk()
            
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Semi-transparent white
        self.root.configure(background='black')
        self.root.attributes('-topmost', True)
        
        # Cursor
        self.root.config(cursor="cross")

        # Events
        self.root.bind("<ButtonPress-1>", self.on_press)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", self.cancel)

        # Canvas for drawing rectangle
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey10", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Wait for visibility before setting transparency on some systems
        self.root.wait_visibility(self.root)
        self.root.attributes('-alpha', 0.4) 

        if self.master:
            self.root.grab_set() # Modal
            self.root.wait_window()
        else:
            self.root.mainloop()
        
        return self.selection

    def on_press(self, event):
        self.start_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        self.start_y = self.root.winfo_pointery() - self.root.winfo_rooty()
        self.is_selecting = True

    def on_drag(self, event):
        if not self.is_selecting:
            return
            
        cur_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        cur_y = self.root.winfo_pointery() - self.root.winfo_rooty()

        if self.cur_rect:
            self.canvas.delete(self.cur_rect)
        
        # Draw red rectangle
        self.cur_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline='red', width=2
        )

    def on_release(self, event):
        if not self.is_selecting:
            return
            
        end_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        end_y = self.root.winfo_pointery() - self.root.winfo_rooty()

        # Calculate coordinates ensuring left < right, top < bottom
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)

        # Basic validation to avoid tiny accidental clicks
        if (right - left) > 10 and (bottom - top) > 10:
            self.selection = (left, top, right, bottom)
            
        self.close()

    def cancel(self, event):
        self.selection = None
        self.close()

    def close(self):
        if self.root:
            self.root.destroy()
            self.root = None

if __name__ == "__main__":
    # Test
    selector = RegionSelector()
    print(f"Selected: {selector.select_region()}")
