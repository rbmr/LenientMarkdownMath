import pytest
from typing import NamedTuple
from main import process_content


class TestCase(NamedTuple):
    name: str
    input_text: str
    expected_output: str
    description: str = ""


TEST_CASES = [
    TestCase(
        name="Input 1",
        description="Simple bullet with inline math",
        input_text=(
            "- Bullet $$\\text{Some Text}$$\n"
            "- Bullet 2"
        ),
        expected_output=(
            "- Bullet\n"
            "    $$\n"
            "    \\text{Some Text}\n"
            "    $$\n"
            "- Bullet 2"
        )
    ),
    TestCase(
        name="Input 2",
        description="Nested indentation",
        input_text=(
            "- Outer bullet 1\n"
            "    - Inner bullet 1 $$\\text{Some Text}$$\n"
            "    - Inner bullet 2\n"
            "- Outer bullet 2"
        ),
        expected_output=(
            "- Outer bullet 1\n"
            "    - Inner bullet 1\n"
            "        $$\n"
            "        \\text{Some Text}\n"
            "        $$\n"
            "    - Inner bullet 2\n"
            "- Outer bullet 2"
        )
    ),
    TestCase(
        name="Input 3",
        description="Multiple math blocks in one line",
        input_text=(
            "- Bullet 1 $$\\text{Some Text}$$some more text$$\\text{Some more text}$$\n"
            "- Bullet 2"
        ),
        expected_output=(
            "- Bullet 1\n"
            "    $$\n"
            "    \\text{Some Text}\n"
            "    $$\n"
            "    some more text\n"
            "    $$\n"
            "    \\text{Some more text}\n"
            "    $$\n"
            "- Bullet 2"
        )
    ),
    TestCase(
        name="Input 4",
        description="Malformed bullet (no space after dash)",
        input_text=(
            "-Not really a bullet $$\\text{Some Text}$$ some more text\n"
            "- Really a bullet"
        ),
        expected_output=(
            "-Not really a bullet\n"
            "$$\n"
            "\\text{Some Text}\n"
            "$$\n"
            "some more text\n"
            "- Really a bullet"
        )
    ),
    TestCase(
        name="Input 5",
        description="Extra spaces after dash",
        input_text=(
            "-  More than one space $$\\text{Some text}$$\n"
            "- Only one space"
        ),
        expected_output=(
            "-  More than one space\n"
            "    $$\n"
            "    \\text{Some text}\n"
            "    $$\n"
            "- Only one space"
        )
    ),
    TestCase(
        name="Input 6",
        description="Newline immediately within bullet",
        input_text=(
            "-\n"
            "A newline $$\\text{Some text}$$\n"
            "- Just a space"
        ),
        expected_output=(
            "-\n"
            "A newline\n"
            "$$\n"
            "\\text{Some text}\n"
            "$$\n"
            "- Just a space"
        )
    ),
    TestCase(
        name="Input 7",
        description="Already correctly formatted (Idempotency)",
        input_text=(
            "- Already correct\n"
            "    $$\n"
            "    \\text{Some Text}\n"
            "    $$\n"
            "- No Formula here"
        ),
        expected_output=(
            "- Already correct\n"
            "    $$\n"
            "    \\text{Some Text}\n"
            "    $$\n"
            "- No Formula here"
        )
    ),
    TestCase(
        name="Input 8",
        description="Partial/Malformed block formatting",
        input_text=(
            "- Almost correct\n"
            "    $$\n"
            "    \\text{Some Text}$$\n"
            "- Also almost correct $$\n"
            "    \\text{Some Text}\n"
            "    $$\n"
            "- Also also almost correct\n"
            "    $$\\text{Some Text}\n"
            "    $$"
        ),
        expected_output=(
            "- Almost correct\n"
            "    $$\n"
            "    \\text{Some Text}\n"
            "    $$\n"
            "- Also almost correct\n"
            "    $$\n"
            "    \\text{Some Text}\n"
            "    $$\n"
            "- Also also almost correct\n"
            "    $$\n"
            "    \\text{Some Text}\n"
            "    $$"
        )
    ),
    TestCase(
        name="Input 9",
        description="Ordered Lists",
        input_text=(
            "1. First item $$\\text{A}$$\n"
            "2. Second item\n"
            "    1. Nested item $$\\text{B}$$"
        ),
        expected_output=(
            "1. First item\n"
            "    $$\n"
            "    \\text{A}\n"
            "    $$\n"
            "2. Second item\n"
            "    1. Nested item\n"
            "        $$\n"
            "        \\text{B}\n"
            "        $$\n"
        )
    ),
    TestCase(
        name="Input 10",
        description="Deep Nesting",
        input_text=(
            "- Level 1\n"
            "    - Level 2\n"
            "        - Level 3 $$\\text{Deep Math}$$"
        ),
        expected_output=(
            "- Level 1\n"
            "    - Level 2\n"
            "        - Level 3\n"
            "            $$\n"
            "            \\text{Deep Math}\n"
            "            $$"
        )
    ),
    TestCase(
        name="Input 11",
        description="Indented Text (Non-List Context)",
        input_text=(
            "Unindented text\n"
            "    This is just indented text, not a list. $$\\text{Math}$$\n"
            "    \n"
            "    Another indented line."
        ),
        expected_output=(
            "Unindented text\n"
            "    This is just indented text, not a list.\n"
            "    $$\n"
            "    \\text{Math}\n"
            "    $$\n"
            "    \n"
            "    Another indented line."
        )
    ),
    TestCase(
        name="Input 12",
        description="Math immediately following List Marker",
        input_text=(
            "- $$f(x) = x^2$$\n"
            "- text after"
        ),
        expected_output=(
            "- \n"
            "    $$\n"
            "    f(x) = x^2\n"
            "    $$\n"
            "- text after"
        )
    ),
    TestCase(
        name="Input 13",
        description="Mixed markers and Trailing text",
        input_text=(
            "* Star marker $$\\text{Math 1}$$ continuation text\n"
            "+ Plus marker $$\\text{Math 2}$$"
        ),
        expected_output=(
            "* Star marker\n"
            "    $$\n"
            "    \\text{Math 1}\n"
            "    $$\n"
            "    continuation text\n"
            "+ Plus marker\n"
            "    $$\n"
            "    \\text{Math 2}\n"
            "    $$"
        )
    ),
    TestCase(
        name="Input 14",
        description="Empty or Whitespace-only Math",
        input_text=(
            "- Empty math block $$ $$\n"
            "- Whitespace block $$ $$"
        ),
        expected_output=(
            "- Empty math block\n"
            "    $$\n"
            "    $$\n"
            "- Whitespace block\n"
            "    $$\n"
            "    $$"
        )
    ),
    TestCase(
        name="Input 15",
        description="Existing Multi-line (Messy)",
        input_text=(
            "- Messy start $$\n"
            "\\text{Line 1}\n"
            "  \\text{Line 2} $$ continuation\n"
            "- Some stuff"
        ),
        expected_output=(
            "- Messy start\n"
            "    $$\n"
            "    \\text{Line 1}\n"
            "  \\text{Line 2}\n"
            "    $$\n"
            "    continuation\n"
            "- Some stuff"
        )
    ),
    TestCase(
        name="Input 16",
        description="Escaped Dollar signs",
        input_text=(
            "- This is not math: \\$$\\text{literal}\\$$\n"
            "- Mixed: \\$$not math, but this is\\$$$$ \\text{math} $$"
        ),
        expected_output=(
            "- This is not math: \\$$\\text{literal}\\$$\n"
            "- Mixed: \\$$not math, but this is\\$$\n"
            "    $$\n"
            "    \\text{math}\n"
            "    $$"
        )
    ),
    TestCase(
        name="Input 17",
        description="Code blocks (Should be ignored)",
        input_text=(
            "```latex\n"
            "$$\\text{ignore me}$$\n"
            "```"
        ),
        expected_output=(
            "```latex\n"
            "$$\\text{ignore me}$$\n"
            "```"
        )
    ),
    TestCase(
        name="Input 18",
        description="Task lists",
        input_text=(
            "- [ ] Unchecked task $$\\text{math}$$ \n"
            "- [x] Checked task $$\\text{math}$$"
        ),
        expected_output=(
            "- [ ] Unchecked task\n"
            "    $$\n"
            "    \\text{math}\n"
            "    $$\n"
            "- [x] Checked task\n"
            "    $$\n"
            "    \\text{math}\n"
            "    $$"
        )
    ),
    TestCase(
        name="Input 19",
        description="Quoted math",
        input_text=(
            "> This is a quote $$\\text{quoted math}$$\n"
            "> Continuation"
        ),
        expected_output=(
            "> This is a quote\n"
            "> $$\n"
            "> \\text{quoted math}\n"
            "> $$\n"
            "> Continuation"
        )
    ),
    TestCase(
        name="Input 20",
        description="Mixed delimiters (inline vs block)",
        input_text=(
            "- Let $x$ be a variable and $$x^2$$ be the square."
        ),
        expected_output=(
            "- Let $x$ be a variable and\n"
            "    $$\n"
            "    x^2\n"
            "    $$\n"
            "    be the square."
        )
    ),
    TestCase(
        name="Input 21",
        description="Tables (Should convert $$ to $)",
        input_text=(
            "| Column 1 | Column 2 |\n"
            "| :--- | :--- |\n"
            "| Text | $$\\text{Math in table}$$ |"
        ),
        expected_output=(
            "| Column 1 | Column 2 |\n"
            "| :--- | :--- |\n"
            "| Text | $\\text{Math in table}$ |"
        )
    ),
    TestCase(
        name="Input 22",
        description="Links (Should convert $$ to $)",
        input_text=(
            "- Click here: [$$\\text{Link}$$](http://example.com)"
        ),
        expected_output=(
            "- Click here: [$\\text{Link}$](http://example.com)"
        )
    ),
    TestCase(
        name="Input 23",
        description="Footnotes (Should trigger list indentation)",
        input_text=(
            "[^1]: This is a footnote with $$x^2$$"
        ),
        expected_output=(
            "[^1]: This is a footnote with\n"
            "    $$\n"
            "    x^2\n"
            "    $$"
        )
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=lambda c: c.name)
def test_process_content(case: TestCase):
    """
    Executes the process_content function against the defined test cases.
    Verifies that the output matches the strict formatting rules defined.
    """
    actual_output = process_content(case.input_text)

    # Using a detailed assertion error message to help debug spacing/newlines
    assert actual_output.strip() == case.expected_output.strip(), \
        f"\nFailed Case: {case.name} ({case.description})\n" \
        f"EXPECTED:\n{case.expected_output!r}\n" \
        f"ACTUAL:\n{actual_output!r}"