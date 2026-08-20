<div align="center">
    <a href="https://www.gnu.org/licenses/gpl-3.0">
        <img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-4c1.svg" />
    </a>
    <a href="https://docs.python.org/3/">
        <img alt="Made With Python" src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" />
    </a>
    <a href="https://www.markdownguide.org/basic-syntax/">
        <img alt="Markdown Badge" src="https://img.shields.io/badge/-Markdown-000000?style=flat&logo=markdown&logoColor=white" />
    </a><br>
    <a href="https://docs.python.org/3/library/tkinter.html">
        <img alt="Tkinter Badge" src="https://img.shields.io/badge/-Tkinter-3776AB?style=flat&logo=python&logoColor=white" />
    </a>
</div>
<br>

# Aether Editor

<img src="aether_icon.png" width=150px  align="right">

### Create documents by writing markdown

A lightweight and efficient Markdown editor built with Python and Tkinter, featuring a live PDF preview engine and dynamic syntax highlighting.

#### Current features:

- **Markdown Writing & Outline:** Write seamlessly with an auto-generated document outline for easy navigation.
- **Live PDF Preview:** Real-time PDF rendering side-by-side using PyMuPDF.
- **Export to PDF:** Convert and save your markdown documents directly to PDF.
- **Syntax Highlighting:** Custom regex-based highlighting for Markdown elements.
- **Styling Themes:** Beautiful Light and Dark modes powered by `sv_ttk`.

## Visualization: 

![visualization of app](preview.png)

## How to download and use:

#### Clone the repository

```bash
git clone https://github.com/Anthony-Davi001/Aether-Editor-v2.git
cd Aether-Editor-v2
```

#### Install th dependencies

```bash
pip install -r requirements.txt
```

#### Run the application

```bash
python3 aether_editor/main.py
```

## Building the Executable

You can compile the project into a standalone executable using the build automation script:

#### Compile the application

```bash
python3 build.py
# This cleans previous builds and compiles the project using PyInstaller. The binary will be available in the dist/ directory.
```

#### Clean build artifacts

To only remove temporary build directories (build/ and dist/) without compiling:

```bash
python3 build.py --clean
```

