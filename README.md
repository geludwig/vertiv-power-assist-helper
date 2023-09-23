# Vertiv PowerAssist Helper Script
- This python script monitors a Vertiv UPS connected via USB. When AC is lost the script initiates a (custom) ssh command, when the remaining runtime of the ups is smaller than a specified value. In the provided script it connects to a ESXi host via ssh and inits a shutdown.
- The installation guide is for linux only, but the python script is written for linux and windows.

- Release Notes:
```
https://downloads1.vertivco.com/Trellis/Power%20Assist/v1.4/Vertiv%20Power%20Assist%20Release%20Notes%20v1.4_VERTIV.pdf
```

### REQUIREMENTS
- OS: Tested on Ubunu 22.04 LTS Server (headless)
- UPS: Vertiv Edge (USB)

### INSTALLATION
1) Get PowerAssist_Linux_1.4.0.zip
```
wget "https://downloads1.vertivco.com/Trellis/Power%20Assist/v1.4/PowerAssist_Linux_1.4.0.zip"
```

2) Unzip
```
unzip PowerAssist_Linux_1.4.0.zip
```

3) Install
```
sudo apt install ./PowerAssist_1.4.0_amd64.deb
```

4) Install default-jre if required
```
sudo apt install default-jre
```
  
5) Check status
```
systemctl status ups.monitoringservice.service
```
  
6) Check webpage
```
http://<ip of host>:8210/api/PowerAssist
```

### CRONJOB SCRIPT
1) Add cronjob (without sudo).
```
crontab -e
```
2) Add following syntax (replace PATH with the actual path of the script) and save. Here the script is executed every 1 minute. A lower polling rate should be avoided.
```
* * * * * $(which python3) /<PATH>/powerassist_cron.py >> /<PATH>/powerassist.log 2>&1
```
3) Setting the DEBUG variable in powerassist_cron.py to "True" should add some output to the log file. Change to False after testing.


### PARAMETERS
Set the appropriate parameters inside the python script. Make sure to set "DEBUG" to "False" after testing.
```
DEBUG = True
MINIMUMRUNTIMELEFT = 900    # minimum runtime left in seconds
VERTIVIP = 'ip'
SSHIP = 'ip'
SSHUSER = 'user'
SSHPASSW = 'pw'
SSHPORT = 22
```
