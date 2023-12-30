import sys
import os
from time import sleep, time
from siyi_sdk import SIYISDK

def manual_absolute_zoom(cam : SIYISDK, target : float):
    # to get current zoom value
    cam.requestZoomHold()
    print("Zoom level: ", cam.getZoomLevel())
    while cam.getZoomLevel() != target:
        total_sleep = 0.005
        if cam.getZoomLevel() > target:
            cam.requestZoomOut()
            sleep(0.01)
            cam.requestZoomHold()
        elif cam.getZoomLevel() < target:
            cam.requestZoomIn()
            sleep(0.01)
            cam.requestZoomHold()
        else:
            cam.requestZoomHold()
            break
        if abs(target - cam.getZoomLevel()) < 0.5:
            total_sleep = 0.05
        sleep(total_sleep)
        cam.requestZoomHold()
        print("Zoom level: ", cam.getZoomLevel())
    cam.requestZoomHold()
    sleep(1)
    print("Zoom level: ", cam.getZoomLevel())
    cam.requestAutoFocus()


def test():
    cam = SIYISDK(server_ip="192.168.144.25", port=37260, debug=False)

    if not cam.connect():
        print("No connection ")
        exit(1)

    sleep(2)
    #print(cam.requestAbsoluteZoom(4.5))
    cam.requestCenterGimbal()
    sleep(2)
    target = 1.5
    manual_absolute_zoom(cam, target)
    #manual_absolute_zoom(cam, target)
    #cam.requestFirmwareVersion()
    #sleep(1)
    #print("Camera Firmware version: ", cam.getFirmwareVersion())

    sleep(3)
    #print("Zoom level: ", cam.getZoomLevel())
    #cam.requestAutoFocus()
    #print("Autofocused")

    cam.disconnect()

if __name__ == "__main__":
    test()