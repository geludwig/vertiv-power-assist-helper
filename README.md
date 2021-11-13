# VertivPowerAssistScript
This shell script will monitor a running VERTIV PowerAssist instance via its API.

The API of a running VERTIV Power Assist instance is available via <ip>:8210/api/PowerAssist.
  
The script will monitor if AC is present or lost and will initiate a command after a specified shutdown time has passed. In the provided script it will ssh to a running ESXi host and inits a shutdown.
  
This is a shell and must therefore be run in foreground or has to be used with "screen".
