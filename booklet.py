#!/usr/bin/env python3

import argparse
import doctest
import subprocess
import tempfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Arrange PDF pages for booklet printing. Pads to a multiple of 4 pages if needed."
    )

    parser.add_argument("input", type=str, help="Input PDF file")
    parser.add_argument("output", type=str, help="Output PDF file")
    parser.add_argument(
        "--padding",
        choices=["end", "before-end"],
        default="before-end",
        help="Where to pad: at or immediately before the end of the document",
    )

    return parser.parse_args()


class BookletError(Exception):
    pass


def compute_booklet_order(page_count: int) -> list[int]:
    """
    Compute correct page order for booklet printing.

    >>> compute_booklet_order(0)
    Traceback (most recent call last):
        ...
    booklet.BookletError: Page count (0) must be positive

    >>> compute_booklet_order(3)
    Traceback (most recent call last):
        ...
    booklet.BookletError: Page count (3) must be a multiple of 4

    >>> compute_booklet_order(8)
    [8, 1, 2, 7, 6, 3, 4, 5]

    >>> compute_booklet_order(16)
    [16, 1, 2, 15, 14, 3, 4, 13, 12, 5, 6, 11, 10, 7, 8, 9]
    """

    if page_count < 1:
        raise BookletError(f"Page count ({page_count}) must be positive")

    if page_count % 4 != 0:
        raise BookletError(f"Page count ({page_count}) must be a multiple of 4")

    booklet_page_order = []

    for i in range(1, page_count // 2, 2):
        booklet_page_order += [page_count - i + 1, i, i + 1, page_count - i]

    return booklet_page_order


def get_page_count(pdf: str) -> int:
    output = subprocess.check_output(["qpdf", "--show-npages", pdf], text=True)
    return int(output.strip())


def generate_booklet_pdf(
    input_pdf: str, page_order: list[int], output_pdf: str
) -> None:
    # QPDF requires a comma separated page list like "4,1,2,3"
    page_order_command = ",".join(map(str, page_order))

    subprocess.run(
        ["qpdf", input_pdf, "--pages", ".", page_order_command, "--", output_pdf],
        check=True,
    )


def generate_padded_pdf(input_pdf: str, padding: str) -> str:
    page_count = get_page_count(input_pdf)
    padding_count = (-page_count) % 4

    if padding_count == 0:
        return input_pdf

    command = ["qpdf", input_pdf, "--pages"]
    padding_pdf = "blank-a5.pdf"
    padding_command = ",".join(["1"] * padding_count)

    if padding == "end":
        # Add entire input file, then the padding.
        command += [".", "1-z", padding_pdf, padding_command]
    elif padding == "before-end":
        # Add entire input file except last page, then padding, then the last page.
        command += [".", "1-r2", padding_pdf, padding_command, ".", "z"]
    else:
        raise BookletError(f"Invalid padding option: {padding}")

    padded_pdf = tempfile.NamedTemporaryFile().name
    command += ["--", padded_pdf]
    subprocess.run(command, check=True)
    return padded_pdf


if __name__ == "__main__":
    args = parse_args()

    try:
        padded_pdf = generate_padded_pdf(args.input, args.padding)
        page_count = get_page_count(padded_pdf)
        page_order = compute_booklet_order(page_count)
        generate_booklet_pdf(padded_pdf, page_order, args.output)
        print(f"Success! Output file generated: {args.output}")

    except (BookletError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}")
        exit(1)
