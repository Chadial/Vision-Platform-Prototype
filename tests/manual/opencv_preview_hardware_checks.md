# OpenCV Preview Hardware Checks

## Purpose

This file captures manual hardware-backed checks for the OpenCV preview path that are not covered well by automated tests.

Keep entries short, concrete, and dated so later sessions can distinguish verified operator behavior from assumptions.

## 2026-03-28

### Environment

- branch: `feature/opencv-ui-operator-block`
- camera: auto-selected attached hardware
- lighting note: low-light setup; preview validation used a higher exposure time

### Commands Used

```powershell
Set-Location C:\Users\Schulz\PycharmProjects\VisionPlatformPrototype
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m vision_platform.apps.opencv_prototype.hardware_preview_demo --exposure-time-us 1000000
```

```powershell
Set-Location C:\Users\Schulz\PycharmProjects\VisionPlatformPrototype
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m vision_platform.apps.opencv_prototype.hardware_preview_demo --exposure-time-us 1000000 --snapshot-save-directory .\captures\preview_shortcuts
```

### Manually Confirmed

- preview window opened successfully on real hardware
- `c` copied point coordinates and paste verification succeeded
- `x` toggled the crosshair
- `r` entered rectangle ROI mode and rectangle ROI creation worked
- `e` entered ellipse ROI mode and ellipse ROI creation worked
- ROI live preview during creation worked
- `q` exited the preview
- `Esc` exited the preview
- closing the window through the title-bar close button exited the preview
- cursor-anchored zoom behaved as intended after the latest viewport update
- the thin outline around the visible image area helped distinguish true image content from padded black regions
- `+` saved preview snapshots successfully when `--snapshot-save-directory` was configured
- mouse-wheel zoom worked on real hardware
- middle-drag pan worked on real hardware after zooming in
- the `view=x,y` status readout made pan movement visible even when the scene itself was too dark for easy visual confirmation

### Notes

- without `--snapshot-save-directory`, the preview correctly reported `Snapshot shortcut unavailable`
- the high exposure setting was needed only because the available light source was weak during the manual check
- wheel-based cursor zoom is acceptable for the current MVP, but at very small zoom factors the anchored image point can still drift slightly because of integer viewport rounding
