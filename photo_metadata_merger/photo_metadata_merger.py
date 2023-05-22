import argparse
import logging
import os
from pathlib import Path
from photo_metadata_merger.exifio.metadata import TakeoutMetadata
from photo_metadata_merger.exifio.archive import Archive, ArchivePair, MetadataNotFound
from photo_metadata_merger.exifio.content import JpgContent, Content

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR)

# Command line arguments parser
parser = argparse.ArgumentParser(description='Process Google Takeout archives.')
parser.add_argument('tarfiles', type=str, nargs='+', help='Path to tarfile(s)')
parser.add_argument('output_directory', type=str, help='Path to the output directory')

args = parser.parse_args()

# Create the output directory if it doesn't exist
Path(args.output_directory).mkdir(parents=True, exist_ok=True)

for tarfile in args.tarfiles:
    try:
        with Archive(tarfile) as archive:
            for content_metadata in archive:
                content_bytes, metadata_bytes = archive.extract_files(content_metadata)

                # Create a TakeoutMetadata instance
                takeout_metadata = TakeoutMetadata(metadata_bytes.read().decode('utf-8'))

                # Check for file type and handle accordingly
                if content_metadata.content_file.name.lower().endswith('.jpg'):
                    content = JpgContent(content_bytes, takeout_metadata)
                    content_file_path = Path(args.output_directory) / content_metadata.content_file.name

                    # Check for name conflicts
                    if content_file_path.exists():
                        logging.warning(f"File {content_file_path} already exists, skipping.")
                        continue

                    content.process_content_metadata(content_file_path)
                else:
                    # Add other file types here
                    pass

    except MetadataNotFound as e:
        print(f'Metadata not found for {e.content_name}')
        logging.error(f'Metadata not found for {e.content_name}')
