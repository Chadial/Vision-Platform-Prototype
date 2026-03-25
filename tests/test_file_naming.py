from pathlib import Path
import unittest

from tests import _path_setup
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.storage.file_naming import build_snapshot_path


class FileNamingTests(unittest.TestCase):
    def test_build_snapshot_path_appends_extension(self) -> None:
        request = SnapshotRequest(save_directory=Path("captures"), file_stem="image_001", file_extension="png")
        self.assertEqual(build_snapshot_path(request), Path("captures/image_001.png"))


if __name__ == "__main__":
    unittest.main()
