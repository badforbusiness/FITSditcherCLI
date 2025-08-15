# FITSditcherCLI

A simple Python command-line tool to help you visually triage astronomical FITS files.

Standard file explorers can't generate useful thumbnails for the high dynamic range FITS images, making it difficult to sift through a night's worth of data to find frames ruined by clouds, bad tracking, or satellites. This tool provides a simple `generate` and `clean` workflow to solve this problem.

## Features

* **Generate Previews:** Quickly creates stretched, easy-to-view JPEG previews for an entire directory of FITS files.
* **Clean Up Originals:** Safely deletes the original FITS files that correspond to the previews you've manually removed.
* **Safety First:** The `clean` command runs in a "dry run" mode by default, showing you what will be deleted without touching any files. Deletion only occurs when you use the `--force` flag.
* **Simple Interface:** A straightforward CLI for easy integration into your processing workflow.

## The Workflow

1.  **Generate:** Run `fits_triage.py generate` on your data directory. A `previews` subfolder will be created containing JPEGs.
2.  **Cull:** Manually look through the `previews` folder and delete the JPEGs for any bad frames (e.g., cloudy, trailed, etc.).
3.  **Clean (Dry Run):** Run `fits_triage.py clean` to see a list of the original FITS files that are marked for deletion.
4.  **Clean (Execute):** Once you're sure the list is correct, run `fits_triage.py clean --force` to permanently delete the unwanted FITS files.

## Installation & Usage

**1. Install Dependencies:**

```bash
pip install astropy numpy matplotlib pillow colorama
