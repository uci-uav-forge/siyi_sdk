import av
import cv2
import numpy as np
import time
import logging
import threading
import collections

class SIYISTREAM:
    def __init__(self, server_ip: str = "192.168.144.25", port: int = 8554, name: str = "main.264", debug: bool = False):
        self._debug = debug
        d_level = logging.DEBUG if debug else logging.INFO
        LOG_FORMAT = ' [%(levelname)s] %(asctime)s [SIYISDK::%(funcName)s] :\t%(message)s'
        logging.basicConfig(format=LOG_FORMAT, level=d_level)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info("Initializing SIYISTREAM")
        self._server_ip = server_ip
        self._port = port
        self._name = name
        self._stream_link = f"rtsp://{self._server_ip}:{self._port}/{self._name}"
        self._container = None
        self._stream = None
        self._packet_queue = collections.deque(maxlen=5)
        self._latest_frame = None
        self._frame_mutex = threading.Lock()
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._decoder_thread = threading.Thread(target=self._decoder_loop, daemon=True)
        self._running = False

    def connect(self):
        """Connect to the RTSP camera and start threads."""
        if self._running:
            self._logger.warning("Already connected to camera")
            return

        self._container = av.open(self._stream_link, format="rtsp", options={"rtsp_transport": "tcp", "max_delay": "500000"})
        self._stream = self._container.demux()

        self._running = True
        self._reader_thread.start()
        self._decoder_thread.start()
        self._logger.info("Connected to camera and started streaming threads")
        return True

    def _reader_loop(self):
        """Continuously read compressed packets into a bounded queue."""
        self._logger.debug("Reader thread started")
        while self._running:
            try:
                packet = next(self._stream)
                if packet is not None:
                    if len(self._packet_queue) == self._packet_queue.maxlen:
                        # Drop the oldest packet to stay up to date
                        self._packet_queue.popleft()
                    self._packet_queue.append(packet)
            except StopIteration:
                self._logger.warning("End of stream reached")
                break
            except Exception as e:
                self._logger.error(f"Error reading packet: {e}")
                time.sleep(0.1)
                continue

    def _decoder_loop(self):
        """Decode packets only when available in the queue."""
        self._logger.debug("Decoder thread started")
        while self._running:
            if not self._packet_queue:
                time.sleep(0.005)
                continue

            packet = self._packet_queue.pop() 
            try:
                frames = packet.decode()
                if len(frames) > 0:
                    frame = frames[-1]
                    img = frame.to_ndarray(format="bgr24")
                    with self._frame_mutex:
                        self._latest_frame = img
            except Exception as e:
                self._logger.error(f"Error decoding packet: {e}")
                time.sleep(0.01)

    def get_frame(self) -> np.ndarray:
        """Return the latest decoded frame."""
        if not self._running:
            raise Exception("Not connected to camera")
        with self._frame_mutex:
            if self._latest_frame is None:
                raise Exception("No frame available yet")
            return self._latest_frame.copy()

    def disconnect(self):
        """Stop threads and close the stream."""
        if not self._running:
            self._logger.warning("Already disconnected from camera")
            return
        self._running = False
        self._reader_thread.join(timeout=2.0)
        self._decoder_thread.join(timeout=2.0)
        if self._container:
            self._container.close()
        self._logger.info("Disconnected from camera and stopped threads")
        return True