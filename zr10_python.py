"""
Python implementation of ZR10 SDK by SIYI
ZR10 webpage: http://en.siyi.biz/en/Gimbal%20Camera/ZR10/overview/
Author : Mohamed Abdelkader
Email: mohamedashraf123@gmail.com
Copyright 2022

Requirements:
crc16 module which is included with this package
- cd crc16-0.1.1
- python setup.py build
- sudo python setup.py install

"""

import socket
from time import sleep
import crc16
import logging

LOG_FORMAT='%(asctime)s [ZR10SDK] [%(levelname)s] [%(funcName)s]:\t%(message)s'

class ZR10SDK:
    """
    Implementation of ZR10 SDK communication protocol
    """

    def __init__(self, server_ip="192.168.144.25", port=37260) -> None:
        """"
        Params
        --
        server_ip [str] IP address of the camera
        port: [int] UDP port of the camera
        """
        self._debug= False # print debug messages
        if self._debug:
            d_level = logging.DEBUG
        else:
            d_level = logging.INFO
        logging.basicConfig(format=LOG_FORMAT, level=d_level)
        self._logger = logging.getLogger(__name__)
        

        self._server_ip = server_ip
        self._port = port

        self._BUFF_SIZE=1024

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rcv_wait_t = 1.0 # Receiving wait time
        self._socket.settimeout(self._rcv_wait_t) # 1 second timeout for recvfrom()

    def toHex(self, val, nbits):
        """
        Converts an integer to hexdecimal.
        Useful for negative integers where hex() doesn't work as expected
        """
        h = format((val + (1 << nbits)) % (1 << nbits),'x')
        if len(h)==1:
            h="0"+h
        return h
    def toInt(self, hexval):
        """
        Ref: https://www.delftstack.com/howto/python/python-hex-to-int/
        """
        bits = 16
        val = int(hexval, bits)
        if val & (1 << (bits-1)):
            val -= 1 << bits
        return val

    def connect(self) -> bool:
        """
        Connects to the camera UDP server using self._server_ip and self._port

        Returns
        --
        True: if connection is established with no errors
        False: if connection is not established
        """
        pass
    def disconnect(self) -> None:
        """
        Disconnect UDP socket
        """
        pass

    def sendMsg(self, msg) -> None:
        """
        Sends a message to the camera

        Params
        --
        msg [str] Message to send
        """
        b = bytes.fromhex(msg)
        self._socket.sendto(b, (self._server_ip, self._port))

    def rcvMsg(self):
        data=None
        try:
            data,addr = self._socket.recvfrom(self._BUFF_SIZE)
        except Exception as e:
            self._logger.error("%s. Did not receive message within %s second(s)", e, self._rcv_wait_t)
        return data

    def decodeMsg(self, msg) -> None:
        """
        Decodes messages that are received on the rcv buffer, and returns the DATA fields.

        Params
        --
        msg: [str] full message received from server

        Returns
        --
        [str] string of hexadecimal of DATA fields.
        """
        DATA = ""
        if len(msg)==0:
            self._logger.error("No data to decode")
            return DATA

        # check crc16, if msg is OK!
        msg_crc=msg[-4:] # last 4 characters
        payload=msg[:-4]
        crc=self.calcCRC16(payload)
        if crc!=msg_crc:
            self._logger.error("CRC16 is not valid. Message is corrupted!")
            return DATA
        
        l1 = msg[6:8]
        l2 = msg[8:10]
        data_len = l2+l1
        data_len = int('0x'+data_len, base=16)
        char_len = data_len*2
        
        cmd_id = msg[14:16]
        
        DATA = msg[16:16+char_len]

        return DATA



    def calcCRC16(self, msg: str):
        """
        Calculates the two bytes CRC16, with swaped order, and returns them as a string
        """
        try:
            b = bytes.fromhex(msg)
            int_crc = crc16.crc16xmodem(b)
            str_crc = format(int_crc, 'x')
            # Make sure we get 4 characters
            if len(str_crc)==3:
                str_crc = "0"+str_crc
            c1 = str_crc[2:]
            c2 = str_crc[0:2]
            crc = c1+c2
            return crc
        except Exception as e:
            self._logger.error("%s", e)
            return None

    def encodeMsg(self, data_len, data, cmd_id):
        """
        Encodes a msg according to SDK protocol

        Returns
        --
        [str] Encoded msg. Empty string if crc16 is not successful
        """
        STX="5566" # Starting bytes in string 0x5566
        CTRL = "01"
        SEQ = "0000" # low byte on the left
        msg_front = STX+CTRL+data_len+SEQ+cmd_id+data
        crc = self.calcCRC16(msg_front)
        if crc is not None:
            msg = msg_front+crc
            self._logger.debug("Encoded msg: %s", msg)
            return msg
        else:
            self._logger.error("crc16 is None")
            return ''

    ###############################################################################
    #                                Message construction                         #
    ###############################################################################

    def acquireFirmwareVersionMsg(self) -> str:
        """
        Prepares the Acquire Firmware Version message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data=""
        data_len = "0000"
        cmd_id = "01"
        return self.encodeMsg(data_len, data, cmd_id)


    def acquireHardwareIdMsg(self) -> str:
        """
        Prepares the Acquire Hardware ID message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data=""
        data_len = "0000"
        cmd_id = "02"
        return self.encodeMsg(data_len, data, cmd_id)

    def autoFocusMsg(self) -> str:
        """
        Prepares the Auto Focus message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="01"
        data_len = "0100"
        cmd_id = "04"
        return self.encodeMsg(data_len, data, cmd_id)

    def stopZoomMsg(self) -> str:
        """
        Prepares the Stop Zoom message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="00"
        data_len = "0100"
        cmd_id = "05"
        return self.encodeMsg(data_len, data, cmd_id)

    def zoomInMsg(self) -> str:
        """
        Prepares the Manual Zoom In message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="01"
        data_len = "0100"
        cmd_id = "05"
        return self.encodeMsg(data_len, data, cmd_id)

    def zoomOutMsg(self) -> str:
        """
        Prepares the Manual Zoom Out message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="ff"
        data_len = "0100"
        cmd_id = "05"
        return self.encodeMsg(data_len, data, cmd_id)

    def manualFocusMsg(self, flag) -> str:
        """
        Prepares the Manual Focus message, and returns it as a string

        Params
        --
        flag: [int] 1: long shot in, 0, stop , -1: close shot

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data=self.toHex(flag, 8)
        data_len = "0100"
        cmd_id = "06"
        return self.encodeMsg(data_len, data, cmd_id)

    def gimbalRotationMsg(self, yaw_speed, pitch_speed) -> str:
        """
        Prepares the Gimbal Rotation message, and returns it as a string

        Params
        --
        yaw_speed: [int] -100~0~100: Negative and positive represent two directions, higher or lower the number is away from 0, faster the rotation speed is. Send 0 when released from control command and gimbal stops rotation.
        pitch_speed: [int] -100~0~100: Negative and positive represent two directions, higher or lower the number is away from 0, faster the rotation speed is. Send 0 when released from control command and gimbal stops rotation.

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data1=self.toHex(yaw_speed, 8)
        data2=self.toHex(pitch_speed, 8)
        data=data1+data2
        data_len = "0200"
        cmd_id = "07"
        return self.encodeMsg(data_len, data, cmd_id)

    def centerMsg(self) -> str:
        """
        Prepares the Center Rotation message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="01"
        data_len = "0100"
        cmd_id = "08"
        return self.encodeMsg(data_len, data, cmd_id)

    def gimbalInfoMsg(self) -> str:
        """
        Prepares the Acquire Gimbal Configuration message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data=""
        data_len = "0000"
        cmd_id = "0a"
        return self.encodeMsg(data_len, data, cmd_id)

    def functionFeedbackMsg(self) -> str:
        """
        Prepares the Function Feedback Information message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data=""
        data_len = "0000"
        cmd_id = "0b"
        return self.encodeMsg(data_len, data, cmd_id)

    def takePhotoMsg(self) -> str:
        """
        Prepares the Take Photo message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="00"
        data_len = "0100"
        cmd_id = "0c"
        return self.encodeMsg(data_len, data, cmd_id)

    def startStopRecordingMsg(self) -> str:
        """
        Prepares the Start/Stop Recording message, and returns it as a string

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="02"
        data_len = "0100"
        cmd_id = "0c"
        return self.encodeMsg(data_len, data, cmd_id)

    def lockModeMsg(self) -> str:
        """
        Prepares the Lock Mode message, and returns it as a string.

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="03"
        data_len = "0100"
        cmd_id = "0c"
        return self.encodeMsg(data_len, data, cmd_id)

    def followModeMsg(self) -> str:
        """
        Prepares the Follow Mode message, and returns it as a string.

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="04"
        data_len = "0100"
        cmd_id = "0c"
        return self.encodeMsg(data_len, data, cmd_id)

    def fpvModeMsg(self) -> str:
        """
        Prepares the FPV Mode message, and returns it as a string.

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data="05"
        data_len = "0100"
        cmd_id = "0c"
        return self.encodeMsg(data_len, data, cmd_id)

    def gimbalAttitudeMsg(self) -> str:
        """
        Prepares the Gimbal Attitude message, and returns it as a string.

        Returns
        --
        [str] encoded msg if available. Otherwise, returns empty string
        """
        data=""
        data_len = "0000"
        cmd_id = "0d"
        return self.encodeMsg(data_len, data, cmd_id)
    
    ###############################################################################
    #                                    Get  functions                           #
    ###############################################################################
    def getFirmwareVersion(self):
        """
        Sends msg to request firmware version

        Returns
        --
        - [str] Currently returns firmware version as hexdecimal string
        """

        msg = self.acquireFirmwareVersionMsg()
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None

            # decode msg
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            firmware_ver = hex_str[8:16]
            self._logger.debug("Firmware version: %s", firmware_ver)
            return firmware_ver
                
        else:
            self._logger.error("Could not construct msg")
            return None

    def getHardwareID(self):
        """
        Sends msg to request hardware ID

        Returns
        --
        - [string] Hardwre ID as string of hexadecimal
        """
        msg = self.acquireHardwareIdMsg()
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None

            # TODO decode msg
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            hw_id = hex_str #int(hex_str, base=16)
            return hw_id
                
        else:
            self._logger.error("Could not construct msg")
            return None

    def getGimbalAttitude(self):
        """
        Sends msg to request gimbal attitude, and returns attitude in degrees, and attitude speed in deg/s.
        Values are accurate to one decimal place.

        Returns
        --
        yaw_deg: [float] yaw in degrees
        pitch_deg: [float] pitch in degrees
        roll_deg: [float] roll in degrees
        yaw_velocity: [float] yaw speed in degrees/second
        pitch_velocity: [float] pitch speed in degrees/second
        roll_velocity: [float] roll speed in degrees/second
        """
        msg = self.gimbalAttitudeMsg()
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None

            self._logger.debug("Server msg: %s", server_msg.hex())

            # decode msg
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            yaw_deg = self.toInt(hex_str[2:4]+hex_str[0:2]) /10.
            pitch_deg = self.toInt(hex_str[6:8]+hex_str[4:6]) /10.
            roll_deg = self.toInt(hex_str[10:12]+hex_str[8:10]) /10.
            yaw_velocity = self.toInt(hex_str[14:16]+hex_str[12:14]) /10.
            pitch_velocity = self.toInt(hex_str[18:20]+hex_str[16:18]) /10.
            roll_velocity = self.toInt(hex_str[22:24]+hex_str[20:22]) /10.
            return yaw_deg, pitch_deg, roll_deg, yaw_velocity, pitch_velocity, roll_velocity
                
        else:
            self._logger.error("Could not construct msg")
            return None

    def getGimbalInfo(self):
        """
        Sends msg to request gimbal configuration information

        Returns
        --
        - record_state: [int] Recording status 0:OFF, 1: ON, 2: TF card slot is empty, 3:(Recording) Data loss in TF card recorded video, please check TF card
        - mounting_dir: [int] Mounting direction 1: Normal, 2: Upside down
        """
        msg = self.gimbalInfoMsg()
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None

            self._logger.debug("Server msg: %s", server_msg.hex())

            # decode msg
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            # hdr_state = int(hex_str[2:4], base=16)
            record_state = int(hex_str[-4:-2], base=16)
            # motion_mode = int(hex_str[8:10], base=16)
            mount_dir = int(hex_str[-2:], base=16)
            return record_state, mount_dir
                
        else:
            self._logger.error("Could not construct msg")
            return None

    def getFuncFeedback(self):
        """
        Sends msg to request Function Feedback Information

        Returns
        --
        ack_data: [int]
                    0: success, 1: Fail to take a photo (Please check if TF card is inserted)
                    2: HDR ON, 3: HDR OFF
                    4: Fail to record a video (Please check if TF card is inserted)
        """
        msg = self.functionFeedbackMsg()
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None

            self._logger.debug("Server msg: %s", server_msg.hex())

            # decode msg
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            ack_data = int(hex_str, base=16)
            return ack_data
                
        else:
            self._logger.error("Could not construct msg")
            return None

    ###############################################################################
    #                                    Set  functions                           #
    ###############################################################################
    def setAutoFocus(self):
        """
        Sends msg to request auto focus.

        Reutrns
        --
        True: Success
        False: Fail
        """
        msg = self.autoFocusMsg()
        self._logger.debug("autofocus hex string: %s", msg)
        
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            self._logger.debug("server_msg hex string: %s", server_msg.hex())

            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None
            
            # Decode mesage
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            flag = int(hex_str, base=16)
            if flag==1:
                return True
            else:
                return False
                
        else:
            self._logger.error("Could not construct msg")
            return None

    def setZoom(self, flag):
        """
        Sends zoom request

        Params
        --
        flag: [int] 1: start zoom in, 0: stop zoom, -1: start zoom out
        
        Returns
        --
        zoom_level: [int] 0~30
        """
        if (flag == 1):
            msg=self.zoomInMsg()
        elif (flag == -1):
            msg=self.zoomOutMsg()
        else:
            msg=self.stopZoomMsg()

        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None
            
            # Decode mesage
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            zoom_level = int(hex_str[2:4]+hex_str[0:2], base=16) /10.
            return zoom_level
                
        else:
            self._logger.error("Could not construct msg")
            return None

    def setFocus(self, flag):
        """
        Sends manual focus request

        Params
        --
        flag: [int] 1: Long shot, 0: stop manual focus, -1: close shot
        
        Returns
        --
        True: Success
        False: Fail
        """
        msg=self.manualFocusMsg(flag)
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None
            
            # Decode mesage
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            ret = int(hex_str, base=16)
            
            return bool(ret)
                
        else:
            self._logger.error("Could not construct msg")
            return None

    def centerGimbal(self):
        """
        Sends msg to set gimbal at the center position

        Returns
        --
        [bool] True if successful. False otherwise
        """
        msg = self.centerMsg()
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None

            # TODO decode msg
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)
            if len(hex_str)==0:
                self._logger.error("Decoded msg is empty")
                return None

            flag = int(hex_str, base=16)
            if flag==1:
                return True
            else:
                return False
        else:
            self._logger.error("Could not construct msg")
            return None

    def setGimbalSpeed(self, yaw_speed, pitch_speed):
        """
        Sends msg to set gimbal yaw and pitch speeds

        Params
        --
        yaw_speed: [int] -100~0~100. Percentage of max speed
        pitch_speed: [int] same as  yaw_speed

        Returns
        --
        [bool] True if successful. False otherwise
        """
        msg = self.gimbalRotationMsg(yaw_speed, pitch_speed)
        if len(msg)>0:
            self.sendMsg(msg)
            # Get feedback, timesout after 1 second
            server_msg = self.rcvMsg()
            if server_msg is None:
                self._logger.warning("Did not get feedback from camera")
                return None

            # TODO decode msg
            hex_str = self.decodeMsg(server_msg.hex())
            self._logger.debug("Data hex string: %s", hex_str)

            if len(hex_str)==0:
                return None

            flag = int(hex_str, base=16)
            if flag==1:
                return True
            else:
                return False
        else:
            self._logger.error("Could not construct msg")
            return None

    def setGimbalRotation(self, yaw, pitch, err_thresh=1):
        """
        Sets gimbal attitude angles yaw and pitch in degrees

        Params
        --
        yaw: [float] desired yaw in degrees
        pitch: [float] desired pitch in degrees
        err_thresh: [float] acceptable error threshold, in degrees, to stop correction
        """
        if (pitch >25 or pitch <-90):
            self._logger.error("desired pitch is outside controllable range -90~25")
            return

        if (yaw >45 or yaw <-45):
            self._logger.error("Desired yaw is outside controllable range -45~45")
            return

        # TODO 
        th = err_thresh
        gain = 3
        while(True):
            vals = self.getGimbalAttitude()
            if vals is None:
                self._logger.warning("Gimbal attitude feedback is None. Not setting rotations")
                break

            y,p,r, y_s, p_s, r_s = vals[0], vals[1], vals[2], vals[3], vals[4], vals[5]
            yaw_err = -yaw + y
            pitch_err = pitch - p

            self._logger.debug("yaw_err= %s", yaw_err)
            self._logger.debug("pitch_err= %s", pitch_err)

            if (abs(yaw_err) <= th and abs(pitch_err)<=th):
                ret = self.setGimbalSpeed(0, 0)
                self._logger.info("Goal rotation is reached")
                break

            y_speed_sp = max(min(100, int(gain*yaw_err)), -100)
            p_speed_sp = max(min(100, int(gain*pitch_err)), -100)
            self._logger.debug("yaw speed setpoint= %s", y_speed_sp)
            self._logger.debug("pitch speed setpoint= %s", p_speed_sp)
            ret = self.setGimbalSpeed(y_speed_sp, p_speed_sp)
            if(not ret):
                self._logger.warning("Could not set gimbal speed")
                break

            sleep(0.1) # command frequency

    def takePhoto(self):
        """
        Sends a message to take a single photo

        Returns
        --
        True: if success. False otherwise
        """
        msg = self.takePhotoMsg()
        if len(msg)>0:
            self.sendMsg(msg)
        # sleep(0.1) # Let the command sink

        ack_code = self.getFuncFeedback()

        if ack_code is None:
            self._logger.warning("Could not get acknowledgement")
            return False

        if ack_code==0:
            return True
        else:
            self._logger.error("Could not take photo. Error code: %s", ack_code)
            return False

    def toggleRecording(self):
        """
        Sends a message to toggle recording state. 
        
        Returns
        --
        [int] 1: Record is ON. Record is OFF. 2: TF card slot is empty. 3: Data loss, check SD card
        """

        msg = self.startStopRecordingMsg()
        if len(msg)>0:
            self.sendMsg(msg)

        sleep(0.1) # Let the command sink

        ack_code = self.getFuncFeedback()
        if ack_code is not None and ack_code>0:
            self._logger.error("Error in recodring. Check SD card. Code: %s", ack_code)
            return False

        info=self.getGimbalInfo()
        if info is None:
            self._logger.warning("Could not get gimbal info for acknowledgement to check recording state")
            return False

        record_state= info[0]
        
        if record_state == 1:
            self._logger.info("Recording is ON")
        elif record_state == 0:
            self._logger.info("Recording is OFF")
        else:
            self._logger.warning("Record state is unknown . Code: %s", record_state)

        return record_state

    def setLockMode(self):
        """
        Sends a message to set Lock mode

        Returns
        --
        True: if success. False otherwise
        """
        msg = self.lockModeMsg()
        print("[setLockMode] Lock mode msg", msg)
        if len(msg)>0:
            self.sendMsg(msg)

        ack_code = self.getFuncFeedback()

        if ack_code is None:
            self._logger.warning("Could not get acknowledgement msg")
            return False

        if ack_code==0:
            self._logger.info("Lock mode is set")
            return True
        else:
            self._logger.warning("Could not set Lock mode. Code: %s", ack_code)
            return False

    def setFollowMode(self):
        """
        Sends a message to set Follow mode

        Returns
        --
        True: if success. False otherwise
        """
        msg = self.followModeMsg()
        if len(msg)>0:
            self.sendMsg(msg)

        ack_code = self.getFuncFeedback()

        if ack_code is None:
            self._logger.warning("Could not get acknowledgement msg")
            return False

        if ack_code==0:
            self._logger.info("Follow mode is set")
            return True
        else:
            self._logger.warning("Could not set Follow mode. Code: %s", ack_code)
            return False

    def setFPVMode(self):
        """
        Sends a message to set FPV mode

        Returns
        --
        True: if success. False otherwise
        """
        msg = self.fpvModeMsg()
        if len(msg)>0:
            self.sendMsg(msg)

        ack_code = self.getFuncFeedback()

        if ack_code is None:
            self._logger.warning("Could not get acknowledgement msg")
            return False

        if ack_code==0:
            self._logger.info("FPV mode is set")
            return True
        else:
            self._logger.warning("Could not set FPV mode. Code: %s", ack_code)
            return False
            



