### MODULES ###
import requests
import os
import subprocess
import paramiko
import sys
import time

### USER DEFINDED VARIABLES ###
runTimeLeft = 900 # runtime left before shutdown in seconds
testFlag = False # test ssh and powerassist connection
infoFlag = False # include additional ups data in log
vertivHost = '<ip/url>'
sshHost = '<ip/url>'
port = 22
username = '<usr ssh>'
password = '<pw ssh>'

### VARIABLES ###
shutdownFlag = False
lasttimeMinute = None
lasttimeHour = None
lastErrorFlagSSH = False
lastErrorFlagVertiv = False

### GLOBAL FUNCTIONS ###
def timeFunc():
    global timeMinute
    global timeHour
    timeMinute = time.strftime('%M', time.gmtime())
    timeHour = time.strftime('%H', time.gmtime())
    return (timeMinute, timeHour)

def timelogFunc():
    global currTime
    currTime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    return currTime

def activeFunc():
    log = open("log.txt", "a")
    log.write(timelogFunc() + ' [INFO] ups monitoring active\n')
    log.close()

def upsmonitorFunc():
    global shutdownFlag
    global lastErrorFlagSSH
    global lastErrorFlagVertiv
    log = open("log.txt", "a")
    # TEST POWER ASSIST API AVAILABILITY
    try:
        responseVertiv = requests.get('http://' + vertivHost + ':8210/api/PowerAssist', timeout=1)
    except requests.exceptions.Timeout:
        log.write(timelogFunc() + ' [ERROR] powerassist request timeout\n')
        errorFlagVertiv = True
    except requests.exceptions.RequestException:
        log.write(timelogFunc() + ' [ERROR] powerassist request fatal error\n')
        errorFlagVertiv = True        
    else:
        jsondict = responseVertiv.json()
        isAcPresent = (jsondict[0]['status']['isAcPresent'])
        runTimeToEmpty = (jsondict[0]['status']['runTimeToEmptyInSeconds'])
        percentLoad = (jsondict[0]['status']['percentLoad'])
        isCharging = (jsondict[0]['status']['isCharging'])
        errorFlagVertiv = False
    # TEST SSH AVAILABILITY
    with open(os.devnull, 'w') as DEVNULL:
        try:
            subprocess.check_call(
            ['ping', '-c', '2', sshHost],
            stdout=DEVNULL,  # suppress output
            stderr=DEVNULL
            )
            errorFlagSSH = False
        except subprocess.CalledProcessError:
            errorFlagSSH = True

    # ACTIONS
    if errorFlagSSH == False and errorFlagVertiv == False:
        if lastErrorFlagSSH == True or lastErrorFlagVertiv == True:
            print(timelogFunc() + ' [ERROR] ups monitoring back online')
            log.write(timelogFunc() + ' [ERROR] ups monitoring back online\n')
        if infoFlag == True:
            log.write(f'{timelogFunc()} [INFO] ac-connected:{isAcPresent}; is-charging:{isCharging}; load:{percentLoad}%; runtime-till-empty:{runTimeToEmpty}s')
        if isAcPresent == False:
            timeToShutdown = (runTimeToEmpty - runTimeLeft)
            print(timelogFunc() + ' [WARNING] ac lost, shutdown in ', timeToShutdown,' seconds')
            log.write(timelogFunc() + ' [WARNING] ac lost, shutdown in ', timeToShutdown,' seconds\n')
            if runTimeToEmpty < runTimeLeft:
                    print(timelogFunc() + ' [ALERT] shutdown now')
                    log.write(timelogFunc() + ' [ALERT] shutdown now\n')
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(sshHost, port, username, password)
                    #stdin, stdout, stderr = ssh.exec_command('/sbin/shutdown.sh && /sbin/poweroff')
                    stdin, stdout, stderr = ssh.exec_command('ls')
                    shutdownFlag = True
    else:
        print(timelogFunc() + ' [ERROR] ups monitoring error')
        log.write(timelogFunc() + ' [ERROR] ups monitoring error\n')
        lastErrorFlagSSH = errorFlagSSH
        lastErrorFlagVertiv = errorFlagVertiv
    log.close()

def testFunc():
    print(timelogFunc() + ' [DEBUG] running testmode')
    try:
        requests.get('http://' + vertivHost + ':8210/api/PowerAssist', timeout=1)
    except requests.exceptions.ConnectionError:
        print(timelogFunc() + ' [ERROR] powerassist host unavailable')
    response = os.system("ping -c 1 " + sshHost + '>/dev/null')
    if response == 0:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sshHost, port, username, password)
        stdin, stdout, stderr = ssh.exec_command('ls')
        outlines=stdout.readlines()
        resp=''.join(outlines)
        print(resp)
        print('ls command executed, check output above')
    else:
        print(timelogFunc() + ' [ERROR] ssh host unavailable')
    sys.exit()

### START LOOP ###
if testFlag == True:
    testFunc()
print(timelogFunc() + ' [INFO] ups daemon started, see log for further information')
while shutdownFlag == False:
    timeFunc() # dirty cron like function
    if timeHour != lasttimeHour: # run activeFunc() every hour
        lasttimeHour = timeHour
        activeFunc()
    if timeMinute != lasttimeMinute: # run upsmonitorFunc() every minute
        lasttimeMinute = timeMinute
        upsmonitorFunc()
    time.sleep(1)
