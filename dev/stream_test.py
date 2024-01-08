from time import sleep
from siyi_sdk import SIYISDK, SIYISTREAM

def test():
    cam = SIYISDK(server_ip="192.168.144.25", port=37260, debug=False)
    stream = SIYISTREAM()

    if not cam.connect():
        print("No connection ")
        exit(1)

    # if not stream.connect():
    #     print("No stream connection")
    #     exit(1)

    sleep(2)
    cam.requestLockMode()
    cam.requestCenterGimbal()
    cam.setAbsoluteZoom(4)
    sleep(2)
    print("Requesting autofocus in 3 seconds")
    sleep(3)
    cam.requestAutoFocus()
    sleep(1)
    stream.test_continuous()

    cam.disconnect()

if __name__ == "__main__":
    test()