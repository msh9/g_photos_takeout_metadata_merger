# Takeout metadata merger

Google Takeout is the only way to pull down original copies of photos in Google Photos in bulk and without manually downloading images in a web broswer.

Unfortunately Google Photos stores photos and photo metadata separately. This means that the takeout archive contains JSON files for image
capture time, location, and other data. That metadata is _not_ stored in the exif section of the downloaded images. Additionally for large libraries the
Takeout process splits data across archives. So it is possible to have a asset 'foo/image.png' in archive1.tgz and its metadata 'foo/image.png.json' in archive2.tgz.

In order to load these images into a digital asset manager like Lightroom or similar tools, we need to move parse the custom takeout format and stored it in the downloaded images.

## Assumptions & Limitations

- we process takeout archives only in the form of gzipped tarballs.
- we assume Google's metadata format is relatively consistent between images and videos
- we can ignore metadata json files if they don't have a matching image or video file in the same directory
- we use the pyexiv2 library to place metadata into files for cross platform compatibility between *nix and Windows. Unfortunately, the underlying exiv library
does not support video files so for those file types and others we write XMP sidecars instead of writing the metadata into the files themselves.

## Goals

- Take standard image and video metadata, like creation time, that Google Photos stores separately and embed that data into the files.
- Perform as much, if not all, processing in memory by streaming the archive contents
- Only extract the base content files and their associated metadata