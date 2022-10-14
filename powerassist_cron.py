### MODULES ###
try:
    import requests
    import os
    import paramiko
    import subprocess
    import time
except ModuleNotFoundError as err:
    print(err, ". Install with 'pip' first!")
    exit()

### VARIABLES ###
deltaTime = 900             # ups runtime left before shutdown in seconds, keep in mind that cron intervall must be smaller than deltaTime
testFlag = False            # shutdown command will not be sent if set to True, instead 'ls' command is sent to test ssh connection
vertivHost = '<ip/url>'     # for example '192.168.200.1'
sshHost = '<ip/url>'        # for example '192.168.200.40'
username = '<usr ssh>'      # for example 'root'
password = '<pw ssh>'
port = 22

### FUNCTIONS ###
def timeFunc():
    global currentTime
    currentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    return currentTime

def activeFunc():
    global hourTime
    hourTime = time.strftime('%H%M', time.gmtime())
    return hourTime

def upsFunc():
    # TEST POWER ASSIST API AVAILABILITY
    try:
        responseVertiv = requests.get('http://' + vertivHost + ':8210/api/PowerAssist', timeout=1)
    except requests.exceptions.Timeout:
        print(timeFunc() + ' [ERROR] powerassist request timeout')
        errorVertiv = True
    except requests.exceptions.RequestException:
        print(timeFunc() + ' [ERROR] powerassist request error')
        errorVertiv = True        
    else:
        jsondict = responseVertiv.json()
        isAcPresent = (jsondict[0]['status']['isAcPresent'])
        runTimeToEmpty = (jsondict[0]['status']['runTimeToEmptyInSeconds'])
        errorVertiv = False
    # TEST SSH AVAILABILITY
    with open(os.devnull, 'w') as DEVNULL:
        try:
            subprocess.check_call(
            ['ping', '-c', '1', sshHost],
            stdout=DEVNULL,  # suppress output
            stderr=DEVNULL
            )
            errorSsh = False
        except subprocess.CalledProcessError:
            print(timeFunc() + ' [ERROR] ssh request error\n')
            errorSsh = True
    # ACTIONS
    if errorSsh == False and errorVertiv == False:
        if isAcPresent == False:
            timeToShutdown = (runTimeToEmpty - deltaTime)
            print(timeFunc() + ' [WARNING] ac lost, shutdown in ', timeToShutdown,' seconds')
            if runTimeToEmpty < deltaTime:
                    print(timeFunc() + ' [ALERT] shutdown now')
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(sshHost, port, username, password)
                    stdin, stdout, stderr = ssh.exec_command('/sbin/shutdown.sh && /sbin/poweroff')
        else:
            activeTime = activeFunc()
            if activeTime == "1200":
                print(timeFunc() + ' [INFO] powerassist active')

    # ACTIONS TESTMODE
    if testFlag == True:
        print(timeFunc() + ' [DEBUG] testmode active, see output for response')
        if errorSsh == False and errorVertiv == False:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(sshHost, port, username, password)
            stdin, stdout, stderr = ssh.exec_command('ls')
            outlines=stdout.readlines()
            resp=''.join(outlines)
            print(resp)

### CALLER ###
upsFunc()
