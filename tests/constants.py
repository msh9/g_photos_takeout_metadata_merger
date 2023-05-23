from pathlib import PurePath, Path

resource_directory = 'resources'
tarone_resource_directory = resource_directory + '/tarone'
tartwo_resource_directory = resource_directory + '/tartwo'
image_metadata_filename = tarone_resource_directory + '/example-img.png.json'
video_metadata_filename = tartwo_resource_directory + '/example-video.mp4.json'
image_filename = tarone_resource_directory + '/example-img.png'

def get_tests_folder() -> PurePath:
    return Path(__file__).parent.absolute()

def get_image_metadata() -> str:
    with open(get_tests_folder().joinpath(image_metadata_filename), 'r') as metadata:
        lines = metadata.read()
    return lines

def get_video_metadata() -> str:
    with open(get_tests_folder().joinpath(video_metadata_filename), 'r') as metadata:
        lines = metadata.read()
    return lines

def get_exif_fixture_path() -> PurePath:
    return get_tests_folder().joinpath(resource_directory).joinpath('exif-fixture.jpg')