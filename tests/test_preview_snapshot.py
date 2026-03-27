import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.apps.opencv_prototype.preview_snapshot import PreviewSnapshotSaver


class PreviewSnapshotSaverTests(unittest.TestCase):
    def test_save_latest_frame_writes_sequential_snapshot_paths(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = MagicMock(pixel_format="Mono8")
        frame_writer = MagicMock()
        frame_writer.write_frame.side_effect = lambda frame, target_path, create_directories=True: target_path

        with TemporaryDirectory() as temp_dir:
            saver = PreviewSnapshotSaver(
                preview_service,
                save_directory=Path(temp_dir),
                file_stem="preview",
                file_extension=".png",
                frame_writer=frame_writer,
            )

            first_path = saver.save_latest_frame()
            second_path = saver.save_latest_frame()

        self.assertEqual(first_path.name, "preview_000000.png")
        self.assertEqual(second_path.name, "preview_000001.png")

    def test_save_latest_frame_rejects_missing_preview_frame(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = None

        with TemporaryDirectory() as temp_dir:
            saver = PreviewSnapshotSaver(
                preview_service,
                save_directory=Path(temp_dir),
            )

            with self.assertRaisesRegex(RuntimeError, "No preview frame available"):
                saver.save_latest_frame()


if __name__ == "__main__":
    unittest.main()
