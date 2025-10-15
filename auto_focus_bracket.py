from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
from ccapi.ccapi import CCAPI
import asyncio, time
import tqdm
import argparse, subprocess

# motor specifications
STEP_ANGLE=1.8 # in degrees
GEAR_RATIO=100
RESCALE_FACTOR=STEP_ANGLE/(16*GEAR_RATIO)

CANON_SSID='EOSR7_B24014-433_Canon0A'
CANON_PWD='pFnnqvC7'
CANON_IP='192.168.1.2'

# app specifications
DEBUG=False
WAIT_TO_TURN=2
WAIT_TO_FOCUS=1
WAIT_TO_SHOOT=2

NEAR_STR='near1'
FAR_STR='far1'

WIDE_AV='f2.8'
MED_AV='f5.6'
NARROW_AV='f8.0'

def put_av(camera, av):
    ret = camera._put(path='/ccapi/ver100/shooting/settings/av',
                 json={"value": av})
    while ret.status_code != 200:
        time.sleep(.25)
        ret = camera._put(path='/ccapi/ver100/shooting/settings/av',
                     json={"value": av})
    return ret

def configure_focus_bracketing(camera, step_size=1, num_steps=49):
    focus_api_path = '/ccapi/ver100/shooting/settings/focusbracketing'

    ret = camera._put(path=f'{focus_api_path}',
                 json={"value": "enable"})
    while ret.status_code != 200:
        time.sleep(.25)
        ret = camera._put(path=f'{focus_api_path}',
                     json={"value": "enable"})

    ret = camera._put(path=f'{focus_api_path}/focusincrement',
             json={"value": step_size})
    while ret.status_code != 200:
        time.sleep(.25)
        ret = camera._put(path=f'{focus_api_path}/focusincrement',
                 json={"value": step_size})

    time.sleep(.25)
    ret = camera._put(path=f'{focus_api_path}/numberofshots',
                 json={"value": num_steps})
    while ret.status_code != 200:
        time.sleep(.25)
        ret = camera._put(path=f'{focus_api_path}/numberofshots',
                     json={"value": num_steps})

def take_photo(camera):
    time.sleep(1)
    ret = camera.shoot(af=False)

def post_focus_drive(camera, step):
    ret = camera._post(path='/ccapi/ver100/shooting/control/drivefocus',
                 json={"value": step})
    while ret.status_code != 200:
        time.sleep(.25)
        ret = camera._post(path='/ccapi/ver100/shooting/control/drivefocus',
                     json={"value": step})
    return ret

def reset_focus(camera, num_steps):
    for _ in range(num_steps):
        ret = post_focus_drive(camera, 'near3')


# 10.09.2025 todo: run with larger step size and larger rot_degree?
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_shoot_steps', type=int, default=9)
    parser.add_argument('--single', action='store_true')
    parser.add_argument('--rot_degree', type=int, default=15)
    parser.add_argument('--half_rot', action='store_true')
    args = parser.parse_args()
    '''
    subprocess.call(['nmcli', 'd', 'wifi',
                     'connect', CANON_SSID,
                     'password', CANON_PWD])
    '''
    stepper = Stepper()
    stepper.openWaitForAttachment(5000)
    stepper.setCurrentLimit(0.67)
    stepper.setEngaged(True)

    # TODO: debug check for api response
    # Wait until api response is clear before continuing?
    # TODO: Calibration captures for aperture + zoom + focus bracketing step size combos
    # Assume camera always starts at max zoom and is focused on the closest part of the object

    rot_degree = args.rot_degree

    camera = CCAPI(debug=DEBUG, ip=CANON_IP)

    start_position = 0

    for rot_iter in tqdm.tqdm(range(int(360/rot_degree))):
        print(rot_iter)
        new_position = start_position + rot_iter*rot_degree/(RESCALE_FACTOR)

        num_wide_steps = args.num_shoot_steps
        num_med_steps = int(args.num_shoot_steps // 2)
        if num_med_steps % 2 == 0:
            num_med_steps = num_med_steps + 1
        #num_narrow_steps = int(args.num_shoot_steps // 9) + 1
        num_narrow_steps = int(args.num_shoot_steps // 6) + 1
        if num_narrow_steps % 2 == 0:
            num_narrow_steps = num_narrow_steps + 1

        reset_focus(camera, 19)
        put_av(camera, WIDE_AV)
        print(WIDE_AV)

        stepper.setTargetPosition(new_position)
        print('turning table')
        time.sleep(6)

        configure_focus_bracketing(camera, step_size=1, num_steps=num_wide_steps)
        take_photo(camera)

        reset_focus(camera, 19)
        put_av(camera, MED_AV)
        print(MED_AV)
        configure_focus_bracketing(camera, step_size=1, num_steps=num_med_steps)
        take_photo(camera)

        reset_focus(camera, 19)
        put_av(camera, NARROW_AV)
        print(NARROW_AV)
        configure_focus_bracketing(camera, step_size=1, num_steps=num_narrow_steps)
        take_photo(camera)
        time.sleep(WAIT_TO_TURN)

        if args.single:
            break
        if rot_iter > 0 and rot_iter%6 == 0:
            time.sleep(3)


if  __name__ == "__main__":
    main()
