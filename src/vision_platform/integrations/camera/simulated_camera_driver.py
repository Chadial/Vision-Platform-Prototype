from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional, Sequence

from vision_platform.integrations.camera.camera_driver import CameraDriver
from vision_platform.models import CameraConfiguration, CameraStatus, CapturedFrame


@dataclass(frozen=True, slots=True)
class _SimulatedImage:
    width: int
    height: int
    pixel_format: str
    buffer: bytes
    source_name: str


class SimulatedCameraDriver(CameraDriver):
    """CameraDriver implementation for hardware-free development and demos."""

    def __init__(
        self,
        camera_id: str = "simulated-camera",
        camera_name: str = "Simulated Camera",
        width: int = 640,
        height: int = 480,
        pixel_format: str = "Mono8",
        sample_image_paths: Sequence[Path] | None = None,
        loop_samples: bool = True,
    ) -> None:
        self._camera_id = camera_id
        self._camera_name = camera_name
        self._default_width = width
        self._default_height = height
        self._default_pixel_format = pixel_format
        self._loop_samples = loop_samples
        self._status = CameraStatus()
        self._latest_frame: Optional[CapturedFrame] = None
        self._frame_counter = 0
        self._configuration = CameraConfiguration(pixel_format=pixel_format)
        self._sample_images = self._load_sample_images(sample_image_paths or [])
        self._sample_index = 0
        self._lock = Lock()

    def initialize(self, camera_id: Optional[str] = None) -> CameraStatus:
        with self._lock:
            if camera_id is not None:
                self._camera_id = camera_id

            self._status = CameraStatus(
                is_initialized=True,
                is_acquiring=False,
                source_kind="simulation",
                driver_name=self.__class__.__name__,
                camera_id=self._camera_id,
                camera_name=self._camera_name,
                camera_model="Simulated",
                camera_serial="SIM-0001",
                interface_id="SIM",
            )
            self._latest_frame = None
            self._frame_counter = 0
            self._sample_index = 0
            return self._status

    def shutdown(self) -> None:
        with self._lock:
            self._latest_frame = None
            self._status = CameraStatus()
            self._frame_counter = 0
            self._sample_index = 0

    def get_status(self) -> CameraStatus:
        with self._lock:
            return CameraStatus(
                is_initialized=self._status.is_initialized,
                is_acquiring=self._status.is_acquiring,
                source_kind=self._status.source_kind,
                driver_name=self._status.driver_name,
                camera_id=self._status.camera_id,
                camera_name=self._status.camera_name,
                camera_model=self._status.camera_model,
                camera_serial=self._status.camera_serial,
                interface_id=self._status.interface_id,
                reported_acquisition_frame_rate=self._status.reported_acquisition_frame_rate,
                acquisition_frame_rate_enabled=self._status.acquisition_frame_rate_enabled,
                last_error=self._status.last_error,
            )

    def apply_configuration(self, config: CameraConfiguration) -> None:
        self._require_initialized()
        self._configuration = CameraConfiguration(
            exposure_time_us=config.exposure_time_us,
            gain=config.gain,
            pixel_format=config.pixel_format or self._configuration.pixel_format or self._default_pixel_format,
            acquisition_frame_rate=config.acquisition_frame_rate,
            roi_offset_x=config.roi_offset_x,
            roi_offset_y=config.roi_offset_y,
            roi_width=config.roi_width,
            roi_height=config.roi_height,
        )

    def start_acquisition(self) -> None:
        self._require_initialized()
        self._status.is_acquiring = True

    def stop_acquisition(self) -> None:
        self._status.is_acquiring = False

    def capture_snapshot(self) -> CapturedFrame:
        self._require_initialized()
        frame = self._create_next_frame()
        self._latest_frame = frame
        return frame

    def get_latest_frame(self) -> Optional[CapturedFrame]:
        self._require_initialized()

        if not self._status.is_acquiring:
            return self._latest_frame

        frame = self._create_next_frame()
        self._latest_frame = frame
        return frame

    def _create_next_frame(self) -> CapturedFrame:
        if self._sample_images:
            sample = self._next_sample_image()
            width = sample.width
            height = sample.height
            pixel_format = sample.pixel_format
            buffer = sample.buffer
        else:
            width = self._default_width
            height = self._default_height
            pixel_format = self._configuration.pixel_format or self._default_pixel_format
            buffer = self._generate_frame_buffer(width, height, pixel_format, self._frame_counter)

        frame = CapturedFrame(
            raw_frame=buffer,
            width=width,
            height=height,
            frame_id=self._frame_counter,
            camera_timestamp=self._frame_counter,
            pixel_format=pixel_format,
            timestamp_utc=datetime.now(timezone.utc),
        )
        self._frame_counter += 1
        return frame

    def _next_sample_image(self) -> _SimulatedImage:
        if not self._sample_images:
            raise RuntimeError("No sample images are configured.")

        if self._sample_index >= len(self._sample_images):
            if not self._loop_samples:
                self._sample_index = len(self._sample_images) - 1
            else:
                self._sample_index = 0

        image = self._sample_images[self._sample_index]
        if self._sample_index < len(self._sample_images) - 1:
            self._sample_index += 1
        elif self._loop_samples:
            self._sample_index = 0
        return image

    def _require_initialized(self) -> None:
        if not self._status.is_initialized:
            raise RuntimeError("Camera driver is not initialized.")

    @staticmethod
    def _generate_frame_buffer(width: int, height: int, pixel_format: str, frame_id: int) -> bytes:
        normalized_format = pixel_format.lower()
        if normalized_format == "mono8":
            return bytes(((x + y + frame_id) % 256) for y in range(height) for x in range(width))
        if normalized_format == "mono16":
            return b"".join(
                (((x * 257) + (y * 257) + frame_id) % 65536).to_bytes(2, byteorder="little")
                for y in range(height)
                for x in range(width)
            )
        if normalized_format == "rgb8":
            return bytes(
                component
                for y in range(height)
                for x in range(width)
                for component in ((x + frame_id) % 256, (y + frame_id) % 256, (x + y + frame_id) % 256)
            )
        if normalized_format == "bgr8":
            return bytes(
                component
                for y in range(height)
                for x in range(width)
                for component in ((x + y + frame_id) % 256, (y + frame_id) % 256, (x + frame_id) % 256)
            )
        raise RuntimeError(f"Unsupported simulated pixel format '{pixel_format}'.")

    @classmethod
    def _load_sample_images(cls, sample_image_paths: Sequence[Path]) -> list[_SimulatedImage]:
        images: list[_SimulatedImage] = []
        for sample_path in sample_image_paths:
            if sample_path.suffix.lower() == ".pgm":
                images.append(cls._parse_pnm(sample_path, expected_magic=b"P5", pixel_format="Mono8"))
            elif sample_path.suffix.lower() == ".ppm":
                images.append(cls._parse_pnm(sample_path, expected_magic=b"P6", pixel_format="Rgb8"))
            else:
                raise RuntimeError(
                    f"Unsupported simulated sample image '{sample_path.name}'. Use .pgm or .ppm sample files."
                )
        return images

    @staticmethod
    def _parse_pnm(path: Path, expected_magic: bytes, pixel_format: str) -> _SimulatedImage:
        data = path.read_bytes()
        offset = 0

        def read_token() -> bytes:
            nonlocal offset
            while offset < len(data) and chr(data[offset]).isspace():
                offset += 1
            if offset < len(data) and data[offset] == ord("#"):
                while offset < len(data) and data[offset] not in (ord("\n"), ord("\r")):
                    offset += 1
                return read_token()

            start = offset
            while offset < len(data) and not chr(data[offset]).isspace():
                offset += 1
            return data[start:offset]

        magic = read_token()
        if magic != expected_magic:
            raise RuntimeError(f"Unsupported sample image format in '{path.name}'.")

        width = int(read_token())
        height = int(read_token())
        max_value = int(read_token())
        if max_value != 255:
            raise RuntimeError(f"Sample image '{path.name}' must use max value 255.")

        while offset < len(data) and chr(data[offset]).isspace():
            offset += 1

        buffer = data[offset:]
        expected_size = width * height * (1 if pixel_format == "Mono8" else 3)
        if len(buffer) != expected_size:
            raise RuntimeError(
                f"Sample image '{path.name}' has unexpected payload size {len(buffer)}; expected {expected_size}."
            )

        return _SimulatedImage(
            width=width,
            height=height,
            pixel_format=pixel_format,
            buffer=buffer,
            source_name=path.name,
        )


__all__ = ["SimulatedCameraDriver"]
