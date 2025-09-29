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
        
        # Keybind configuration
        self.keybind_config_file = "keybind_config.json"
        self.default_keybinds = {
            "next_step": {"modifiers": ["shift"], "key": "d"},
            "previous_step": {"modifiers": ["shift"], "key": "s"},
            "quit_app": {"modifiers": ["shift"], "key": "q"},
            "minimize_toggle": {"modifiers": ["shift"], "key": "r"}
        }
        self.keybinds = self.load_keybind_config()
        
        # Window state tracking
        self.is_minimized = False
        
        # Drag functionality variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_window_x = 0
        self.drag_window_y = 0
        self.is_dragging = False
        
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
        
        # Settings button
        settings_btn = tk.Button(
            button_frame,
            text="Settings",
            command=self.open_settings,
            font=('Arial', 8),
            bg='purple',
            fg='white',
            width=10
        )
        settings_btn.pack(side=tk.LEFT, padx=2)
        
        # Controls info
        self.controls_label = tk.Label(
            main_frame,
            text=self.get_controls_text(),
            font=('Arial', 8),
            fg='gray',
            bg='black'
        )
        self.controls_label.pack(side=tk.BOTTOM)
        
        # Bind mouse events for window dragging
        main_frame.bind("<Button-1>", self.start_drag)
        main_frame.bind("<B1-Motion>", self.drag_window)
        main_frame.bind("<ButtonRelease-1>", self.stop_drag)
        
        # Also bind to the title label for easier dragging
        title_label.bind("<Button-1>", self.start_drag)
        title_label.bind("<B1-Motion>", self.drag_window)
        title_label.bind("<ButtonRelease-1>", self.stop_drag)
        
    def setup_keyboard_listener(self):
        """Set up global keyboard listener for navigation"""
        def on_key_press(key):
            try:
                current_time = time.time()
                
                # Prevent rapid-fire actions (debounce)
                if current_time - self.last_action_time < 0.2:
                    return
                
                # Track modifier keys
                if key == keyboard.Key.shift:
                    self.pressed_keys.add('shift')
                    return
                elif key == keyboard.Key.ctrl:
                    self.pressed_keys.add('ctrl')
                    return
                elif key == keyboard.Key.alt:
                    self.pressed_keys.add('alt')
                    return
                
                # Check for configured keybinds
                if hasattr(key, 'char') and key.char:
                    char = key.char.lower()
                    self.check_keybind(char)
                elif hasattr(key, 'name'):
                    # Handle special keys like F1-F12, etc.
                    self.check_keybind(key.name.lower())
                    
            except (AttributeError, TypeError):
                pass
                
        def on_key_release(key):
            try:
                # Remove modifier keys from pressed keys when released
                if key == keyboard.Key.shift:
                    self.pressed_keys.discard('shift')
                elif key == keyboard.Key.ctrl:
                    self.pressed_keys.discard('ctrl')
                elif key == keyboard.Key.alt:
                    self.pressed_keys.discard('alt')
            except (AttributeError, TypeError):
                pass
        
        # Start keyboard listener in a separate thread
        self.listener = keyboard.Listener(
            on_press=on_key_press,
            on_release=on_key_release
        )
        self.listener.start()
    
    def restart_keyboard_listener(self):
        """Restart the keyboard listener with updated keybinds"""
        if hasattr(self, 'listener'):
            self.listener.stop()
        self.setup_keyboard_listener()
    
    def load_keybind_config(self):
        """Load keybind configuration from file or use defaults"""
        if os.path.exists(self.keybind_config_file):
            try:
                with open(self.keybind_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys are present
                    keybinds = self.default_keybinds.copy()
                    keybinds.update(config)
                    return keybinds
            except Exception as e:
                print(f"Error loading keybind config: {e}")
                return self.default_keybinds.copy()
        else:
            return self.default_keybinds.copy()
    
    def save_keybind_config(self):
        """Save current keybind configuration to file"""
        try:
            with open(self.keybind_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.keybinds, f, indent=2)
        except Exception as e:
            print(f"Error saving keybind config: {e}")
    
    def check_keybind(self, pressed_key):
        """Check if the pressed key combination matches any configured keybind"""
        current_time = time.time()
        
        for action, config in self.keybinds.items():
            required_modifiers = set(config.get('modifiers', []))
            required_key = config.get('key', '')
            
            # Debug print (can be removed later)
            # print(f"Checking {action}: required_modifiers={required_modifiers}, required_key={required_key}")
            # print(f"Current: pressed_keys={self.pressed_keys}, pressed_key={pressed_key}")
            
            # Check if modifiers match
            if required_modifiers == self.pressed_keys and required_key == pressed_key:
                # print(f"Keybind match found for {action}")
                if action == 'next_step':
                    self.next_step()
                    self.last_action_time = current_time
                elif action == 'previous_step':
                    self.previous_step()
                    self.last_action_time = current_time
                elif action == 'quit_app':
                    self.quit_application()
                    self.last_action_time = current_time
                elif action == 'minimize_toggle':
                    self.toggle_minimize()
                    self.last_action_time = current_time
                break
    
    def get_controls_text(self):
        """Generate controls text based on current keybind configuration"""
        next_key = self.format_keybind(self.keybinds['next_step'])
        prev_key = self.format_keybind(self.keybinds['previous_step'])
        quit_key = self.format_keybind(self.keybinds['quit_app'])
        minimize_key = self.format_keybind(self.keybinds['minimize_toggle'])
        return f"{next_key}: Next | {prev_key}: Previous | {minimize_key}: Min/Max | {quit_key}: Quit"
    
    def format_keybind(self, keybind_config):
        """Format a keybind configuration for display"""
        modifiers = keybind_config.get('modifiers', [])
        key = keybind_config.get('key', '')
        
        modifier_text = '+'.join([mod.capitalize() for mod in modifiers])
        if modifier_text:
            return f"{modifier_text}+{key.upper()}"
        else:
            return key.upper()
    
    def open_settings(self):
        """Open the settings window for keybind customization"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings - Keybind Configuration")
        settings_window.geometry("500x400")
        settings_window.configure(bg='black')
        settings_window.attributes('-topmost', True)
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Title
        title_label = tk.Label(
            settings_window,
            text="Keybind Configuration",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='black'
        )
        title_label.pack(pady=10)
        
        # Keybind configuration frame
        config_frame = tk.Frame(settings_window, bg='black')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create keybind configuration widgets
        self.keybind_widgets = {}
        keybind_actions = [
            ("next_step", "Next Step"),
            ("previous_step", "Previous Step"),
            ("minimize_toggle", "Minimize/Maximize"),
            ("quit_app", "Quit Application")
        ]
        
        for action, label in keybind_actions:
            self.create_keybind_widget(config_frame, action, label)
        
        # Buttons frame
        button_frame = tk.Frame(settings_window, bg='black')
        button_frame.pack(pady=20)
        
        def save_settings():
            # Validate and save keybinds
            if self.validate_keybinds():
                self.save_keybind_config()
                # Restart keyboard listener with new keybinds
                self.restart_keyboard_listener()
                # Update controls display
                self.controls_label.config(text=self.get_controls_text())
                messagebox.showinfo("Success", "Keybind settings saved successfully!")
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Invalid keybind configuration. Please check for conflicts.")
        
        def reset_defaults():
            self.keybinds = self.default_keybinds.copy()
            self.update_keybind_widgets()
            messagebox.showinfo("Reset", "Keybinds reset to defaults")
        
        def cancel_settings():
            settings_window.destroy()
        
        tk.Button(button_frame, text="Save", command=save_settings,
                 bg='darkgreen', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset Defaults", command=reset_defaults,
                 bg='darkorange', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel_settings,
                 bg='darkred', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
    
    def create_keybind_widget(self, parent, action, label):
        """Create a keybind configuration widget"""
        frame = tk.Frame(parent, bg='black')
        frame.pack(fill=tk.X, pady=5)
        
        # Label
        tk.Label(frame, text=f"{label}:", font=('Arial', 10), fg='white', bg='black').pack(side=tk.LEFT)
        
        # Modifiers frame
        modifiers_frame = tk.Frame(frame, bg='black')
        modifiers_frame.pack(side=tk.LEFT, padx=10)
        
        # Modifier radio buttons (only one can be selected)
        modifier_var = tk.StringVar(value=self.get_current_modifier(action))
        modifier_vars = {'modifier': modifier_var}
        
        # No modifier option
        rb_none = tk.Radiobutton(
            modifiers_frame,
            text="None",
            variable=modifier_var,
            value="none",
            font=('Arial', 9),
            fg='white',
            bg='black',
            selectcolor='darkgray',
            activebackground='black',
            activeforeground='white'
        )
        rb_none.pack(side=tk.LEFT, padx=2)
        
        # Modifier options
        for modifier in ['shift', 'ctrl', 'alt']:
            rb = tk.Radiobutton(
                modifiers_frame,
                text=modifier.capitalize(),
                variable=modifier_var,
                value=modifier,
                font=('Arial', 9),
                fg='white',
                bg='black',
                selectcolor='darkgray',
                activebackground='black',
                activeforeground='white'
            )
            rb.pack(side=tk.LEFT, padx=2)
        
        # Key entry
        key_var = tk.StringVar(value=self.keybinds[action].get('key', ''))
        key_entry = tk.Entry(
            modifiers_frame,
            textvariable=key_var,
            font=('Arial', 9),
            width=5,
            bg='darkgray',
            fg='black'
        )
        key_entry.pack(side=tk.LEFT, padx=5)
        
        # Store widgets for later access
        self.keybind_widgets[action] = {
            'modifiers': modifier_vars,
            'key': key_var
        }
    
    def get_current_modifier(self, action):
        """Get the current modifier for an action (returns first modifier or 'none')"""
        modifiers = self.keybinds[action].get('modifiers', [])
        if modifiers:
            return modifiers[0]  # Return first modifier only
        return "none"
    
    def update_keybind_widgets(self):
        """Update keybind widgets with current configuration"""
        for action, widgets in self.keybind_widgets.items():
            config = self.keybinds[action]
            key = config.get('key', '')
            
            # Update modifier radio button
            current_modifier = self.get_current_modifier(action)
            widgets['modifiers']['modifier'].set(current_modifier)
            
            # Update key entry
            widgets['key'].set(key)
    
    def validate_keybinds(self):
        """Validate keybind configuration and update internal state"""
        new_keybinds = {}
        
        for action, widgets in self.keybind_widgets.items():
            # Get selected modifier (only one allowed now)
            selected_modifier = widgets['modifiers']['modifier'].get()
            modifiers = []
            if selected_modifier != "none":
                modifiers = [selected_modifier]
            
            # Get key
            key = widgets['key'].get().strip().lower()
            
            if not key:
                messagebox.showerror("Error", f"Please specify a key for {action}")
                return False
            
            new_keybinds[action] = {
                'modifiers': modifiers,
                'key': key
            }
        
        # Check for conflicts
        keybind_strings = []
        for action, config in new_keybinds.items():
            if config['modifiers']:
                keybind_str = f"{'+'.join(config['modifiers'])}+{config['key']}"
            else:
                keybind_str = config['key']
            
            if keybind_str in keybind_strings:
                messagebox.showerror("Error", f"Duplicate keybind detected: {keybind_str}")
                return False
            keybind_strings.append(keybind_str)
        
        # Update internal keybinds
        self.keybinds = new_keybinds
        return True
    
    def toggle_minimize(self):
        """Toggle between minimized and maximized state"""
        if self.is_minimized:
            # Restore the window
            self.root.deiconify()
            self.root.attributes('-alpha', 0.9)
            self.is_minimized = False
        else:
            # Minimize the window (make it invisible but keep it running)
            self.root.withdraw()
            self.is_minimized = True
        
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
    
    def start_drag(self, event):
        """Start dragging the window"""
        self.is_dragging = True
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.drag_window_x = self.root.winfo_x()
        self.drag_window_y = self.root.winfo_y()
    
    def drag_window(self, event):
        """Handle window dragging"""
        if self.is_dragging:
            # Calculate new window position
            delta_x = event.x_root - self.drag_start_x
            delta_y = event.y_root - self.drag_start_y
            new_x = self.drag_window_x + delta_x
            new_y = self.drag_window_y + delta_y
            
            # Update window position
            self.root.geometry(f"+{new_x}+{new_y}")
    
    def stop_drag(self, event):
        """Stop dragging the window"""
        self.is_dragging = False

if __name__ == "__main__":
    tracker = VTaskTracker()
    try:
        tracker.run()
    except KeyboardInterrupt:
        tracker.cleanup()
