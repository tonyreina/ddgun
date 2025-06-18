#!/usr/bin/env python
"""
DDGun setup script - pythonic version
Installs dependencies without shell command calls
"""
import os
import sys
import argparse
import shutil
import tarfile
import subprocess
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError


def install_hhblits(prog_dir):
    """Install hhblits using git and cmake in a pythonic way"""
    utils_dir = Path(prog_dir) / 'utils'
    hh_suite_dir = utils_dir / 'hh-suite'
    build_dir = hh_suite_dir / 'build'
    
    try:
        # Clone the repository if it doesn't exist
        if not hh_suite_dir.exists():
            print("Cloning hh-suite repository...")
            result = subprocess.run([
                'git', 'clone', 'https://github.com/soedinglab/hh-suite.git'
            ], cwd=utils_dir, check=True, capture_output=True, text=True)
        
        # Create build directory
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Run cmake
        print("Running cmake...")
        result = subprocess.run([
            'cmake', '-DCMAKE_INSTALL_PREFIX=..', '..'
        ], cwd=build_dir, check=True, capture_output=True, text=True)
        
        # Build and install
        print("Building and installing...")
        result = subprocess.run([
            'make', '-j', '4'
        ], cwd=build_dir, check=True, capture_output=True, text=True)
        
        result = subprocess.run([
            'make', 'install'
        ], cwd=build_dir, check=True, capture_output=True, text=True)
        
        # Test installation
        hhblits_path = hh_suite_dir / 'bin' / 'hhblits'
        if not hhblits_path.exists():
            raise FileNotFoundError(f"hhblits not found at {hhblits_path}")
        
        # Test if hhblits works
        result = subprocess.run([
            str(hhblits_path), '-h'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise RuntimeError(f"hhblits test failed: {result.stderr}")
            
        print('\b   done!')
        
    except subprocess.CalledProcessError as e:
        print(f'ERROR: hhblits installation failed\n{e.stderr}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'ERROR: hhblits installation failed\n{str(e)}', file=sys.stderr)
        sys.exit(1)


def download_uniclust30(prog_dir):
    """Download uniclust30 database using urllib"""
    data_dir = Path(prog_dir) / 'data'
    www_uc30 = 'https://storage.googleapis.com/alphafold-databases/casp14_versions/uniclust30_2018_08_hhsuite.tar.gz'
    file_uc30 = 'uniclust30_2018_08_hhsuite.tar.gz'
    file_path = data_dir / file_uc30
    
    try:
        # Create data directory if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        if file_path.exists():
            print(f"File {file_uc30} already exists, skipping download")
            print('\b   done!')
            return
        
        print(f"Downloading {file_uc30} from {www_uc30}...")
        
        def progress_hook(block_num, block_size, total_size):
            """Simple progress indicator for download"""
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                sys.stdout.write(f'\rDownload progress: {percent}%')
                sys.stdout.flush()
        
        urlretrieve(www_uc30, str(file_path), reporthook=progress_hook)
        print()  # New line after progress
        
        # Verify file was downloaded
        if not file_path.exists():
            raise FileNotFoundError(f"Download failed: {file_path} not found")
            
        print('\b   done!')
        
    except URLError as e:
        print(f'ERROR: uniclust30_2018_08 download failed\n{str(e)}', file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f'ERROR: uniclust30_2018_08 download failed\n{str(e)}', file=sys.stderr)
        sys.exit(3)


def extract_uniclust30(prog_dir):
    """Extract uniclust30 database using tarfile module"""
    data_dir = Path(prog_dir) / 'data'
    file_uc30 = 'uniclust30_2018_08_hhsuite.tar.gz'
    file_path = data_dir / file_uc30
    extracted_dir = data_dir / 'uniclust30_2018_08'
    
    try:
        # Check if already extracted
        if extracted_dir.exists():
            print(f"Directory {extracted_dir.name} already exists, skipping extraction")
            # Still clean up the archive if it exists
            if file_path.exists():
                file_path.unlink()
                print(f"Removed archive {file_uc30}")
            print('\b   done!')
            return
        
        # Check if archive exists
        if not file_path.exists():
            raise FileNotFoundError(f"Archive {file_path} not found")
        
        print(f"Extracting {file_uc30}...")
        
        # Extract using tarfile module
        with tarfile.open(str(file_path), 'r:gz') as tar:
            # Extract all files to data directory with data filter to avoid deprecation warning
            tar.extractall(path=str(data_dir), filter='data')
        
        # Verify extraction
        if not extracted_dir.exists():
            raise RuntimeError(f"Extraction failed: {extracted_dir} not found")
        
        # Remove the archive file to save space
        file_path.unlink()
        print(f"Removed archive {file_uc30}")
        
        print('\b   done!')
        
    except tarfile.TarError as e:
        print(f'ERROR: untar uniclust30_2018_08 failed\n{str(e)}', file=sys.stderr)
        sys.exit(4)
    except Exception as e:
        print(f'ERROR: untar uniclust30_2018_08 failed\n{str(e)}', file=sys.stderr)
        sys.exit(4)



def main():
    """Main function to install DDGun dependencies"""
    parser = argparse.ArgumentParser(description='Program for the installation of DDGun.')
    parser.add_argument("-d", "--db", action="store_true", dest="db", 
                       help="Install DB only")
    args = parser.parse_args()
    
    prog_dir = os.path.dirname(os.path.abspath(__file__))
    step = 1
    
    try:
        if not args.db:
            print(f'{step}) Install hhblits', file=sys.stderr)        
            install_hhblits(prog_dir)
            step += 1
            
        print(f'{step}) Download uniclust30_2018_08 (25Gb)', file=sys.stderr)
        download_uniclust30(prog_dir)
        step += 1
        
        print(f'{step}) Extract uniclust30_2018_08 (25Gb)', file=sys.stderr)
        extract_uniclust30(prog_dir)
        
        print("Installation completed successfully!")
        
    except KeyboardInterrupt:
        print("\nInstallation interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Installation failed: {e}", file=sys.stderr)
        sys.exit(1)
        


if __name__ == '__main__':
        main()
