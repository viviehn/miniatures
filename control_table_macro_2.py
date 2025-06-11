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

parser = argparse.ArgumentParser()
parser.add_argument('--num_init_steps', type=int, default=0)
parser.add_argument('--num_shoot_steps', type=int, default=9)
parser.add_argument('--rot_degree', type=int, default=15)
parser.add_argument('--half_rot', action='store_true')
args = parser.parse_args()

num_back_steps = args.num_init_steps + args.num_shoot_steps + 1
half_rot = args.half_rot
rot_degree=args.rot_degree
total_rot=180 if half_rot else 360

def post_focus_drive(camera, step):
    time.sleep(WAIT_TO_FOCUS)
    ret = camera._post(path='/ccapi/ver100/shooting/control/drivefocus',
                 json={"value": step})

def put_av(camera, av):
    time.sleep(WAIT_TO_FOCUS)
    ret = camera._put(path='/ccapi/ver100/shooting/settings/av',
                 json={"value": av})

async def turn_table(delay, new_position):
    await asyncio.sleep(delay)
    print(new_position)
    #stepper.setTargetPosition(new_position)

def take_photo(camera):
    print('take photo')
    time.sleep(WAIT_TO_SHOOT)
    camera.shoot(af=False)
    time.sleep(WAIT_TO_SHOOT)


def main():
    subprocess.call(['nmcli', 'd', 'wifi', 
	'connect', CANON_SSID, 
	'password', CANON_PWD])
    stepper = Stepper()
    stepper.openWaitForAttachment(5000)
    stepper.setCurrentLimit(0.67)
    stepper.setEngaged(True)
    #set acceleration limit?

    camera = CCAPI(debug=DEBUG)
    print(camera.get_settings_value("av"))

    start_position = 0

    for rot_iter in tqdm.tqdm(range(int(360/rot_degree))):
        new_position = start_position + rot_iter*rot_degree/(RESCALE_FACTOR)
        time.sleep(WAIT_TO_TURN)
        stepper.setTargetPosition(new_position)

        # reset to beginning of lens focus range
        print("pull focus near")
        if rot_iter > 0:
            for _ in range(num_back_steps):
                post_focus_drive(camera, 'near3')

        # reset to beginning of focus for this obj
        print("init focus")
        for _ in range(args.num_init_steps):
            post_focus_drive(camera, 'far3')

        # take narrow aperture images
        print("taking narrow aperture images")
        put_av(camera, "f22")
        take_photo(camera)

        # move to halfway point
        print("set focus to halfway point")
        for _ in range(int(args.num_shoot_steps/2)):
            post_focus_drive(camera, 'far3')
        print("taking narrow aperture images..")
        take_photo(camera)
        for _ in range(int(args.num_shoot_steps/2)):
            post_focus_drive(camera, 'far3')
        print("taking narrow aperture images...")
        take_photo(camera)

        # reset to mid aperture
        #camera.av = "f4.0"
        print("reset focus")
        put_av(camera, "f11")
        for _ in range(num_back_steps):
            post_focus_drive(camera, 'near3')

        # reset to beginning of focus for this obj
        for _ in range(args.num_init_steps):
            post_focus_drive(camera, 'far3')

        # step through focus
        print("taking wide aperture images...")
        for _ in range(0, args.num_shoot_steps, 2):
            take_photo(camera)
            post_focus_drive(camera, 'far3')
            post_focus_drive(camera, 'far3')
        take_photo(camera)

        # reset to wide aperture
        #camera.av = "f4.0"
        print("reset focus")
        put_av(camera, "f4.0")
        for _ in range(num_back_steps):
            post_focus_drive(camera, 'near3')

        # reset to beginning of focus for this obj
        for _ in range(args.num_init_steps):
            post_focus_drive(camera, 'far3')

        # step through focus
        print("taking wide aperture images...")
        for _ in range(args.num_shoot_steps):
            take_photo(camera)
            post_focus_drive(camera, 'far3')


    stepper.close()

main()
