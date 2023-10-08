# VARIABLES
DEBUG = True    # get debug message every time script is executed and use debug ssh command (ls)
TCPSEND = True  # send additional message over tcp (for example "fluentd")

MINIMUMRUNTIMELEFT = 900    # minimum runtime left in seconds
VERTIVIP = 'ip'

SSHIP = 'ip'
SSHUSER = 'user'
SSHPASSW = 'pw'
SSHPORT = 22

TCPIP = 'ip'
TCPPORT = 99999
TCPBUFFER = 1024

# INSTALL MISSING MODULES AUTOMATIC
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
    # returns minute
    heartbeat_time = time.strftime('%M', time.gmtime())
    return heartbeat_time

# CHECK UPS STATUS
def checkUpsApi():
    responseVertiv = requests.get('http://' + VERTIVIP + ':8210/api/PowerAssist', timeout=2)
    jsondict = responseVertiv.json()
    isAcPresent = (jsondict[0]['status']['isAcPresent'])
    runTimeToEmpty = (jsondict[0]['status']['runTimeToEmptyInSeconds'])
    if isAcPresent == False:
        if runTimeToEmpty > MINIMUMRUNTIMELEFT:
            runTimeLeft = runTimeToEmpty - MINIMUMRUNTIMELEFT
            return isAcPresent, runTimeLeft
        else:
            return isAcPresent, 0
    else:
        return isAcPresent, runTimeToEmpty

# PING SSH
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

# PING TCP
def checkTcp():
    with open(os.devnull, 'w') as DEVNULL:
        if platform.system() == "Linux":
            subprocess.check_call(
            ['ping', '-c', '1', TCPIP],
            stdout=DEVNULL,  # suppress output
            stderr=DEVNULL
            )
        if platform.system() == "Windows":
            subprocess.check_call(
            ['ping', TCPIP, '-n', '1'],
            stdout=DEVNULL,  # suppress output
            stderr=DEVNULL
            )

# SSH COMMAND IF UPS RUNTIME LOW
def sendSsh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHIP, SSHPORT, SSHUSER, SSHPASSW)
    stdin, stdout, stderr = ssh.exec_command('/sbin/shutdown.sh && /sbin/poweroff')

# DEBUG MODE
def sendSshDebug():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHIP, SSHPORT, SSHUSER, SSHPASSW)
    stdin, stdout, stderr = ssh.exec_command('ls')
    outlines=stdout.readlines(1) # read only first line
    resp = (''.join(outlines)).rstrip()
    return resp

# SEND TCP MESSAGE
def sendTcp(severityStr, msgStr):
    if TCPSEND == True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TCPIP, TCPPORT))
        send = '{"device_id":"PowerAssistHelper","timestamp":"' + currentTime() + '","severity":"' + severityStr + '","msg":"' + msgStr + '"}' + '\n'
        s.send((send).encode())
        s.close()

# MAIN
module = ['requests', 'paramiko', 'socket']
module_name = ['requests', 'paramiko', 'socket']
try:
    import importlib
    import subprocess
    import platform
    import os
    import socket
    import time
    installModules(module, module_name)

    isAcPresent, runTimeLeft = checkUpsApi()
    checkSsh()
    checkTcp()

    if DEBUG == True:
        # Print ssh
        severityStr = 'DEBUG'
        msgStr = str(sendSshDebug())
        print(f'{currentTime()} : {severityStr} : {msgStr}')
        sendTcp(severityStr, msgStr)
        # Print runtime
        severityStr = 'DEBUG'
        msgStr = str(runTimeLeft) + ' seconds estimated runtime.'
        print(f'{currentTime()} : {severityStr} : {msgStr}')
        sendTcp(severityStr, msgStr)

    if runTimeLeft == 0:
        if DEBUG == True:
            severityStr = 'DEBUG'
            msgStr = str(sendSshDebug())
            print(f'{currentTime()} : {severityStr} : {msgStr}')
            sendTcp(severityStr, msgStr)
        else:
            severityStr = 'WARNING'
            msgStr = 'Shutdown now.'
            print(f'{currentTime()} : {severityStr} : {msgStr}')
            sendTcp(severityStr, msgStr)
            sendSsh()
    elif isAcPresent == False:
        severityStr = 'WARNING'
        msgStr = 'AC lost! ' + str(runTimeLeft) + ' seconds runtime left.'
        print(f'{currentTime()} : {severityStr} : {msgStr}')
        sendTcp(severityStr, msgStr)
    elif heartbeatTime() == '00':
        severityStr = 'INFO'
        msgStr = currentTime() + ' : ' + str(runTimeLeft) + ' seconds estimated runtime.'
        print(f'{currentTime()} : {severityStr} : {msgStr}')
        sendTcp(severityStr, msgStr)
    else:
        pass
except Exception as err:
    try:
        severityStr = 'ERROR'
        msgStr = str(err)
        print(f'{currentTime()} : {severityStr} : {err}')
        sendTcp(severityStr, msgStr)
    except Exception as err:
        severityStr = 'ERROR'
        msgStr = str(err)
        print(f'{currentTime()} : {severityStr} : {err}')
