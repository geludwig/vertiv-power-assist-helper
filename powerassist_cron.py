
# VARIABLES
DEBUG = True     # dry run testing
TCPSEND = False  # send additional message over tcp (for example "fluentd")

MINIMUMRUNTIMELEFT = 900    # minimum usv runtime left in seconds
VERTIVIP = 'IP'

SSHIP = 'IP'
SSHUSER = 'USER'
SSHPASSW = 'PASSWORD'
SSHPORT = 22

TCPIP = 'IP'
TCPPORT = 0
TCPBUFFER = 1024

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
    heartbeat_time = time.strftime('%M', time.gmtime())
    return heartbeat_time

# CHECK UPS STATUS
def checkUpsApi():
    responseVertiv = requests.get('https://' + VERTIVIP + ':8210/api/PowerAssist', timeout=2, verify=False)
    jsondict = responseVertiv.json()
    isAcPresent = (jsondict[0]['status']['isAcPresent'])
    runTimeToEmpty = (jsondict[0]['status']['runTimeToEmptyInSeconds'])
    return isAcPresent, runTimeToEmpty

# PING SSH
def checkSsh():
    with open(os.devnull, 'w') as DEVNULL:
        if platform.system() == "Linux":
            subprocess.check_call(
            ['ping', '-c', '1', SSHIP],
            stdout=DEVNULL,
            stderr=DEVNULL
            )
        if platform.system() == "Windows":
            subprocess.check_call(
            ['ping', SSHIP, '-n', '1'],
            stdout=DEVNULL,
            stderr=DEVNULL
            )

# PING TCP
def checkTcp():
    if TCPSEND == True:
        with open(os.devnull, 'w') as DEVNULL:
            if platform.system() == "Linux":
                subprocess.check_call(
                ['ping', '-c', '1', TCPIP],
                stdout=DEVNULL,
                stderr=DEVNULL
                )
            if platform.system() == "Windows":
                subprocess.check_call(
                ['ping', TCPIP, '-n', '1'],
                stdout=DEVNULL,
                stderr=DEVNULL
                )

# SSH COMMAND
def sendSsh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHIP, SSHPORT, SSHUSER, SSHPASSW)
    stdin, stdout, stderr = ssh.exec_command('shutdown now') # good old exec ... yeah

# SSH COMMAND DEBUG
def sendSshDebug():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHIP, SSHPORT, SSHUSER, SSHPASSW)
    stdin, stdout, stderr = ssh.exec_command('uname -a')
    outlines=stdout.readlines(1)
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

    # disable ssl warnings due to self signed certificate
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    isAcPresent, runTimeLeft = checkUpsApi()
    checkSsh()
    checkTcp()

    # print additional debug message
    if DEBUG == True:
        severityStr = 'DEBUG'
        msgStr = str(sendSshDebug())
        print(f'{currentTime()} : {severityStr} : {msgStr}')
        sendTcp(severityStr, msgStr)
        severityStr = 'DEBUG'
        msgStr = str(runTimeLeft) + ' seconds estimated runtime.'
        print(f'{currentTime()} : {severityStr} : {msgStr}')
        sendTcp(severityStr, msgStr)

    # functions
    # send shutdown command over ssh and message over tcp
    if runTimeLeft <= MINIMUMRUNTIMELEFT:
        if DEBUG == True:
            severityStr = 'DEBUG'
            msgStr = str(sendSshDebug())
            print(f'{currentTime()} : {severityStr} : Printing ssh debug message instead of sending live ssh command.')
            print(f'{currentTime()} : {severityStr} : {msgStr}')
            sendTcp(severityStr, msgStr)
        else:
            severityStr = 'WARNING'
            msgStr = 'Shutdown now.'
            print(f'{currentTime()} : {severityStr} : {msgStr}')
            sendTcp(severityStr, msgStr)
            sendSsh()
    # send ac lost message over tcp and print to console
    elif isAcPresent == False:
        severityStr = 'WARNING'
        msgStr = 'AC lost! ' + str(runTimeLeft) + ' seconds runtime left.'
        print(f'{currentTime()} : {severityStr} : {msgStr}')
        sendTcp(severityStr, msgStr)
    # send heartbeat message every hour over tcp
    elif heartbeatTime() == '00':
        severityStr = 'INFO'
        msgStr = currentTime() + ' : ' + str(runTimeLeft) + ' seconds estimated runtime.'
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
