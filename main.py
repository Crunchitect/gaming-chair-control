import websocket
import json
import functools
import threading
import keyboard
from reactive import ref, watch


spike = ref(False)
left_spike = ref(False)
right_spike = ref(False)
ccw_spike = ref(False)
cw_spike = ref(False)


def on_message(url, ws, message):
    sensor_type = url.split('.')[-1]
    match sensor_type:
        case 'accelerometer':
            values = json.loads(message)['values']
            x, _, z = values
            if x < -2:
                if cw_spike:
                    return
                if right_spike:
                    right_spike.value = False
                else:
                    left_spike.value = True
            elif x > 2:
                if ccw_spike:
                    return
                if left_spike:
                    left_spike.value = False
                else:
                    right_spike.value = True
            else:
                spike.value = 'no'

            if z > 16:
                move('space', True, True)
            elif z > 12:
                move('down', True, True)
        case 'gyroscope':
            values = json.loads(message)['values']
            alpha, beta, gamma = values
            if beta < -2:
                if cw_spike:
                    cw_spike.value = False
                else:
                    ccw_spike.value = True
            elif beta > 2:
                if ccw_spike:
                    ccw_spike.value = False
                else:
                    cw_spike.value = True
            else:
                spike.value = 'no'
                cw_spike.value = False
                ccw_spike.value = False


def on_error(ws, error):
    print("error occurred ", error)


def on_close(ws, close_code, reason):
    print("connection closed : ", reason)


def on_open(url, ws):
    print(url)
    print("connected")


def connect(url):
    ws = websocket.WebSocketApp(url,
                                on_open=functools.partial(on_open, url),
                                on_message=functools.partial(on_message, url),
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()


old_dir = ""


def move(direction, _, new):
    global old_dir
    if new:
        if direction == 'left' and old_dir == 'right':
            return
        if direction == 'right' and old_dir == 'left':
            return
        if direction == old_dir:
            return
        keyboard.press_and_release(direction)
        old_dir = direction



watch(left_spike, lambda old, new: move("left", old, new))
watch(right_spike, lambda old, new: move("right", old, new))
watch(ccw_spike, lambda old, new: move("z", old, new))
watch(cw_spike, lambda old, new: move("x", old, new))
# watch(spike, lambda old, new: move("none", old, new))


acl = threading.Thread(target=connect, args=("ws://192.168.1.140:42069/sensor/connect?type=android.sensor.accelerometer",))
gyr = threading.Thread(target=connect, args=("ws://192.168.1.140:42069/sensor/connect?type=android.sensor.gyroscope",))

acl.start()
gyr.start()
