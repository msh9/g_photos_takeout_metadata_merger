import unittest
import constants
import datetime
from photo_metadata_merger.exifio import metadata

class TestMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.photo_fixture = constants.get_image_metadata()
        cls.video_fixture = constants.get_video_metadata()

    def test_get_creation_time(self):
        photo_metadata = metadata.TakeoutMetadata(TestMetadata.photo_fixture)
        correct_creation_time = datetime.datetime.fromtimestamp(1621897037, datetime.timezone.utc)
        self.assertEqual(correct_creation_time, photo_metadata.get_creation_time())

    def test_get_photo_taken_time(self):
        photo_metadata = metadata.TakeoutMetadata(TestMetadata.photo_fixture)
        correct_taken_time = datetime.datetime.fromtimestamp(1229616017, datetime.timezone.utc)
        self.assertEqual(correct_taken_time, photo_metadata.get_photo_taken_time())

    def test_get_title(self):
        photo_metadata = metadata.TakeoutMetadata(TestMetadata.photo_fixture)
        self.assertEqual('old-bike.jpg', photo_metadata.get_title())

    def test_get_gphotos_location_is_a_location(self):
        video_metadata = metadata.TakeoutMetadata(TestMetadata.video_fixture)
        self.assertIsInstance(video_metadata.get_gphotos_location(), metadata.Location)
    
    def test_get_exif_location_is_a_location(self):
        video_metadata = metadata.TakeoutMetadata(TestMetadata.video_fixture)
        self.assertIsInstance(video_metadata.get_exif_location(), metadata.Location)

    def test_get_exif_location(self):
        video_metadata = metadata.TakeoutMetadata(TestMetadata.video_fixture)
        location = video_metadata.get_gphotos_location()
        self.assertEqual(40.558699999999995, location.latitude)
        self.assertEqual(-111.6563, location.longitude)

    def test_get_exif_location(self):
        video_metadata = metadata.TakeoutMetadata(TestMetadata.video_fixture)
        exif_location = video_metadata.get_exif_location()
        self.assertEqual(40.558699999999995, exif_location.latitude)
        self.assertEqual(-111.6564, exif_location.longitude)

class TestLocation(unittest.TestCase):

    def test_is_latitude_north(self):
        north_location = metadata.Location(20.5, 21.5)
        self.assertTrue(north_location.is_latitude_north())

        south_location = metadata.Location(-20.5, 21.5)
        self.assertFalse(south_location.is_latitude_north())

    def test_is_longitude_west(self):
        west_location = metadata.Location(20.5, -110.5)
        self.assertTrue(west_location.is_longitude_west())

        east_location = metadata.Location(20.5, 111.4)
        self.assertFalse(east_location.is_longitude_west())

    def test_get_latitude_as_deg_minutes_seconds(self):
        degrees, minutes, seconds = metadata.Location(20.75, 110.75).get_latitude_as_deg_minutes_seconds()

        self.assertEqual(degrees, 20)
        self.assertEqual(minutes, 45)
        self.assertEqual(seconds, 0)

    def test_get_longitude_as_deg_minutes_seconds(self):
        degrees, minutes, seconds = metadata.Location(20.75, -110.75).get_longitude_as_deg_minutes_seconds()

        self.assertEqual(degrees, 110)
        self.assertEqual(minutes, 45)
        self.assertEqual(seconds, 0)

if __name__ == '__main__':
    unittest.main()