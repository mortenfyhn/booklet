#!/usr/bin/env python3

import argparse
import doctest
import subprocess


class BookletError(Exception):
    pass


def reorder(page_count: int) -> list[int]:
    """
    Compute correct page order for booklet printing.

    >>> reorder(0)
    Traceback (most recent call last):
        ...
    booklet.BookletError: Page count (0) must be positive

    >>> reorder(3)
    Traceback (most recent call last):
        ...
    booklet.BookletError: Page count (3) must be a multiple of 4

    >>> reorder(8)
    [8, 1, 2, 7, 6, 3, 4, 5]

    >>> reorder(16)
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


def get_page_count(file: str) -> int:
    output = subprocess.check_output(["qpdf", "--show-npages", file], text=True)
    return int(output.strip())


def generate_booklet_pdf(file: str, page_order: list[int]) -> str:
    # TODO describe
    # may throw subprocess.CalledProcessError

    # QPDF requires a comma separated page list like "4,1,2,3"
    page_order_string = ",".join(map(str, page_order))

    output_filename = "output.pdf"

    subprocess.run(
        ["qpdf", file, "--pages", ".", page_order_string, "--", output_filename],
        check=True,
    )

    return output_filename

def generate_padded_pdf(file: str, insert_blank_pages: str) -> str:

    page_count = get_page_count(file)

    padding_count = (-page_count) % 4
    padding=",".join(["1"] * padding_count)

    blank_page_file="blank-a5.pdf"
    padded_pdf="padded.pdf"

    # adjust 1-r2
    # adjust number of pages


    # none -> just return input
    # last -> first = "1-z", last = "" (try to get nothing)
    # before-last -> first = "1-r2", last = "z"

    # maybe need to just build the array instead of defining strings

    if padding_count == 0:
        return file

    if insert_blank_pages == "none":
        return file

    command = ["qpdf", file, "--pages"]

    if insert_blank_pages == "last":
        # Add entire input file, then the blank pages.
        command += [".", "1-z", blank_page_file, padding]
    elif insert_blank_pages == "before-last":
        # Add input file except last page, then blank pages, then the last page.
        command += [".", "1-r2", blank_page_file, padding, ".", "z"]
    else:
        raise BookletError("invalid option todo ")

    command += ["--", padded_pdf]


    subprocess.run(command,
        check=True,
    )

    return padded_pdf





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-tests", action="store_true")
    parser.add_argument(
        "--insert-blank-pages",
        choices=["none", "last", "before-last"],
        default="none",
        help="Insert blank pages to pad to multiple of 4",
    )
    parser.add_argument("file", type=str)
    args = parser.parse_args()

    try:

        # pad with blank pages (to guarantee x4)
        # compute new ordering
        # generate booklet order pdf

        # page_count = get_page_count(file)

        padded_pdf = generate_padded_pdf(args.file, args.insert_blank_pages)



        page_count = get_page_count(padded_pdf)
        page_order = reorder(page_count)



        output_filename = generate_booklet_pdf(padded_pdf, page_order)



        print(f"Success! Output file generated: {output_filename}")

    except (BookletError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}")
        exit(1)
