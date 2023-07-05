import argparse
import logging
from pathlib import PurePath, Path
from exifio.metadata import TakeoutMetadata
from exifio.archive import Archive, MetadataNotFound
from exifio.content import GenericXMPExifContent, XMPSidecar

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

def setup_arguments():
    parser = argparse.ArgumentParser(description='Process Google Takeout archives.')
    parser.add_argument('tarfiles', type=str, nargs='+', help='Path to tarfile(s)')
    parser.add_argument('output_directory', type=str, help='Path to the output directory')
    return parser

def run_extraction(args):
    # Create the output directory if it doesn't exist
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)
    logging.warning(args)
    with Archive(*args.tarfiles) as archive:
        archives_entries = iter(archive)
        while True:
            try:
                content_metadata = next(archives_entries)
            except MetadataNotFound as e:
                logging.error(f'Metadata not found for {e.content_name}')
                continue
            except StopIteration:
                break
            logging.debug(f'Reading from archives with names {content_metadata}')
            content_reader, metadata_reader = archive.extract_files(content_metadata)

            # Create a TakeoutMetadata instance
            takeout_metadata = TakeoutMetadata(metadata_reader.read().decode('utf-8'))
            content_file_extension = PurePath(content_metadata.content_file.name).suffix.lower()
            content_file_path = Path(args.output_directory).joinpath(content_metadata.content_file.name)

            logging.info(f"Reading {content_metadata.content_file.name} and writing to {content_file_path}")

            content_bytes = content_reader.read()
            if content_file_extension == '.jpg' or content_file_extension == '.png':
                content = GenericXMPExifContent(content_bytes, takeout_metadata)
            else:
                logging.info(f"Writing sidecar for {content_file_path}")
                content = XMPSidecar(content_bytes, takeout_metadata)

            # Check for name conflicts
            if content_file_path.exists():
                logging.warning(f"File {content_file_path} already exists, skipping.")
                continue

            content.process_content_metadata(content_file_path)
            logging.info(f"Finished {content_metadata.content_file.name}")
def main():
    arg_parser = setup_arguments()
    program_arguments = arg_parser.parse_args()
    logging.info(f"Running with {program_arguments}")
    run_extraction(program_arguments)

if __name__ == "__main__":
    main() 