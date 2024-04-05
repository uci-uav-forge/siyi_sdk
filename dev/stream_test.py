from time import sleep
from siyi_sdk import SIYISDK, SIYISTREAM
import cv2

def test():
    cam = SIYISDK(server_ip="192.168.144.25", port=37260, debug=False)
    stream = SIYISTREAM()

    if not cam.connect():
        print("No connection ")
        exit(1)

    if not stream.connect():
        print("No stream connection")
        exit(1)

    sleep(2)
    cam.requestLockMode()
    cam.requestCenterGimbal()
    cam.setAbsoluteZoom(4)
    sleep(2)
    print("Requesting autofocus in 1 second")
    sleep(1)
    cam.requestAutoFocus()
    sleep(1)
    while 1:
        frame = stream.get_frame()
        cv2.putText(frame, "Resolution: {}".format(frame.shape), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.disconnect()

if __name__ == "__main__":
    test()