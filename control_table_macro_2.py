from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
from ccapi.ccapi import CCAPI
import asyncio, time
import tqdm
import argparse

# motor specifications
STEP_ANGLE=1.8 # in degrees
GEAR_RATIO=100
RESCALE_FACTOR=STEP_ANGLE/(16*GEAR_RATIO)

# turntable user specifications
rot_degree=15
half_rot=False
total_rot=180 if half_rot else 360

# app specifications
DEBUG=False
WAIT_TO_TURN=2
WAIT_TO_FOCUS=3
WAIT_TO_SHOOT=2

parser = argparse.ArgumentParser()
parser.add_argument('--num_init_steps', type=int)
parser.add_argument('--num_shoot_steps', type=int)
args = parser.parse_args()

num_back_steps = args.num_init_steps + args.num_shoot_steps + 1

def post_focus_drive(camera, step):
    time.sleep(1)
    ret = camera._post(path='/ccapi/ver100/shooting/control/drivefocus',
                 json={"value": step})
    print(ret)

def put_av(camera, av):
    time.sleep(1)
    ret = camera._put(path='/ccapi/ver100/shooting/settings/av',
                 json={"value": av})
    print(ret)

async def turn_table(delay, new_position):
    await asyncio.sleep(delay)
    print(new_position)
    #stepper.setTargetPosition(new_position)

async def take_photo(delay):
    await asyncio.sleep(delay)
    print('take photo')


def main():
    stepper = Stepper()
    stepper.openWaitForAttachment(5000)
    stepper.setCurrentLimit(0.67)
    stepper.setEngaged(True)
    #set acceleration limit?

    camera = CCAPI(debug=DEBUG)
    print(camera.get_settings_value("av"))


    time.sleep(WAIT_TO_SHOOT)

    start_position = 0

    for rot_iter in tqdm.tqdm(range(int(360/rot_degree))):
        new_position = start_position + rot_iter*rot_degree/(RESCALE_FACTOR)
        time.sleep(WAIT_TO_TURN)
        stepper.setTargetPosition(new_position)

        # reset to beginning of lens focus range
        print("reset focus")
        if rot_iter > 0:
            for _ in range(num_back_steps):
                post_focus_drive(camera, 'near3')

        # reset to beginning of focus for this obj
        for _ in range(args.num_init_steps):
            post_focus_drive(camera, 'far3')

        # take narrow aperture images
        #camera.av = "f22"
        print("taking narrow aperture images.")
        put_av(camera, "f22")
        time.sleep(WAIT_TO_SHOOT)
        camera.shoot(af=False)
        time.sleep(WAIT_TO_SHOOT)
        # move to halfway point
        for _ in range(int(args.num_shoot_steps/2)):
            post_focus_drive(camera, 'far3')
        print("taking narrow aperture images..")
        time.sleep(WAIT_TO_SHOOT)
        camera.shoot(af=False)
        time.sleep(WAIT_TO_SHOOT)
        for _ in range(int(args.num_shoot_steps/2) - 1):
            post_focus_drive(camera, 'far3')
        print("taking narrow aperture images...")
        time.sleep(WAIT_TO_SHOOT)
        camera.shoot(af=False)
        time.sleep(WAIT_TO_SHOOT)

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
            time.sleep(WAIT_TO_SHOOT)
            camera.shoot(af=False)
            time.sleep(WAIT_TO_SHOOT)
            post_focus_drive(camera, 'far3')


    stepper.close()

main()
