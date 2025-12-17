import fitz
import os
import re
from pix2text import Pix2Text
import sys # Used for checking if P2T initialization failed


# Output directory where temporary formula images will be saved
OUTPUT_DIR = "formula_images"

# --- 1. PIX2TEXT INITIALIZATION (Run once) ---
try:
    # Initialize the P2T model globally or once per process
    # We use the 'math' recognition mode for high-accuracy formula conversion.
    p2t = Pix2Text(recognize_config={'model_type': 'math'})
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize Pix2Text. Please ensure installation is correct.")
    print(f"Error details: {e}", file=sys.stderr)
    p2t = None


# --- 2. FORMULA DETECTION HELPER ---
def is_formula_block(text, block_font_size, body_text_size):

    text = text.strip()
    if not text:
        return False

    # 1: size (too big to be a formula block)
    if not (body_text_size - 1.0 <= block_font_size <= body_text_size + 0.5):
        return False

    # 2: content (math symbols)
    math_symbols = r"[\=\+\-\*\/\^_{}\[\]\(\)><≈±\u0370-\u03FF\u2200-\u22FF]" 
    if not re.search(math_symbols, text):
        return False

    # 3: structure (Centered and short, or contains an equation number)
    is_short = len(text.split()) < 20
    is_equation_number = re.search(r"\s+\(\d{1,3}[a-z]?\s*\)$", text) # e.g., (1), (3a)

    if is_short or is_equation_number:
        # if more symbols than words)
        if len(text) > 5 and (sum(c.isalpha() for c in text) / len(text)) < 0.5:
            return True

    return False


# --- 3. IMAGE RENDERING HELPER (using fitz) ---
def render_block_to_image(page, block_coords, page_num, math_block_index):

    """ It renders the area defined by block_coords (x0, y0, x1, y1)
        from the 'Page'(by using fitz) object into a PNG file. """

    if not isinstance(page, fitz.Page):
        raise TypeError("Input 'page' must be a valid fitz.Page object.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rect = fitz.Rect(block_coords)

    # Render with high DPI (: Dots Per Inch)
    pix = page.get_pixmap(clip=rect, dpi=300)

    filename = f"formula_p{page_num}_b{math_block_index}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    pix.save(filepath)

    return filepath


# --- 4. PIX2TEXT CONVERSION HELPER ---
def convert_image_to_LaTeX(image_path):

    """ It uses the local Pix2Text library
        to convert the image file to a LaTeX string."""

    if p2t is None:
        return f"$$ \\text{{P2T INITIALIZATION FAILED: Check log for details}} $$"

    try:
        # P2T processes the image file path directly
        result = p2t.recognize(image_path)

        # We expect a list of blocks; we take the text from the first one.
        if result and len(result) > 0:
            recognized_latex = result[0].get('text', '$$ \\text{P2T Empty Result} $$')

            # to ensure the output is wrapped in LaTeX math delimiters ($$ ... $$) for LLM
            if not recognized_latex.startswith('$$'):
                 recognized_latex = f"$$ {recognized_latex} $$"

            return recognized_latex

        return f"$$ \\text{{P2T No Formula Detected for: {os.path.basename(image_path)}}} $$"

    except Exception as e:

        print(f"Pix2Text Recognition Error on {image_path}: {e}", file=sys.stderr)
        return f"$$ \\text{{P2T RUNTIME ERROR: {os.path.basename(image_path)}}} $$"
    finally:
        # Clean up the temporary image file after processing
        if os.path.exists(image_path):
             os.remove(image_path)