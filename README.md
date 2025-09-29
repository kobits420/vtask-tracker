# VTask Tracker

A transparent overlay application that displays step-by-step task guides with keyboard navigation. Perfect for speedruns, tutorials, checklists, and any sequential process you need to follow while gaming or working.

## Features

- **Always-on-top transparent overlay** - Stays visible over any application
- **Step-by-step guide display** - Navigate through your tasks one at a time
- **Customizable keyboard navigation**:
  - Default: `Shift + D`: Next step, `Shift + S`: Previous step, `Shift + R`: Minimize/Maximize, `Shift + Q`: Quit application
  - Fully customizable keybinds with modifier support (Shift, Ctrl, Alt)
  - Settings window for easy keybind configuration
  - Minimize/maximize functionality to hide/show overlay as needed
- **Template management**:
  - Create custom templates with the built-in editor
  - Load existing templates from JSON files
  - Export/save templates for sharing
- **Positioned in top-right corner** - Won't interfere with your main workflow

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python vrising_overlay.py
   ```

2. The overlay will appear in the top-right corner of your screen
3. Use the keyboard shortcuts to navigate through your steps

## Template Management

### Creating a New Template
1. Click the **"New Template"** button
2. Enter a template name
3. Add your steps (one per line)
4. Click **"Save Template"**

### Loading a Template
1. Click the **"Load Template"** button
2. Select a JSON file from your computer
3. The template will be loaded immediately

### Saving a Template
1. Click the **"Save Template"** button
2. Choose where to save the file
3. Your current template will be exported

## Keybind Customization

### Accessing Settings
1. Click the **"Settings"** button in the main overlay
2. The keybind configuration window will open

### Configuring Keybinds
1. For each action (Next Step, Previous Step, Minimize/Maximize, Quit Application):
   - Select one modifier key (None, Shift, Ctrl, Alt) using radio buttons
   - Enter the desired key in the text field
2. Click **"Save"** to apply changes
3. Click **"Reset Defaults"** to restore original keybinds
4. Click **"Cancel"** to discard changes

### Keybind Examples
- `Ctrl + N`: Next step
- `Ctrl + P`: Previous step  
- `F1`: Minimize/Maximize (no modifiers)
- `Alt + F4`: Quit application
- `F2`: Next step (no modifiers)

### Keybind Validation
- The system prevents duplicate keybind assignments
- All actions must have a key assigned
- Settings are automatically saved to `keybind_config.json`

## Template Format

Templates use a simple JSON format:

```json
{
  "title": "Your Custom Guide",
  "steps": [
    "Step 1: Do this first",
    "Step 2: Then do this",
    "Step 3: Finally, do this"
  ]
}
```

## Controls

### Default Keybinds
- `Shift + D`: Next step
- `Shift + S`: Previous step
- `Shift + R`: Minimize/Maximize overlay
- `Shift + Q`: Quit application

### Customization
- All keybinds can be customized through the Settings window
- Supports Shift, Ctrl, and Alt modifiers (one at a time)
- Works globally, even when other applications are in focus
- Settings are saved automatically and persist between sessions
- Minimize functionality allows you to hide the overlay when not needed

## Use Cases

- **Gaming**: Speedrun guides, boss fight strategies, quest walkthroughs
- **Work**: Process checklists, troubleshooting steps, training guides
- **Learning**: Tutorial steps, study guides, practice routines
- **Any sequential task** that benefits from step-by-step guidance

## Notes

- The overlay is semi-transparent and always stays on top
- Positioned in the top-right corner to minimize interference
- Includes a sample guide to get you started
- All templates are saved as JSON files for easy sharing

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve VTask Tracker!
