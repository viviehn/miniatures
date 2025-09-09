from ccapi.ccapi import CCAPI
import asyncio, time
import tqdm
import argparse
import subprocess


CANON_SSID='EOSR7_B24014-433_Canon0A'
CANON_PWD='pFnnqvC7'
CANON_IP='192.168.1.2'
DEBUG=False

WAIT_TO_SHOOT=1

APERTURE_VALS=['2.5', '2.8', '3.2', '3.5', '4.0',
               '4.5', '5.0', '5.6', '6.3', '7.1',
               '8.0', '9.0', '10', '11', '13',
               '14', '16', '18', '20', '22',
               '25', '29', '32']

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

def take_photo(camera):
    print('take photo')
    time.sleep(WAIT_TO_SHOOT)
    camera.shoot(af=False)
    time.sleep(WAIT_TO_SHOOT)

def main():
    '''
    subprocess.call(['nmcli', 'd', 'wifi',
        'connect', CANON_SSID,
        'password', CANON_PWD])
    '''
    #set acceleration limit?

    camera = CCAPI(debug=DEBUG)
    '''

    put_av(camera, "f22")
    for _ in range(10):
        take_photo(camera)

    put_av(camera, "f4.0")
    for _ in range(10):
        take_photo(camera)

    for _ in range(5):
        put_av(camera, "f22")
        take_photo(camera)
        put_av(camera, "f4.0")
        take_photo(camera)

    put_av(camera, 'f22')
    post_focus_drive(camera, 'far3')
    for _ in range(10):
        take_photo(camera)

    for _ in range(10):
        post_focus_drive(camera, 'near3')
        post_focus_drive(camera, 'near3')
        post_focus_drive(camera, 'far3')
        take_photo(camera)
    '''

    for av in APERTURE_VALS:
        put_av(camera, f'f{av}')
        take_photo(camera)

main()
