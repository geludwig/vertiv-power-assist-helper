# VertivPowerAssistScript
This shell script will monitor a running VERTIV PowerAssist instance via its API.

The API of a running VERTIV Power Assist instance is available via IP:8210/api/PowerAssist.
  
The script will monitor if AC is present or lost and will initiate a command after the runtime-left of the ups is smaller than a specified value. In the provided script it will ssh to a running ESXi host and inits a shutdown.
  
This is a python script and must therefore be run in foreground or has to be used with "screen". Please take note which modules are required and install if needed.
