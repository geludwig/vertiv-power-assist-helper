# VertivPowerAssistScript
This shell script will monitor a running VERTIV PowerAssist instance.

The API of a running VERTIV Power Assist instance is available via http://<IP>:8210/api/PowerAssist.
  
The script will monitor if AC is present or lost and will initiate a (ssh) command when the remaining runtime of the ups is smaller than a specified value. In the provided script it will ssh to a running ESXi host and inits a shutdown.

### REQUIREMENTS
SYSTEM: Ubuntu Server 20.04 (Focal Fossa)
UPS: Vertiv Edge (USB)
Tested unsuccessful on Ubuntu Server 22.04 and Raspberry Pi B+ (Raspberry OS Lite). Needs investigation.

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

This is a python script and must therefore be run in foreground or has to be used with "screen". Please take note which modules are required and install if needed.
