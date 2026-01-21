from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *

# motor specifications
STEP_ANGLE=1.8 # in degrees
GEAR_RATIO=100
RESCALE_FACTOR=STEP_ANGLE/(16*GEAR_RATIO)

stepper = Stepper()
stepper.openWaitForAttachment(5000)
stepper.setCurrentLimit(0.67)
stepper.setEngaged(True)

start_position = 0
new_position = 359. / RESCALE_FACTOR
stepper.setTargetPosition(new_position)
