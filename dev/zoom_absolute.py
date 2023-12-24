import sys
import os
from time import sleep
from siyi_sdk_src import SIYISDK

def test():
    cam = SIYISDK(server_ip="192.168.144.25", port=37260, debug=True)

    if not cam.connect():
        print("No connection ")
        exit(1)

    sleep(2)
    cam.setAbsoluteZoom(4.5)
    #cam.requestFirmwareVersion()
    #sleep(1)
    #print("Camera Firmware version: ", cam.getFirmwareVersion())

    sleep(3)
    print("Zoom level: ", cam.getZoomLevel())
    cam.requestAutoFocus()
    print("Autofocused")

    cam.disconnect()

if __name__ == "__main__":
    test()