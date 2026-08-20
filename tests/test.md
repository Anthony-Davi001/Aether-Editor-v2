# Welcome to Aether Editor!

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

## Syntax Highlighted Code Blocks

You can create code blocks by wrapping text with triple backticks and the language name. See how Python gets highlighted:

```python
def greet(name):
    """A simple welcome function."""
    message = f"Hello, {name}! Enjoy using the editor."
    return message

print(greet("Your Name"))
```