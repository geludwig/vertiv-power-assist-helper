
# VARIABLES
DEBUG = True
MINIMUMRUNTIMELEFT = 900    # minimum runtime left in seconds
VERTIVIP = 'ip'
SSHIP = 'ip'
SSHUSER = 'user'
SSHPASSW = 'pw'
SSHPORT = 22

# INSTALL MISSING MODULES
def installModules(module, module_name):
    i = 0
    for x in module:
        try:
            globals()[module_name[i]] = importlib.import_module(x)
        except:
            if platform.system() == "Windows":
                subprocess.call(["py", "-m", "pip", "install", x])
            elif platform.system() == "Linux":
                subprocess.call(["python3", "-m", "pip", "install", x])
            else:
                print(f'Cannot install module {x}.')
                raise
            try:
                globals()[module_name[i]] = importlib.import_module(x)
            except:
                raise
        i += 1

# CURRENT TIME
def currentTime():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    return current_time

# HEARTBEAT TIME
def heartbeatTime():
    global hour_time
    hour_time = time.strftime('%H%M', time.gmtime())
    return hour_time

# HEARTBEAT
def heartbeat():
    if heartbeatTime() == '1200':
        print(currentTime() + ' [INFO] powerassist active')

# CKECK UPS STATUS
def checkUpsApi():
    responseVertiv = requests.get('http://' + VERTIVIP + ':8210/api/PowerAssist', timeout=1)
    jsondict = responseVertiv.json()
    isAcPresent = (jsondict[0]['status']['isAcPresent'])
    runTimeToEmpty = (jsondict[0]['status']['runTimeToEmptyInSeconds'])

    isAcPresent = False

    if isAcPresent == False:
        if runTimeToEmpty > MINIMUMRUNTIMELEFT:
            runTimeLeft = runTimeToEmpty - MINIMUMRUNTIMELEFT
            return isAcPresent, runTimeLeft
        else:
            return isAcPresent, 0
    else:
        return isAcPresent, runTimeToEmpty

# PING SSH IP
def checkSsh():
    with open(os.devnull, 'w') as DEVNULL:
        if platform.system() == "Linux":
            subprocess.check_call(
            ['ping', '-c', '1', SSHIP],
            stdout=DEVNULL,  # suppress output
            stderr=DEVNULL
            )
        if platform.system() == "Windows":
            subprocess.check_call(
            ['ping', SSHIP, '-n', '1'],
            stdout=DEVNULL,  # suppress output
            stderr=DEVNULL
            )

# SSH COMMAND IF UPS RUNTIME LOW
def sendSsh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHIP, SSHPORT, SSHUSER, SSHPASSW)
    stdin, stdout, stderr = ssh.exec_command('/sbin/shutdown.sh && /sbin/poweroff')

# SEND TCP MESSAGE
'''
def sendTcp():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCPIP, TCPPORT))
    s.send('{"MESSAGE"}' + '\n')
'''
    
# DEBUG MODE
def sendSshDebug():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHIP, SSHPORT, SSHUSER, SSHPASSW)
    stdin, stdout, stderr = ssh.exec_command('ls')
    outlines=stdout.readlines()
    resp=''.join(outlines)
    print(f'{resp}')

# MAIN
module = ['requests', 'paramiko']
module_name = ['requests', 'paramiko']
try:
    import importlib
    import subprocess
    import platform
    import os
    import socket
    import time
    installModules(module, module_name)
except Exception as err:
    print(f'{err}')
    exit()

try:
    heartbeat()
except Exception as err:
    print(f'{err}')
    exit()

try:
    isAcPresent, runTimeLeft = checkUpsApi()
except Exception as err:
    print(f'{err}')
    exit()

try:
    checkSsh()
except Exception as err:
    print(f'{err}')
    exit()

try:
    if DEBUG == True:
        print(f'[DEBUG] ssh test command.')
        sendSshDebug()
        if runTimeLeft == 0:
            print(f'[DEBUG] ssh command sent.')
        elif isAcPresent == False:
            print(f'[DEBUG] {str(runTimeLeft)} seconds runtime left.')
        else:
            print(f'[DEBUG] {str(runTimeLeft)} seconds estimated runtime.')
    else:
        if runTimeLeft == 0:
            sendSsh()
        elif isAcPresent == False:
            print(f'{str(runTimeLeft)} seconds runtime left.')
        else:
            print(f'{str(runTimeLeft)} seconds estimated runtime.')
except Exception as err:
    print(err)
    exit()
