

import os
import glob
import argparse
import sys
from colorama import init, Fore, Style

# Initialize colorama to work on all platforms
init(autoreset=True)

try:
    from astropy.io import fits
    from astropy.visualization import AsinhStretch, ImageNormalize
    import numpy as np
    import matplotlib.pyplot as plt
    # Pillow is used by matplotlib for JPG output
    from PIL import Image
except ImportError:
    print(Fore.RED + "Error: Missing required libraries. Please run:")
    print(Style.BRIGHT + "pip install astropy numpy matplotlib pillow colorama")
    sys.exit(1)


def generate_previews(directory):
    """Finds FITS files and generates stretched JPEG previews."""
    output_dir = os.path.join(directory, 'previews')
    
    if not os.path.isdir(directory):
        print(Fore.RED + f"Error: Directory not found at '{directory}'")
        sys.exit(1)
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(Fore.GREEN + f"Created preview directory: {output_dir}")

    fits_files = glob.glob(os.path.join(directory, '*.fit*'))
    if not fits_files:
        print(Fore.YELLOW + f"No FITS files found in '{directory}'. Nothing to do.")
        return

    print(Fore.GREEN + f"Found {len(fits_files)} FITS files. Generating previews...")
    
    for f_path in fits_files:
        base_name = os.path.basename(f_path)
        try:
            with fits.open(f_path) as hdul:
                data = hdul[0].data.astype(np.float32)
            
            stretch = AsinhStretch()
            norm = ImageNormalize(data, vmin=np.percentile(data, 5), vmax=np.percentile(data, 99.5), stretch=stretch)
            stretched_data = norm(data)
            
            preview_name = os.path.splitext(base_name)[0] + '.jpg'
            output_path = os.path.join(output_dir, preview_name)
            
            plt.imsave(output_path, stretched_data, cmap='gray', origin='lower')
            print(Fore.GREEN + f"  -> Saved preview for {base_name}")
            
        except Exception as e:
            print(Fore.RED + f"Could not process {base_name}: {e}")

    print(Style.BRIGHT + Fore.GREEN + "\nPreview generation complete!")


def clean_fits(directory, force):
    """Deletes FITS files that are missing a corresponding preview."""
    preview_dir = os.path.join(directory, 'previews')

    if not os.path.isdir(directory) or not os.path.isdir(preview_dir):
        print(Fore.RED + f"Error: Ensure both '{directory}' and its 'previews' subfolder exist.")
        sys.exit(1)

    preview_basenames = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(preview_dir, '*.jpg'))}

    if not preview_basenames:
        print(Fore.YELLOW + "Warning: No preview files found. No FITS files will be deleted.")
        return

    fits_files_to_check = glob.glob(os.path.join(directory, '*.fit*'))
    files_to_delete = []

    for fits_path in fits_files_to_check:
        fits_basename = os.path.splitext(os.path.basename(fits_path))[0]
        if fits_basename not in preview_basenames:
            files_to_delete.append(fits_path)

    print(Fore.GREEN + f"Found {len(preview_basenames)} remaining previews. Checking {len(fits_files_to_check)} FITS files.")
    
    if not files_to_delete:
        print(Fore.GREEN + "All FITS files have a matching preview. Nothing to clean.")
        return

    if force:
        print(Fore.RED + Style.BRIGHT + f"\n--- DELETING {len(files_to_delete)} FITS FILES ---")
        for f in files_to_delete:
            try:
                os.remove(f)
                print(Fore.RED + f"  -> DELETED: {os.path.basename(f)}")
            except OSError as e:
                print(Fore.RED + f"  -> ERROR: Could not delete {os.path.basename(f)}: {e}")
        print(Style.BRIGHT + Fore.GREEN + "\nCleanup complete.")
    else:
        print(Fore.YELLOW + Style.BRIGHT + "\n--- DRY RUN MODE ---")
        print(Fore.YELLOW + "No files will be deleted. The following files are marked for removal:")
        for f in files_to_delete:
            print(Fore.YELLOW + f"  -> {os.path.basename(f)}")
        print(Style.BRIGHT + Fore.GREEN + "\nTo delete these files, run this command again with the --force flag.")


def main():
    """Main function to parse arguments and run commands."""
    parser = argparse.ArgumentParser(
        description=Fore.GREEN + "A traditional CLI tool to triage FITS files.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30)
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # Generate command
    parser_gen = subparsers.add_parser('generate', help='Generate JPEG previews for all FITS files in a directory.')
    parser_gen.add_argument('directory', type=str, help='The directory containing your FITS files.')

    # Clean command
    parser_clean = subparsers.add_parser('clean', help='Delete FITS files that are missing a preview.')
    parser_clean.add_argument('directory', type=str, help='The directory containing your FITS files.')
    parser_clean.add_argument('--force', action='store_true', help='Disable dry run and permanently delete files.')

    args = parser.parse_args()

    if args.command == 'generate':
        generate_previews(args.directory)
    elif args.command == 'clean':
        clean_fits(args.directory, args.force)

if __name__ == '__main__':
    main()