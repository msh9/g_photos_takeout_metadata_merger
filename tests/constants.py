from pathlib import PurePath, Path

resource_directory = 'resources'
tarone_resource_directory = 'resources/tarone'
tartwo_resource_directory = 'resources/tartwo'
image_metadata_filename = 'example-img.png.json'

def get_path_resource_folder_added(filepath: str) -> PurePath:
    return Path(filepath).parent.absolute().joinpath(resource_directory)