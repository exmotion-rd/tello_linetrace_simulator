

from collections import OrderedDict
from enum import Enum
from threading import Thread
from typing import Generic, List, TypeVar
import airsim
import math
import numpy as np
import socket
import subprocess
import time

SIMSCALE = 5

CONTROL_UDP_PORT = 8889
STATE_UDP_PORT = 8890
VIDEO_UDP_PORT = 11111

class Mode(Enum):
    BINARY = 0
    SDK = 1
    
class VideoStream(Enum):
    OFF = 0
    ON = 1

mode: Mode
video_stream: VideoStream
controller_ip: str
running: bool

rc_time = None

def control_comm_proc() -> None:
    def _cmd_command(args: List[str]) -> str:
        # entry SDK mode
        global mode
        mode = Mode.SDK
        global controller_ip
        controller_ip = addr[0]
        return 'ok'

    def _cmd_takeoff(args: List[str]) -> str:
        # Tello auto takeoff
        airsim_client.takeoffAsync()
        return 'ok'

    def _cmd_land(args: List[str]) -> str:
        # Tello auto land
        airsim_client.landAsync()
        return 'ok'

    def _cmd_streamon(args: List[str]) -> str:
        # Set video stream on
        global video_stream
        video_stream = VideoStream.ON
        return 'ok'

    def _cmd_streamoff(args: List[str]) -> str:
        # Set video stream off
        global video_stream
        video_stream = VideoStream.OFF
        return 'ok'

    def _cmd_up(args: List[str]) -> str:
        # Tello fly up with distance x cm
        # x: 20-500
        x = float(args[0])
        delta = SIMSCALE * 0.01 * x
        state = airsim_client.getMultirotorState()
        pos = state.kinematics_estimated.position
        airsim_client.moveToPositionAsync(pos.x_val, pos.y_val, pos.z_val - delta, 1.0)
        return 'ok'

    def _cmd_down(args: List[str]) -> str:
        # Tello fly down with distance x cm
        # x: 20-500
        x = float(args[0])
        delta = SIMSCALE * 0.01 * x
        state = airsim_client.getMultirotorState()
        pos = state.kinematics_estimated.position
        airsim_client.moveToPositionAsync(pos.x_val, pos.y_val, pos.z_val + delta, 1.0)
        return 'ok'

    def _cmd_left(args: List[str]) -> str:
        # Tello fly left with distance x cm
        # x: 20-500
        x = float(args[0])
        delta = SIMSCALE * 0.01 * x
        state = airsim_client.getMultirotorState()
        pos = state.kinematics_estimated.position
        airsim_client.moveToPositionAsync(pos.x_val, pos.y_val - delta, pos.z_val, 1.0)
        return 'ok'

    def _cmd_right(args: List[str]) -> str:
        # Tello fly right with distance x cm
        # x: 20-500
        x = float(args[0])
        delta = SIMSCALE * 0.01 * x
        state = airsim_client.getMultirotorState()
        pos = state.kinematics_estimated.position
        airsim_client.moveToPositionAsync(pos.x_val, pos.y_val + delta, pos.z_val, 1.0)
        return 'ok'

    def _cmd_forward(args: List[str]) -> str:
        # Tello fly forward with distance x cm
        # x: 20-500
        x = float(args[0])
        delta = SIMSCALE * 0.01 * x
        state = airsim_client.getMultirotorState()
        pos = state.kinematics_estimated.position
        airsim_client.moveToPositionAsync(pos.x_val + delta, pos.y_val, pos.z_val, 1.0)
        return 'ok'

    def _cmd_back(args: List[str]) -> str:
        # Tello fly back with distance x cm
        # x: 20-500
        x = float(args[0])
        delta = SIMSCALE * 0.01 * x
        state = airsim_client.getMultirotorState()
        pos = state.kinematics_estimated.position
        airsim_client.moveToPositionAsync(pos.x_val - delta, pos.y_val, pos.z_val, 1.0)
        return 'ok'

    def _cmd_cw(args: List[str]) -> str:
        # Tello rotate x degree clockwise
        # x: 1-3600
        x = float(args[0])
        # TODO IMPREMENT ME
        return 'ok'

    def _cmd_ccw(args: List[str]) -> str:
        # Tello rotate x degree counterclockwise
        # x: 1-3600
        x = float(args[0])
        # TODO IMPREMENT ME
        return 'ok'

    def _cmd_rc(args: List[str]) -> str:
        # Send RC control via four channels.
        # a: left/right (-100~100)
        # b: forward/backward (-100~100)
        # c: up/down (-100~100)
        # d: yaw (-100~100)
        a, b, c, d = [float(arg) for arg in args]

        V_SCALE = 0.01
        YAW_RATE_SCALE = 0.1
        vx = V_SCALE * b
        vy = V_SCALE * a
        vz = V_SCALE * c
        yaw_rate = YAW_RATE_SCALE * d
        duration = 1.0

        global rc_time
        if time.time() - rc_time > 1.0:
            rc_time = time.time()
            airsim_client.moveByVelocityBodyFrameAsync(vx, vy, vz, duration, yaw_mode = { 'is_rate': True, 'yaw_or_rate': yaw_rate})

        return 'ok'

    commands = {
        'command'   : _cmd_command,
        'takeoff'   : _cmd_takeoff,
        'land'      : _cmd_land,
        'streamon'  : _cmd_streamon,
        'streamoff' : _cmd_streamoff,
        'up'        : _cmd_up,
        'down'      : _cmd_down,
        'left'      : _cmd_left,
        'right'     : _cmd_right,
        'forward'   : _cmd_forward,
        'back'      : _cmd_back,
        'cw'        : _cmd_cw,
        'ccw'       : _cmd_ccw,
        'rc'        : _cmd_rc,
    }

    airsim_client = airsim.MultirotorClient()
    airsim_client.confirmConnection()
    airsim_client.enableApiControl(True)
    airsim_client.armDisarm(True)

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_socket.bind(('', CONTROL_UDP_PORT))

    global running
    while True:
        command, addr = control_socket.recvfrom(1024)
        command = command.decode(encoding = 'ASCII')
        func, *args = command.split()
        if func in commands:
            response = commands[func](args)
        else:
            response = 'error'
        control_socket.sendto(response.encode('ASCII'), addr)

