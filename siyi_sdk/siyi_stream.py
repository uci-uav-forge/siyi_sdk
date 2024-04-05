import av # pip install av --no-binary av (https://stackoverflow.com/a/74265080)
import cv2
import numpy as np
import time
import logging
import threading

# Default stream: rtsp://192.168.144.25:8554/main.264

# Does not work on my mac but maybe on Jetson?
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Untested but could work if we build opencv with gstreamer:
# This will automatically grab latest frame
#cv2.VideoCapture("rtspsrc location=rtsp://... ! decodebin ! videoconvert ! video/x-raw,framerate=30/1 ! appsink drop=true sync=false", cv2.CAP_GSTREAMER)

class SIYISTREAM:

    def __init__(self, server_ip : str = "192.168.144.25", port : int = 8554, name : str = "main.264", debug : bool = False):
        """
        
        Params
        --
        - server_ip [str] IP address of the camera
        - port: [int] UDP port of the camera
        - name: [str] name of the stream
        """
        self._debug= debug # print debug messages
        if self._debug:
            d_level = logging.DEBUG
        else:
            d_level = logging.INFO
        LOG_FORMAT=' [%(levelname)s] %(asctime)s [SIYISDK::%(funcName)s] :\t%(message)s'
        logging.basicConfig(format=LOG_FORMAT, level=d_level)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info("Initializing SIYISTREAM")
        self._server_ip = server_ip
        self._port = port
        self._name = name
        self._stream_link = "rtsp://"+self._server_ip+":"+str(self._port)+"/"+self._name
        self._logger.info("Stream link: {}".format(self._stream_link))
        self._stream = None

    def connect(self):
        """
        Connect to the camera
        """
        if self._stream is not None:
            self._logger.warning("Already connected to camera")
            return
        self._stream = av.open("rtsp://192.168.144.25:8554/main.264", format="rtsp").demux()
  
        self._logger.info("Connected to camera")
        return True

    def disconnect(self):
        """
        Disconnect from the camera
        """
        if self._stream is None:
            self._logger.warning("Already disconnected from camera")
            return
        self._stream = None
        self._logger.info("Disconnected from camera")
        return

    def get_frame(self) -> np.ndarray:
        """
        Get a frame from the stream
        """
        if self._stream is None:
            self._logger.warning("Not connected to camera")
            return
        ret = False
        while not ret:
            self._logger.debug("Waiting for lock")
            self._logger.debug("Lock acquired")
            frame: av.VideoFrame = next(self._stream).decode()[0]
            frame = frame.to_ndarray(format="bgr24")
            ret = frame is not None
            if ret:
                self._logger.info("Frame read")
            else:
                self._logger.warning("Unable to read frame")
        return frame
    