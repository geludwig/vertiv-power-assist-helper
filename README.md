# Vertiv PowerAssist for Linux
- This shell script will monitor a running VERTIV PowerAssist instance via USB.

- When AC is lost it initiates a (ssh) command, when the remaining runtime of the ups is smaller than a specified value. In the provided script it will ssh to a running ESXi host and inits a shutdown.

### REQUIREMENTS
- SYSTEM: Ubuntu Server 20.04 (more recent versions may not be supported by Vertiv)
- UPS: Vertiv Edge (USB)

### INSTALLATION
1) Get PowerAssist.deb
```
wget "https://downloads1.vertivco.com/Trellis/Power%20Assist/v1.35%20Windows%20v1.25%20Linux%20August%202021/Power%20Assist%20Linux%201.25.zip"
```
  
2) Install
```
sudo apt install ./Powerassist.deb
```

3) Install default-jre if required
```
sudo apt install default-jre
```
  
4) Check status
```
systemctl status ups.monitoringservice.service
```
  
5) Check webpage
```
http://<ip>:8210/api/PowerAssist
```

### STANDALONE SCRIPT
This is a python script and must therefore be run in foreground or has to be used with "screen". Please take note which modules are required and install if needed.

1) Copy "powerassist.py" and "start_powerassist.sh" into desired folder
2) Edit "start_powerassist.sh" and add correct folder path
```
sudo nano start_powerassist.sh
```
3) Make bash executable
```
sudo chmod +x start_powerassist.sh
```
4) Start "start_powerassist.sh"
```
sudo ./start_powerassist.sh
```
5) Resume to screen
```
sudo screen -r powerassist
```
6) Exit screen
```
KEY COMBO: STRG + A + D
```

### CRONJOB SCRIPT
1) Add cronjob (without sudo)
```
crontab -e
```
2) Add following syntax (replace PATH with the actual path of the script) and save
```
* * * * * $(which python3) /<PATH>/powerassist_cron.py >> /<PATH>/powerassist.log 2>&1
```
3) Setting the testFlag variable inside the powerassist_cron.py script to True should add some output to the log file.