def state_comm_proc() -> None:
    global mode
    global video_stream
    global controller_ip
    global running

    def format(name, value) -> str:
        fmt = None
        if isinstance(value, int):
            fmt = '{:d}'
        elif isinstance(value, float):
            fmt = '{:.2f}'
        else:
            raise Exception
        return ':'.join([name, fmt.format(value)])

    airsim_client = airsim.MultirotorClient()
    airsim_client.confirmConnection()
    airsim_client.enableApiControl(True)

    state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        if mode == Mode.SDK:
            k = airsim_client.getMultirotorState().kinematics_estimated
            pitch, roll, yaw = airsim.utils.to_eularian_angles(k.orientation)
            state = OrderedDict()
            state['pitch'] = int(math.degrees(pitch))
            state['roll']  = int(math.degrees(roll))
            state['yaw']   = int(math.degrees(yaw))
            state['vgx']   = int(100 * k.linear_velocity.x_val)
            state['vgy']   = int(100 * k.linear_velocity.y_val)
            state['vgz']   = int(100 * k.linear_velocity.z_val)
            state['templ'] = int(0)
            state['temph'] = int(0)
            state['tof']   = int(0)
            state['h']     = int(100 * k.position.z_val)
            state['bat']   = float(0.0)
            state['baro']  = int(0)
            state['time']  = int(0)
            state['agx']   = float(k.linear_acceleration.x_val)
            state['agy']   = float(k.linear_acceleration.y_val)
            state['agz']   = float(k.linear_acceleration.z_val)

            data = ':'.join([format(name, value) for name, value in state.items()])
            data = data.encode('ASCII')
            state_socket.sendto(data, (controller_ip, STATE_UDP_PORT))
            time.sleep(0.1)

def video_comm_proc() -> None:
    global mode
    global video_stream
    global controller_ip
    global running

    airsim_client = airsim.MultirotorClient()
    airsim_client.confirmConnection()
    airsim_client.enableApiControl(True)

    # NEED TO INSTALL FFMPEG
    while True:
        if mode == Mode.SDK:
            address = f'udp://{controller_ip}:{VIDEO_UDP_PORT}'
            command = (
                'ffmpeg',
                '-f', 'rawvideo',
                '-pixel_format', 'bgr24',
                '-video_size', '960x720',
                '-framerate', '15',
                '-i', '-',
                '-an',
                '-c:v', 'libx264',
                '-g', '15',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-f', 'mpegts',
                #'-f', 'h264',
                address)
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            break

    while True:
        if video_stream == VideoStream.ON:
            start_time = time.perf_counter()
            requests = [airsim.ImageRequest('0', airsim.ImageType.Scene, False, False)]
            responses = airsim_client.simGetImages(requests)
            response = responses[0]
            end_time = time.perf_counter()
            print(end_time - start_time)
            frame = np.fromstring(response.image_data_uint8, dtype=np.uint8)
            process.stdin.write(frame.tobytes())
            process.stdin.flush()

def main():
    global mode
    global video_stream
    global controller_ip
    global running
    global rc_time

    mode = Mode.BINARY
    video_stream = VideoStream.OFF
    controller_ip = None
    running = True
    rc_time = time.time()

    control_comm_thread = Thread(target = control_comm_proc, daemon = True)
    state_comm_thread = Thread(target = state_comm_proc, daemon = True)
    video_comm_thread = Thread(target = video_comm_proc, daemon = True)

    control_comm_thread.start()
    state_comm_thread.start()
    video_comm_thread.start()

    while True:
        time.sleep(0.1)

    # TODO SHUTDOWN GRACEFLLY!

if __name__ == '__main__':
    main()