def test():
    # cam = ZR10SDK(server_ip="127.0.0.1", port=5005)
    cam = ZR10SDK()

    # cam.getGimbalAttitude()
    fw_ver = cam.getFirmwareVersion()
    print("[test] FW version: ", fw_ver)
    hw_id = cam.getHardwareID()
    print("HW ID: ", hw_id)

    # cam.setGimbalSpeed(50,0)
    # sleep(0.5)
    # cam.setGimbalSpeed(0,0)

    cam.centerGimbal()
    sleep(2)

    # cam.setGimbalRotation(0,-80)

    # y,p,r,y_speed, p_speed, r_speed = cam.getGimbalAttitude()
    # print("Attitude [deg] yaw, pitch, roll: ", y,p,r)
    # print("Attitude speed [deg/s]: ", y_speed,p_speed,r_speed)

    # hdr_state, record_state, motion_mode, mount_dir=cam.getGimbalInfo()
    # print("HDR state: ", hdr_state)
    # print("Recording state: ", record_state)
    # print("Motion mode: ", motion_mode)
    # print("Mounting Direction: ", mount_dir)

    # fb = cam.setFocus(1)
    # print("[test] Manual focus, long shot: ", fb)
    # sleep(1)
    # fb = cam.setFocus(0)
    # print("[test] Manual focus, close shot: ", fb)
    # sleep (1)

    # fb = cam.setAutoFocus()
    # print("[test] Set auto focus: ", fb)

    
    # val = cam.setZoom(-1)
    # print("[test] Zooming out, level: ", val)
    # sleep(5)
    # val = cam.setZoom(0)
    # print("[test] Stop zoom, level: ", val)

    # val = cam.setZoom(1)
    # print("[test] Zooming in, level: ", val)
    # sleep(1)
    
    # val = cam.setZoom(0)
    # print("[test] Stop zoom, level: ", val)

    # fb = cam.takePhoto()
    # print("[test] Take photo: ", fb)

    # fb = cam.toggleRecording()
    # print("[test] Toggle recording: ", fb)

    # fb = cam.setFPVMode()
    # print("[test] Set FPV mode: ", fb)

    # fb = cam.setFollowMode()
    # print("[test] Set Follow mode: ", fb)

    # fb = cam.setLockMode()
    # print("[test] Set Lock mode: ", fb)
    

if __name__ == "__main__":
    test()