"""
@file test_record_video.py
@Description: This is a test script for using the ZR10 SDK Python implementation to record video
@Author: Mohamed Abdelkader
@Contact: mohamedashraf123@gmail.com
All rights reserved 2022
"""

from zr10_python import ZR10SDK

def test():
    cam = ZR10SDK(server_ip="192.168.144.25", port=37260)

    val = cam.toggleRecording()
    # if val is not None:
    #     hdr_state, record_state, motion_mode, mount_dir = val[0], val[1], val[2], val[3]

    print("Record video feedback: ", val)

if __name__ == "__main__":
    test()