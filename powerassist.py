# MODULES
import requests
from time import gmtime, strftime, sleep
import paramiko

# VARIABLES
shutdownFlag = False
runTimeLeft = 900 #runtime left till empty
testMode = False # test ssh connection with simple 'ls'

# SSH
host = 'url/ip'
port = 22
username = "usr"
password = "pw"

# GLOBAL FUNCTION
def timestamp():
    global timestamp
    timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return timestamp

# TEST MODE
if testMode == True:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('ls')
    outlines=stdout.readlines()
    resp=''.join(outlines)
    print(resp)
    exit()

# UPS MONITORING
print(timestamp(), '[NOTICE] ups monitoring started')
while shutdownFlag == False:
    
# WEB REQUEST
    url = 'http://<url/ip>:8210/api/PowerAssist'
    response = requests.get(url)
    if response.status_code != 200: 
        print(timestamp(), '[ERROR] web request error with status:', response.status_code)
    jsondict = response.json()

# PARSE JSON
    acPresent = (jsondict[0]['status']['isAcPresent'])
    timeTillEmpty = (jsondict[0]['status']['runTimeToEmptyInSeconds'])    

# ACTIONS
    if acPresent == False:
        timeToShutdown = (timeTillEmpty - runTimeLeft)
        print(timestamp(), '[WARNING] ac lost. shutdown in ', timeToShutdown,' seconds')
        if timeTillEmpty < runTimeLeft:
            print[timestamp(), '[ALERT] shutdown now']
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)
            stdin, stdout, stderr = ssh.exec_command('/sbin/shutdown.sh && /sbin/poweroff')
            shutdownFlag = True
    sleep(5)