import argparse
import json
import logging
import os
import tarfile
from pathlib import PurePath, Path
from PIL import Image
import piexif

from exifio.archive import Archive, ArchivePair, MetadataNotFound
from exifio.metadata import TakeoutMetadata

logging.basicConfig(filename='error.log', level=logging.ERROR)

def process_takeout_files(tarfile_paths, output_dir):
    with Archive(*tarfile_paths) as archive:
        for name_as_path, metadata_path in archive:
            try:
                pair = ArchivePair(name_as_path, metadata_path)
                process_file(pair, archive, output_dir)
            except MetadataNotFound as e:
                logging.error(f"Metadata not found for {e.content_name}")
                print(f"Metadata not found for {e.content_name}")

def process_file(pair: ArchivePair, archive: Archive, output_dir: str):
    # Get metadata from json
    metadata_file = archive.extractfile(pair.metadata_name)
    metadata = TakeoutMetadata(metadata_file.read())
    
    # Get image file and load with Pillow
    img_file = archive.extractfile(pair.data_name)
    img = Image.open(img_file)

    # Update metadata
    exif_dict = piexif.load(img.info['exif'])
    exif_dict['0th'][piexif.ImageIFD.DateTime] = metadata.get_photo_taken_time().strftime("%Y:%m:%d %H:%M:%S")
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = metadata.get_exif_location().latitude
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = metadata.get_exif_location().longitude
    exif_bytes = piexif.dump(exif_dict)
    img.save(output_dir / pair.data_name, exif=exif_bytes)

def main():
    parser = argparse.ArgumentParser(description='Process Google Takeout files.')
    parser.add_argument('tarfiles', metavar='N', type=str, nargs='+', help='input tar files')
    parser.add_argument('output_dir', type=str, help='output directory for processed files')

    args = parser.parse_args()

    process_takeout_files(args.tarfiles, args.output_dir)

if __name__ == '__main__':
    main()
