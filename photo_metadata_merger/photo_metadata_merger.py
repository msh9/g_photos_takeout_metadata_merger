import argparse
import logging
from pathlib import PurePath, Path
from exifio.metadata import TakeoutMetadata
from exifio.archive import Archive, MetadataNotFound
from exifio.content import GenericXMPExifContent, XMPSidecar
from storage import Persisted as PersistedStorage

# Initialize logging
logging.basicConfig(level=logging.INFO)
persist_seen_files_every = 20


def setup_arguments():
    parser = argparse.ArgumentParser(description="Process Google Takeout archives.")
    parser.add_argument("tarfiles", type=str, nargs="+", help="Path to tarfile(s)")
    parser.add_argument(
        "duplicate_tracking",
        type=str,
        help="Path to an existing gzipped JSON file with seen file hashes created by this application",
    )
    parser.add_argument(
        "output_directory", type=str, help="Path to the output directory"
    )
    return parser


def create_and_ensure_destination_path(
    root: Path, takeout_metadata: TakeoutMetadata, content_archive_path: Path
) -> Path:
    photo_taken = takeout_metadata.get_photo_taken_time()
    content_destination = root.joinpath(
        str(photo_taken.year), str(photo_taken.month), content_archive_path.name
    )
    content_destination.parent.mkdir(parents=True, exist_ok=True)
    return content_destination


def run_extraction(args):
    logging.warning(args)

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)
    seen_content = PersistedStorage(Path(args.duplicate_tracking))
    files_processed_counter = 0
    with Archive(*args.tarfiles) as archive:
        archives_entries = iter(archive)
        while True:
            try:
                content_metadata = next(archives_entries)
            except MetadataNotFound as e:
                logging.error(f"Metadata not found for {e.content_name}")
                continue
            except StopIteration:
                break
            logging.debug(f"Reading from archives with names {content_metadata}")
            content_reader, metadata_reader = archive.extract_files(content_metadata)
            content_bytes = content_reader.read()
            if seen_content.seen_content_bytes(content_bytes):
                logging.info(f"Already processed {content_metadata} based on hash")
                continue

            takeout_metadata = TakeoutMetadata(metadata_reader.read().decode("utf-8"))
            content_name_as_path = PurePath(content_metadata.content_file.name)
            content_file_path = create_and_ensure_destination_path(
                Path(args.output_directory), takeout_metadata, content_name_as_path
            )

            logging.info(
                f"Reading {content_metadata.content_file.name} and writing to {content_file_path}"
            )

            content_file_extension = content_name_as_path.suffix.lower()
            if content_file_extension == ".jpg" or content_file_extension == ".png":
                content = GenericXMPExifContent(content_bytes, takeout_metadata)
            else:
                logging.info(f"Writing sidecar for {content_file_path}")
                content = XMPSidecar(content_bytes, takeout_metadata)

            # Check for name conflicts
            if content_file_path.exists():
                logging.warning(f"File {content_file_path} already exists, skipping.")
                continue

            content.process_content_metadata(content_file_path)
            seen_content.add_content_bytes(content_bytes, content_file_path)
            files_processed_counter += 1
            if files_processed_counter % persist_seen_files_every == 0:
                logging.info(
                    f"Processed {files_processed_counter} files, saving seen contents files storage to {args.duplicate_tracking}"
                )
                seen_content.save()

            logging.info(f"Finished {content_metadata.content_file.name}")

    seen_content.save()


def main():
    arg_parser = setup_arguments()
    program_arguments = arg_parser.parse_args()
    logging.info(f"Running with {program_arguments}")
    run_extraction(program_arguments)


if __name__ == "__main__":
    main()
