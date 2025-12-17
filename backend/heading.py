import re

# SECTION_KEYWORDS = {
#     "abstract": ["abstract"],
#     "introduction": ["introduction", "background", "overview"],
#     "methods": ["method", "methods", "methodology", "approach", "experimental setup", "experiments"],
#     "results": ["results", "evaluation", "findings", "analysis", "performance"],
#     "conclusion": ["conclusion", "discussion", "future work", "summary"],
# }
# HEADING_PATTERN = re.compile(
#     r"^\s*(\d+(\.\d+)*)?\s*[A-Z][A-Za-z ]{1,60}$"
# )


def detect_heading(text, block_font_size, body_text_size, y0, previousBlock_y1):

    # Font size check
    big_enough = block_font_size >= body_text_size * 1.10  # 10% bigger than body text

    # Text length check
    short_enough = len(text.split()) <= 7

    # Punctuation check
    clean_text = text.strip()
    no_period = not clean_text.endswith(".")

    #Handle the very first block on a page:
    if previousBlock_y1 is None: # or if previousBlock_y1 == 0.0
        # Skip the gap check for the first block, or return None immediately if you only check text properties
        return None

    # Spacing pattern check
    spaced = previousBlock_y1 is None or (y0 - previousBlock_y1 > 10)

    if big_enough and short_enough and no_period and spaced:
        return text

    return None




