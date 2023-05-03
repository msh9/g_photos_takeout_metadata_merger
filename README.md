# Takeout metadata merger

Google Takeout is the only way to pull down original copies of photos in Google Photos in bulk and without manually downloading images in a web broswer.

Unfortunately Google Photos stores photos and photo metadata separately. This means that the takeout archive contains JSON files for image
capture time, location, and other data. That metadata is _not_ stored in the exif section of the downloaded images. In order to load this images into a
digital asset manager like Lightroom or similar tools, we need to move parse the custom takeout format and stored it in the downloaded images.