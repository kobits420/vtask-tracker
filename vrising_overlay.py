import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from pynput import keyboard
import threading
import time

class VTaskTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.current_step = 0
        self.steps = []
        self.pressed_keys = set()
        self.last_action_time = 0
        self.current_template = "sample_guide.json"
        self.setup_ui()
        self.setup_keyboard_listener()
        self.load_guide()
        
    def setup_window(self):
        """Configure the overlay window properties"""
        self.root.title("VTask Tracker")
        self.root.geometry("400x250")
        self.root.configure(bg='black')
        
        # Make window always on top and transparent
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Position window in top-right corner
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"400x250+{screen_width-420}+20")
        
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='black', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="VTask Tracker", 
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='black'
        )
        title_label.pack(pady=(0, 10))
        
        # Step counter
        self.step_counter = tk.Label(
            main_frame,
            text="Step 0 of 0",
            font=('Arial', 10),
            fg='yellow',
            bg='black'
        )
        self.step_counter.pack()
        
        # Current step display
        self.step_display = tk.Label(
            main_frame,
            text="No steps loaded",
            font=('Arial', 11),
            fg='white',
            bg='black',
            wraplength=380,
            justify=tk.LEFT
        )
        self.step_display.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Template management buttons
        button_frame = tk.Frame(main_frame, bg='black')
        button_frame.pack(side=tk.BOTTOM, pady=5)
        
        new_template_btn = tk.Button(
            button_frame,
            text="New Template",
            command=self.create_new_template,
            font=('Arial', 8),
            bg='darkgreen',
            fg='white',
            width=10
        )
        new_template_btn.pack(side=tk.LEFT, padx=2)
        
        load_template_btn = tk.Button(
            button_frame,
            text="Load Template",
            command=self.load_template,
            font=('Arial', 8),
            bg='darkblue',
            fg='white',
            width=10
        )
        load_template_btn.pack(side=tk.LEFT, padx=2)
        
        save_template_btn = tk.Button(
            button_frame,
            text="Save Template",
            command=self.save_template,
            font=('Arial', 8),
            bg='darkorange',
            fg='white',
            width=10
        )
        save_template_btn.pack(side=tk.LEFT, padx=2)
        
        # Controls info
        controls_label = tk.Label(
            main_frame,
            text="Shift+D: Next | Shift+S: Previous | Shift+Q: Quit",
            font=('Arial', 8),
            fg='gray',
            bg='black'
        )
        controls_label.pack(side=tk.BOTTOM)
        
    def setup_keyboard_listener(self):
        """Set up global keyboard listener for navigation"""
        def on_key_press(key):
            try:
                current_time = time.time()
                
                # Prevent rapid-fire actions (debounce)
                if current_time - self.last_action_time < 0.2:
                    return
                
                # Track shift key
                if key == keyboard.Key.shift:
                    self.pressed_keys.add('shift')
                    return
                
                # Check for letter keys with shift
                if hasattr(key, 'char') and key.char:
                    char = key.char.lower()
                    
                    # Check for Shift+D combination (next step)
                    if char == 'd' and 'shift' in self.pressed_keys:
                        self.next_step()
                        self.last_action_time = current_time
                        return
                        
                    # Check for Shift+S combination (previous step)
                    elif char == 's' and 'shift' in self.pressed_keys:
                        self.previous_step()
                        self.last_action_time = current_time
                        return
                        
                    # Check for Shift+Q combination (quit)
                    elif char == 'q' and 'shift' in self.pressed_keys:
                        self.quit_application()
                        self.last_action_time = current_time
                        return
                    
            except (AttributeError, TypeError):
                pass
                
        def on_key_release(key):
            try:
                # Remove shift from pressed keys when released
                if key == keyboard.Key.shift:
                    self.pressed_keys.discard('shift')
            except (AttributeError, TypeError):
                pass
        
        # Start keyboard listener in a separate thread
        self.listener = keyboard.Listener(
            on_press=on_key_press,
            on_release=on_key_release
        )
        self.listener.start()
        
    def create_new_template(self):
        """Create a new custom template"""
        # Create a new window for template creation
        template_window = tk.Toplevel(self.root)
        template_window.title("Create New Template")
        template_window.geometry("500x400")
        template_window.configure(bg='black')
        template_window.attributes('-topmost', True)
        
        # Center the window
        template_window.transient(self.root)
        template_window.grab_set()
        
        # Template name input
        name_frame = tk.Frame(template_window, bg='black')
        name_frame.pack(pady=10)
        
        tk.Label(name_frame, text="Template Name:", font=('Arial', 10), fg='white', bg='black').pack()
        name_entry = tk.Entry(name_frame, font=('Arial', 10), width=30)
        name_entry.pack(pady=5)
        
        # Steps input
        steps_frame = tk.Frame(template_window, bg='black')
        steps_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(steps_frame, text="Steps (one per line):", font=('Arial', 10), fg='white', bg='black').pack()
        
        # Text widget with scrollbar for steps
        text_frame = tk.Frame(steps_frame, bg='black')
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        steps_text = tk.Text(text_frame, font=('Arial', 9), height=15, width=50, bg='darkgray', fg='black')
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=steps_text.yview)
        steps_text.configure(yscrollcommand=scrollbar.set)
        
        steps_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = tk.Frame(template_window, bg='black')
        button_frame.pack(pady=10)
        
        def save_new_template():
            template_name = name_entry.get().strip()
            steps_content = steps_text.get("1.0", tk.END).strip()
            
            if not template_name:
                messagebox.showerror("Error", "Please enter a template name")
                return
                
            if not steps_content:
                messagebox.showerror("Error", "Please enter at least one step")
                return
            
            # Parse steps
            steps = [step.strip() for step in steps_content.split('\n') if step.strip()]
            
            # Create template data
            template_data = {
                "title": template_name,
                "steps": steps
            }
            
            # Save template
            filename = f"{template_name.replace(' ', '_').lower()}_template.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Template '{template_name}' saved as {filename}")
                template_window.destroy()
                
                # Load the new template
                self.current_template = filename
                self.load_guide()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save template: {str(e)}")
        
        def cancel_template():
            template_window.destroy()
        
        tk.Button(button_frame, text="Save Template", command=save_new_template, 
                 bg='darkgreen', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel_template, 
                 bg='darkred', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

    def load_template(self):
        """Load a template from file"""
        filename = filedialog.askopenfilename(
            title="Load Template",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.steps = data.get('steps', [])
                    self.current_template = filename
                    self.current_step = 0
                    self.update_display()
                    messagebox.showinfo("Success", f"Template loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load template: {str(e)}")

    def save_template(self):
        """Save current template to file"""
        if not self.steps:
            messagebox.showerror("Error", "No steps to save")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Template",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                template_data = {
                    "title": os.path.splitext(os.path.basename(filename))[0],
                    "steps": self.steps
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Template saved: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save template: {str(e)}")

    def load_guide(self):
        """Load speedrun guide from JSON file"""
        guide_file = self.current_template
        if os.path.exists(guide_file):
            try:
                with open(guide_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.steps = data.get('steps', [])
                    self.update_display()
            except Exception as e:
                self.step_display.config(text=f"Error loading guide: {str(e)}")
        else:
            # Create sample guide if none exists
            self.create_sample_guide()
            
    def create_sample_guide(self):
        """Create a sample speedrun guide"""
        sample_steps = [
            "Start the game and create your character",
            "Collect basic materials (stone, wood, fiber)",
            "Build your first Castle Heart",
            "Craft basic weapons and armor",
            "Find and defeat the first boss",
            "Upgrade your Castle Heart to level 2",
            "Explore the world for better resources",
            "Defeat the second boss",
            "Continue following the main quest line"
        ]
        
        guide_data = {
            "title": "VTask Tracker Guide",
            "steps": sample_steps
        }
        
        with open("speedrun_guide.json", 'w', encoding='utf-8') as f:
            json.dump(guide_data, f, indent=2)
            
        self.steps = sample_steps
        self.update_display()
        
    def next_step(self):
        """Move to the next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_display()
            
    def previous_step(self):
        """Move to the previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_display()
            
    def update_display(self):
        """Update the step display"""
        if self.steps:
            self.step_counter.config(text=f"Step {self.current_step + 1} of {len(self.steps)}")
            self.step_display.config(text=self.steps[self.current_step])
        else:
            self.step_counter.config(text="No steps available")
            self.step_display.config(text="No steps loaded")
            
    def quit_application(self):
        """Quit the application"""
        self.cleanup()
        self.root.quit()
        self.root.destroy()
            
    def run(self):
        """Start the overlay application"""
        self.root.mainloop()
        
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'listener'):
            self.listener.stop()

if __name__ == "__main__":
    tracker = VTaskTracker()
    try:
        tracker.run()
    except KeyboardInterrupt:
        tracker.cleanup()
