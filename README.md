# VTask Tracker

A transparent overlay application that displays step-by-step task guides with keyboard navigation. Perfect for speedruns, tutorials, checklists, and any sequential process you need to follow while gaming or working.

## Features

- **Always-on-top transparent overlay** - Stays visible over any application
- **Step-by-step guide display** - Navigate through your tasks one at a time
- **Keyboard navigation**:
  - `Shift + D`: Next step
  - `Shift + S`: Previous step
  - `Shift + Q`: Quit application
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

- `Shift + D`: Next step
- `Shift + S`: Previous step
- `Shift + Q`: Quit application
- The overlay works globally, even when other applications are in focus

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
