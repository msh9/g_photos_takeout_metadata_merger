import os
import io
import json
import tarfile
import piexif
from PIL import Image
from dateutil.parser import parse
from pathlib import Path

def process_takeout_archive(archive_path, output_folder):
    with tarfile.open(archive_path, 'r:gz') as tar_ref:
        for tar_info in tar_ref:
            if tar_info.isfile():
                with tar_ref.extractfile(tar_info) as file_obj:
                    process_file(file_obj, tar_info.name, output_folder)

def process_file(file_obj, file_name, output_folder):
    if file_name.endswith('.json'):
        json_data = json.load(file_obj)
        if 'photoTakenTime' in json_data:
            photo_taken_time = json_data['photoTakenTime']['formatted']
            image_file_name = os.path.splitext(file_name)[0]
            process_image_file(image_file_name, photo_taken_time, output_folder)

def process_image_file(image_file_name, photo_taken_time, output_folder):
    date = parse(photo_taken_time).date()
    dest_folder = os.path.join(output_folder, str(date))
    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    dest_file_path = os.path.join(dest_folder, os.path.basename(image_file_name))

    with open(dest_file_path, 'wb') as dest_file:
        shutil.copyfileobj(file_obj, dest_file)

    update_exif_metadata(dest_file_path, photo_taken_time)

def update_exif_metadata(image_file_path, photo_taken_time):
    image = Image.open(image_file_path)
    exif_dict = piexif.load(image.info['exif'])

    exif_datetime = photo_taken_time.replace(':', '').replace(' ', ':')[:19]
    exif_bytes = exif_datetime.encode('utf-8')

    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_bytes
    exif_dict['Exif'][piexif.ExifIFD.DateTime] = exif_bytes

    exif_bytes = piexif.dump(exif_dict)
    image.save(image_file_path, exif=exif_bytes)

def main():
    archive_path = 'path/to/your/takeout/archive.tgz'
    output_folder = 'path/to/output/folder'

    process_takeout_archive(archive_path, output_folder)

if __name__ == '__main__':
    main()
