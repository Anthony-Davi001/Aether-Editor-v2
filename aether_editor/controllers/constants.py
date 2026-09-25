"""
Aether Editor - Configuration Constants.

This module contains the default templates and text constants used 
by the editor interface and preview engine.

Attributes:
    EXAMPLE_MD (string): This is a simple guide of markdown use, with examples and explanations

Author: Anthony Davi <anthonyvieira789@gmail.com>
"""

EXAMPLE_MD = """# Welcome to Aether Editor!

This document is a quick guide to help you learn basic Markdown formatting. Edit this text on the left panel and watch the **PDF preview** update automatically on the right!

---

## Basic Text Formatting

You can easily emphasize your words:

- Use double asterisks for **bold text**.
- Use a single asterisk for *italic text*.
- Or combine both for ***bold and italic***.

To highlight something as inline code within a sentence, use backticks: `var x = 10`.

## Organized Lists

**Task List:**

- Type your text in Markdown.
- Wait half a second (debounce) for the preview to update.
- Click "Export to PDF" on the top bar.

**Numbered List (Step-by-Step):**

1. Install dependencies.
2. Run the script.
3. Start typing!

## Quotes and Links

Blockquotes are great for highlighting ideas or important notes:

> "Simplicity is the ultimate sophistication." - Leonardo da Vinci

You can also easily insert [links to web pages](https://example.com).

## Syntax Highlighted Code Blocks

You can create code blocks by wrapping text with triple backticks and the language name. See how Python gets highlighted:

```python
def greet(name):
    \"\"\"A simple welcome function.\"\"\"
    message = f"Hello, {name}! Enjoy using the editor."
    return message

print(greet("Your Name"))
```
"""