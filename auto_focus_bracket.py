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
WAIT_TO_FOCUS=.25
WAIT_TO_SHOOT=2

NEAR_STR='near1'
FAR_STR='far1'

WIDE_AV='f4.0'
MED_AV='f8.0'
NARROW_AV='f16'

def configure_focus_bracketing(step_size=1, num_steps=49):
    focus_api_path = '/ccapi/ver100/shooting/settings/focusbracketing'

    campera._put(path=f'{focus_api_path}',
                 json={"value": "enable"})

    campera._put(path=f'{focus_api_path}/focusincrement',
                 json={"value": step_size})

    campera._put(path=f'{focus_api_path}/numberofshots',
                 json={"value": num_steps})

def take_photo(camera):
    time.sleep(WAIT_TO_SHOOT)
    camera.shoot(af=False)
    time.sleep(WAIT_TO_SHOOT)

def post_focus_drive(camera, step):
    time.sleep(WAIT_TO_FOCUS)
    ret = camera._post(path='/ccapi/ver100/shooting/control/drivefocus',
                 json={"value": step})

def reset_focus(num_steps):
    for _ in range(num_steps):
        post_focus_drive(camera, 'near3')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_shoot_steps', type=int, default=9)
    parser.add_argument('--single', action='store_true')
    parser.add_argument('--rot_degree', type=int, default=15)
    parser.add_argument('--half_rot', action='store_true')
    args = parser.parse_args()
    subprocess.call(['nmcli', 'd', 'wifi',
                     'connect', CANON_SSID,
                     'password', CANON_PWD])
    stepper = Stepper()
    stepper.openWaitForAttachment(5000)
    stepper.setCurrentLimit(0.67)
    stepper.setEngaged(True)

    camera = CCAPI(debug=DEBUG, ip=CANON_IP)

    for rot_iter in tqdm.tqdm(range(int(360/rot_degree))):
        new_position = start_position + rot_iter*rot_degree/(RESCALE_FACTOR)
        time.sleep(WAIT_TO_TURN)
        stepper.setTargetPosition(new_position)

        num_wide_steps = args.num_shoot_steps
        num_med_steps = int(args.num_shoot_steps // 5) + 1
        num_narrow_steps = int(args.num_shoot_steps // 9) + 1

        #TODO: Manually reset focus
        reset_focus(num_narrow_steps)
        put_av(camera, WIDE_AV)
        configure_focus_bracketing(step_size=1, num_steps=num_wide_steps)
        take_photo(camera)
        time.sleep(WAIT_TO_SHOOT*2)

        #TODO: Manually reset focus
        reset_focus(num_narrow_steps)
        put_av(camera, MED_AV)
        configure_focus_bracketing(step_size=5, num_steps=num_med_steps)
        time.sleep(WAIT_TO_SHOOT*2)

        #TODO: Manually reset focus
        reset_focus(num_narrow_steps)
        put_av(camera, NARROW_AV)
        configure_focus_bracketing(step_size=9, num_steps=num_narrow_steps)
        time.sleep(WAIT_TO_SHOOT*2)

        if args.single:
            break


if  __name__ == "__main__":
    main()
