from ccapi.ccapi import CCAPI
import asyncio, time
import tqdm

# motor specifications
STEP_ANGLE=1.8 # in degrees
GEAR_RATIO=100
RESCALE_FACTOR=STEP_ANGLE/(16*GEAR_RATIO)

# turntable user specifications
rot_degree=2

# app specifications
DEBUG=False
WAIT_TO_TURN=3
WAIT_TO_SHOOT=3

CANON_SSID='EOSR7_B24014-433_Canon0A'
CANON_PWD='pFnnqvC7'
CANON_IP='192.168.1.2'

def post_focus_drive(camera, step):
    camera._post(path='/ccapi/ver100/shooting/control/drivefocus',
                 json={"value": step})

def main():
    subprocess.call(['nmcli', 'd', 'wifi', 
	'connect', CANON_SSID, 
	'password', CANON_PWD])

    camera = CCAPI(debug=DEBUG)

    finding_starting_point = True
    init_steps = 0

    while finding_starting_point:
        cmd = input("Press Enter to continue, or s+enter to stop")
        if cmd == 's':
            finding_starting_point = False
            break
        # camera step forward
        post_focus_drive(camera, 'far3')
        init_steps += 1

    print(f'init steps: {init_steps}')

    stack_steps = 0
    finding_ending_point = True
    while finding_ending_point:
        cmd = input("Press Enter to continue, or s+enter to stop")
        if cmd == 's':
            finding_ending_point = False
            break
        # camera step forward
        post_focus_drive(camera, 'far3')
        stack_steps += 1

    print(f'stack steps: {stack_steps}')

    num_back_steps = init_steps + stack_steps + 3 # compensate just for good measure

    print(f'total steps: {num_back_steps}')


main()
