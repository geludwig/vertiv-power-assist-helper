# MODULES
import requests
import os
import paramiko
import schedule
from sys import exit
from time import gmtime, strftime, sleep

# USER DEFINDED VARIABLES
runTimeLeft = 900 # runtime left before shutdown in seconds
testMode = False # test ssh and powerassist connection
vertivHost = '<url/ip>'
sshHost = '<url/ip>'
port = 22
username = '<usr>'
password = '<pw>'

# VARIABLES
shutdownFlag = False
initialFlag = True
errorFlagSSH = True
errorFlagVertiv = True

# GLOBAL FUNCTIONS
def timestamp():
    global currTime
    currTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return currTime

def lifeSignal():
    log.write(timestamp() + ' [INFO] ups monitoring active')

# TEST MODE
if testMode == True:
    # POWER ASSIST API
    try:
        requests.get('http://' + vertivHost + ':8210/api/PowerAssist', timeout=1)
    except requests.exceptions.ConnectionError:
        print(timestamp() + ' [ERROR] powerassist host unavailable')
    # SSH
    response = os.system('ping -c 1 ' + sshHost)
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
        print(timestamp() + ' [ERROR] ssh host unavailable')
    exit()

# OPEN LOG
log = open("log.txt", "a")

# UPS MONITORING
while shutdownFlag == False:
    # SIGN OF LIFE SIGNAL
    schedule.every().day.at("00:00").do(lifeSignal)

    # POWER ASSIST API
    try:
        response = requests.get('http://' + vertivHost + ':8210/api/PowerAssist', timeout=1)
    except requests.exceptions.ConnectionError:
        log.write(timestamp() + ' [ERROR] powerassist host unavailable\n')
        errorFlagVertiv = True
    else:
        jsondict = response.json()
        acPresent = (jsondict[0]['status']['isAcPresent'])
        timeTillEmpty = (jsondict[0]['status']['runTimeToEmptyInSeconds'])
        errorFlagVertiv = False

    # SSH
    response = os.system('ping -c 1 ' + sshHost + '>/dev/null')
    if response != 0:
        log.write(timestamp() + ' [ERROR] ssh host unavailable\n')
        errorFlagSSH = True
    else:
        errorFlagSSH = False

    # ACTIONS
    if errorFlagSSH==False and errorFlagVertiv==False:
        if initialFlag == True:
            initialFlag = False
            print(timestamp() + ' [INFO] ups monitoring started, see log')
            log.write(timestamp() + ' [INFO] ups monitoring started\n')
        if acPresent == False:
            timeToShutdown = (timeTillEmpty - runTimeLeft)
            log.write(timestamp() + ' [WARNING] ac lost. shutdown in ', timeToShutdown,' seconds\n')
            if timeTillEmpty < runTimeLeft:
                log.write[timestamp() + ' [ALERT] shutdown now\n']
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(sshHost, port, username, password)
                stdin, stdout, stderr = ssh.exec_command('/sbin/shutdown.sh && /sbin/poweroff')
                shutdownFlag = True
                log.close()
    else:
        print(timestamp() + ' [ERROR] ups monitoring disabled, see log')
        log.write(timestamp() + ' [ERROR] ups monitoring disabled\n')

    log.flush()
    sleep(30)
