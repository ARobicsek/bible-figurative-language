#!/usr/bin/env python3
"""
Download database from Google Drive during deployment
Uses gdown library for reliable Google Drive downloads
"""
import os
import sys
from pathlib import Path

# Google Drive file ID (extracted from share link)
GOOGLE_DRIVE_FILE_ID = "1TXHpTd4NtQ-NGw8QHwtgQTX0cLjDrvvf"

# Database path
SCRIPT_DIR = Path(__file__).parent
DATABASE_DIR = SCRIPT_DIR.parent / "database"
DATABASE_PATH = DATABASE_DIR / "Biblical_fig_language.db"

def download_from_google_drive(file_id, destination):
    """Download a file from Google Drive using gdown"""
    import gdown

    print(f"Downloading database from Google Drive...")
    print(f"File ID: {file_id}")
    print(f"Destination: {destination}")

    # Create database directory if it doesn't exist
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Construct Google Drive URL
    url = f"https://drive.google.com/uc?id={file_id}"

    # Download with gdown (handles large files automatically)
    gdown.download(url, str(destination), quiet=False)

    print(f"\nDatabase downloaded successfully!")
    print(f"Location: {destination}")
    print(f"Size: {destination.stat().st_size / (1024*1024):.1f} MB")

def main():
    # Check if database already exists
    if DATABASE_PATH.exists():
        size_mb = DATABASE_PATH.stat().st_size / (1024*1024)
        print(f"Database already exists: {DATABASE_PATH} ({size_mb:.1f} MB)")

        # If it's too small (likely a git placeholder or failed download), re-download
        if size_mb < 50:
            print("Database file is too small, downloading fresh copy...")
            DATABASE_PATH.unlink()  # Delete the bad file
            download_from_google_drive(GOOGLE_DRIVE_FILE_ID, DATABASE_PATH)
        else:
            print("Using existing database file")
            return 0
    else:
        print(f"Database not found at {DATABASE_PATH}, downloading...")
        download_from_google_drive(GOOGLE_DRIVE_FILE_ID, DATABASE_PATH)

    return 0

if __name__ == "__main__":
    sys.exit(main())
