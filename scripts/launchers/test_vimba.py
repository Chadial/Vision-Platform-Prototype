from vmbpy import *

with VmbSystem.get_instance() as vmb:
    cams = vmb.get_all_cameras()

    print(f"Found {len(cams)} camera(s):\n")

    for i, cam in enumerate(cams, start=1):
        with cam:
            print(f"Camera {i}")
            print(f"  ID: {cam.get_id()}")
            print(f"  Name: {cam.get_name()}")
            print(f"  Model: {cam.get_model()}")
            print(f"  Serial: {cam.get_serial()}")
            print(f"  Interface ID: {cam.get_interface_id()}")
            print()