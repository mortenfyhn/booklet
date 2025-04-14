# Booklet

A little utility for booklet printing. It fixes the page ordering of your pdf so that you can print it as a booklet with four pages per sheet (two on each side). If your document isn't a multiple of four pages, it can pad with blank pages.

Shoutouts to

* https://gitlab.com/pdftools/pdfbook for inspiration, and
* https://github.com/georgjaehnig/booklet-page-calculator for math verification.

## Dependencies

* qpdf
* Python 3.9+

## Usage

```sh
./booklet.py input.pdf
```

If you want more info:

```sh
./booklet.py --help
```

## Running tests

```sh
python3 -m doctest booklet.py --verbose
```
