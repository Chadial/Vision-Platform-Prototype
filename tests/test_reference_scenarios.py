import unittest

from tests import _path_setup


REFERENCE_SCENARIO_TEST_NAMES = [
    "tests.test_snapshot_service.SnapshotServiceTests.test_save_snapshot_captures_frame_and_writes_to_explicit_path",
    "tests.test_recording_service.RecordingServiceTests.test_start_recording_writes_raw_sequence_until_frame_limit",
    "tests.test_interval_capture_service.IntervalCaptureServiceTests.test_interval_capture_writes_sequence_until_frame_limit",
]


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str | None) -> unittest.TestSuite:
    del tests, pattern
    return loader.loadTestsFromNames(REFERENCE_SCENARIO_TEST_NAMES)


if __name__ == "__main__":
    unittest.main()
