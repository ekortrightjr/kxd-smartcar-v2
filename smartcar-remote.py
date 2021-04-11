import joystickapi
import msvcrt
import time
import rpyc


def handleAxisXYZ(axisXYZ):
    if (axisXYZ[0] == 0 and axisXYZ[1] < 0 and axisXYZ[2] == 0):
        carStateService.root.set_state("move", "fwd")
        carStateService.root.set_state("brakelights", "off")
        print("fwd")
    elif (axisXYZ[0] == 0 and axisXYZ[1] > 0 and axisXYZ[2] == 0):
        carStateService.root.set_state("move", "rev")
        carStateService.root.set_state("brakelights", "rev")
        print("rev")
    elif (axisXYZ[0] < 0 and axisXYZ[1] < 0 and axisXYZ[2] == 0):
        carStateService.root.set_state("move", "fwd-left")
        carStateService.root.set_state("brakelights", "off")
        print("fwd-left")
    elif (axisXYZ[0] > 0 and axisXYZ[1] < 0 and axisXYZ[2] == 0):
        carStateService.root.set_state("move", "fwd-right")
        carStateService.root.set_state("brakelights", "off")
        print("fwd-right")
    elif (axisXYZ[0] < 0 and axisXYZ[1] > 0 and axisXYZ[2] == 0):
        carStateService.root.set_state("move", "rev-left")
        carStateService.root.set_state("brakelights", "rev")
        print("rev-left")
    elif (axisXYZ[0] > 0 and axisXYZ[1] > 0 and axisXYZ[2] == 0):
        carStateService.root.set_state("move", "rev-right")
        carStateService.root.set_state("brakelights", "rev")
        print("rev-right")
    elif (axisXYZ[0] == 0 and axisXYZ[1] == 0 and axisXYZ[2] == 0):
        carStateService.root.set_state("move", "stop")
        carStateService.root.set_state("brakelights", "on")
        print("stop")
        
def handleBtns(btns):
    if (btns[4]):
        state = carStateService.root.get_state()
        print("state:", state)
        signalsMode = state["signals"]
        if (signalsMode != "left"):
            carStateService.root.set_state("signals", "left")
        elif (signalsMode == "left"):
            carStateService.root.set_state("signals", "off")

    if (btns[5]):
        state = carStateService.root.get_state()
        print("state:", state)
        signalsMode = state["signals"]
        if (signalsMode != "right"):
            carStateService.root.set_state("signals", "right")
        elif (signalsMode == "right"):
            carStateService.root.set_state("signals", "off")


print("start")

carStateService = rpyc.connect("192.168.1.243", 18861)
print("connected to car service")

num = joystickapi.joyGetNumDevs()
ret, caps, startinfo = False, None, None
for id in range(num):
    ret, caps = joystickapi.joyGetDevCaps(id)
    if ret:
        print("gamepad detected: " + caps.szPname)
        ret, startinfo = joystickapi.joyGetPosEx(id)
        break
else:
    print("no gamepad detected")

run = ret
while run:
    time.sleep(0.1)
    if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode(): # detect ESC
        run = False

    ret, info = joystickapi.joyGetPosEx(id)
    if ret:
        btns = [(1 << i) & info.dwButtons != 0 for i in range(caps.wNumButtons)]
        axisXYZ = [info.dwXpos-startinfo.dwXpos, info.dwYpos-startinfo.dwYpos, info.dwZpos-startinfo.dwZpos]
        axisRUV = [info.dwRpos-startinfo.dwRpos, info.dwUpos-startinfo.dwUpos, info.dwVpos-startinfo.dwVpos]

        if info.dwButtons:
            print("buttons: ", btns)
            handleBtns(btns)
        if any([abs(v) > 10 for v in axisXYZ]):
            print("axis:", axisXYZ)
            handleAxisXYZ(axisXYZ)
        else:
            carStateService.root.set_state("move", "stop")
            carStateService.root.set_state("brakelights", "on")
        if any([abs(v) > 10 for v in axisRUV]):
            print("roation axis:", axisRUV)

print("end")