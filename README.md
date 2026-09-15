# DeHash
**The Ultimate Python & Jupyter Comment Cleaner**

Tired of messy code files cluttered with old notes, commented-out code, and random `# TODOs`? Meet **DeHash**! 

DeHash is a sleek, Dark Mode GUI application built in Python that lets you safely search, preview, and stealthily assassinate comments from `.py` and `.ipynb` (Jupyter Notebook) files. 

Unlike clunky regex scripts that accidentally delete `#` symbols hiding inside your strings or URLs, DeHash uses Python's built-in `tokenize` brain. It knows exactly what is a comment and what is actual code.

## Why It's Awesome

* **Dual File Power:** Natively handles standard Python scripts (`.py`) and Jupyter Notebooks (`.ipynb`) without destroying your JSON structures.
* **Sleek Dark Mode:** A clean, modern, VSCode-inspired dark theme because your eyes deserve a break.
* **Live Code Preview:** See your code exactly as it is with built-in syntax highlighting for keywords, strings, and comments.
* **Ninja Navigation:** 
  * **Left-Click:** Select or deselect the comments you want to banish.
  * **Right-Click:** Instantly scrolls the preview window to highlight exactly where that comment lives in your code.
* **Real-Time Search:** Looking for a specific tag? Type in the Find box and watch the list filter instantly.
* **Safety First:** Prompts you to create a `.bak` backup file of your original code before applying any destructive strikes.
* **Future-Proof:** Built using modern Tkinter methods (`trace_add`), making it fully compatible with Python 3.14+.
* **Zero Dependencies:** Runs 100% on Python's standard library. No `pip install` required. Just run and go!

## Prerequisites

* Python 3.6 or higher (Tested and working beautifully up to Python 3.14).
* Tkinter (Usually included with standard Python installations out of the box).

## Installation

1. Clone this repository or download the script directly:
   ```bash
   git clone [https://github.com/ManitShukla/DeHash.git](https://github.com/ManitShukla/DeHash.git)
   ```

2. Navigate to the folder:
   ```bash
   cd dehash

   ```



## How to Play (Usage)

Boot up the app from your terminal or command prompt:

```bash
python dehash.py

```

### DeHashing Instructions:

1. Click **Select .py or .ipynb File** and pick the file you want to clean.
2. The left panel will instantly load up every comment it finds.
3. Use the **Find** box to filter for specific things (like "TODO" or "fix this").
4. **Right-click** any comment in the list to teleport to its exact location in the right-hand code preview.
5. **Left-click** (or mash "Select All") to highlight the comments you want to remove.
6. Click **Delete Selected Comments**. (Don't worry, it will ask if you want to create a backup first!)

## The Jupyter Magic

Jupyter Notebooks (`.ipynb`) are basically giant JSON files, which makes editing them outside of Jupyter scary. DeHash handles this flawlessly!

It concatenates code cells in the preview panel with visible `# --- Code Cell X ---` dividers. When you delete a comment, DeHash safely reaches into the JSON tree and modifies *only* that specific line in that specific cell. No corrupted files, no broken notebooks. Just pure, clean code.
