import re


def process_content(text: str) -> str:
    """
    Reformats Markdown content to ensure all $$ block formulas are properly
    indented and placed on their own lines.
    """

    # --- Step 1: Protection (Code Blocks & Escaped Delimiters) ---
    code_blocks = {}

    def store_code_block(match):
        key = f"__CODE_BLOCK_{len(code_blocks)}__"
        code_blocks[key] = match.group(0)
        return key

    # Protect fenced code blocks (```...```) and inline code (`...`)
    # We use ?ms to handle multi-line blocks correctly
    text = re.sub(r'(?ms)^(\s*`{3,}).*?\1', store_code_block, text)
    text = re.sub(r'(`[^`\n]+`)', store_code_block, text)

    # Protect escaped dollar signs (\$$)
    escaped_dollar_key = "__ESCAPED_DOLLAR_LITERAL__"
    text = text.replace(r'\$$', escaped_dollar_key)

    lines = text.split('\n')
    output_lines = []

    # State tracking
    inside_math_block = False
    current_math_indent = ""

    # Regex definitions
    # Matches list markers: "- ", "* ", "+ ", "1. ", "- [ ] "
    # Group 1: Leading Indent
    # Group 2: The Marker
    # Group 3: Trailing Space
    list_pattern = re.compile(r'^(\s*)([-*+]|\d+\.|- \[[ x]\]|\[\^[^\]]+\]:)(\s+)')

    # Matches blockquotes: "> ", ">> "
    quote_pattern = re.compile(r'^((?:>\s?)+)')

    for line in lines:
        # --- Pre-check: Tables and Links ---
        # If line looks like a table row or a link with math, convert $$ to $ (Tests 21, 22)
        if re.match(r'^\s*\|', line) or re.search(r'\[\s*\$\$', line):
            cleaned_line = line.replace('$$', '$')
            output_lines.append(cleaned_line)
            continue

        # --- Pre-check: Idempotency / Pure Delimiter Lines ---
        # If a line is JUST whitespace and $$, it is already a structural delimiter.
        if re.match(r'^\s*\$\$\s*$', line):
            if inside_math_block:
                # Closing an existing block
                output_lines.append(f"{current_math_indent}$$")
                inside_math_block = False
            else:
                # Opening a new block (already on its own line)
                # We calculate indent based on this line's whitespace
                ws_match = re.match(r'^(\s*)', line)
                current_math_indent = ws_match.group(1) if ws_match else ""
                output_lines.append(f"{current_math_indent}$$")
                inside_math_block = True
            continue

        # --- Main Parsing Logic ---

        # Split line into tokens: Text, $$, Text, $$, etc.
        tokens = re.split(r'(\$\$)', line)

        # If no delimiters are found, handle based on state
        if len(tokens) == 1:
            content = tokens[0]
            if inside_math_block:
                # We are inside a multi-line block, just indent and print content
                clean_content = content.strip()
                if clean_content:
                    output_lines.append(f"{current_math_indent}{clean_content}")
            else:
                # Normal text line, pass through exactly as is
                output_lines.append(content)
            continue

        # If we have delimiters, we need to calculate the indentation context for this line
        # This indent applies to ANY math block opening on this line.

        line_math_indent = ""

        list_match = list_pattern.match(line)
        quote_match = quote_pattern.match(line)

        if list_match:
            # It's a list item. Indent is base indent + 4 spaces.
            base_indent = list_match.group(1)
            line_math_indent = base_indent + "    "
        elif quote_match:
            # It's a blockquote. Preserve the quote markers.
            line_math_indent = quote_match.group(1)
        else:
            # Standard text. Preserve leading whitespace.
            ws_match = re.match(r'^(\s*)', line)
            line_math_indent = ws_match.group(1) if ws_match else ""

        # Process Tokens
        for i, token in enumerate(tokens):
            if token == '$$':
                if inside_math_block:
                    # Closing a block
                    output_lines.append(f"{current_math_indent}$$")
                    inside_math_block = False
                else:
                    # Opening a block
                    # Update the current global indent to this line's calculated indent
                    current_math_indent = line_math_indent
                    output_lines.append(f"{current_math_indent}$$")
                    inside_math_block = True
            else:
                # Text Content
                if not token.strip():
                    # Handle purely whitespace tokens
                    if not inside_math_block:
                        # If we are at the start of the line (index 0) and it's a list marker line
                        # we usually need to print it.
                        if i == 0:
                            # Edge case: "- $$...". Token 0 is "- ".
                            # If we strip it, we lose the list marker format.
                            if list_match and token == list_match.group(0):
                                output_lines.append(token)
                            elif token:
                                # Just whitespace at start of line (e.g. indented text)
                                pass
                    continue

                if inside_math_block:
                    # Content inside math delimiters (on a line that has delimiters)
                    clean_text = token.strip()
                    if clean_text:
                        # Use line_math_indent to respect the physical indentation of this line
                        # This fixes cases where inner content has specific relative indentation
                        output_lines.append(f"{line_math_indent}{clean_text}")
                else:
                    # Content outside math delimiters
                    if i == 0:
                        # Text BEFORE the first $$ on the line
                        is_pure_marker = False
                        if list_match:
                            # Check if this token IS exactly the marker (e.g. "- ")
                            if token == list_match.group(0):
                                is_pure_marker = True

                        if is_pure_marker:
                            output_lines.append(token)
                        else:
                            output_lines.append(token.rstrip())
                    else:
                        # Text AFTER a $$ (Continuation)
                        # Must be moved to new line with proper indentation
                        clean_text = token.strip()
                        if clean_text:
                            # Use current_math_indent (block indent) for continuation text
                            # to align it with the block that just closed.
                            output_lines.append(f"{current_math_indent}{clean_text}")

    # --- Step 3: Cleanup ---
    result = "\n".join(output_lines)

    # Restore escaped dollars
    result = result.replace(escaped_dollar_key, r'\$$')

    # Restore code blocks
    for key, code in code_blocks.items():
        result = result.replace(key, code)

    return result