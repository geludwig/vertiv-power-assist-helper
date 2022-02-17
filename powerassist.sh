#!/bin/bash

########################################
# THIS SCRIPT IS OBSOLETE - DO NOT USE #
########################################

# VARIABLES
shutTime=600 # time from ac lost to shutdown
j=0
timer=0
enableTimer=0
initTime=0

# GLOBAL FUNCTIONS
timestamp() {
	# date +"%T" # old current time
	printf '%(%Y-%m-%d %H:%M:%S)T\n' -1
}

# BEGIN
echo " "
echo $(timestamp) "[INFO] UPS MONITORING STARTED"
echo $(timestamp) "[INFO] UPS MONITORING STARTED" >> log.txt

# BEGIN LOOP
while [ $j -eq 0 ]; do

# CHECK CONDITIONS
	wget -q -t 1 -T 2 -O PowerAssist "http://<ip_vertivpowerassist>:8210/api/PowerAssist"
	httpStat=$?
	
	if [ $httpStat -ne 0 ] && [ $enableTimer -eq 0 ]; then
		shutdown=1
		echo $(timestamp) "[ERROR] UPS SERVER UNREACHABLE"
		echo $(timestamp) "[ERROR] UPS SERVER UNREACHABLE" >> log.txt
		
	elif  [ $httpStat -ne 0 ] && [ $enableTimer -eq 1 ]; then
		shutdown=1
	else
		acpresent=$(grep -c '"isAcPresent":true' PowerAssist)
			if [ $acpresent -eq 0 -a $enableTimer -eq 0 ]; then
				shutdown=1
				echo $(timestamp) "[ALERT] AC LOST"
				echo $(timestamp) "[ALERT] AC LOST" >> log.txt
			elif [ $acpresent -eq 0 -a $enableTimer -eq 1 ]; then
				shutdown=1;
			else
				shutdown=0
			fi
	fi
	
# SHUTDOWN SEQUENCE	
	if [ $shutdown -eq 1 -a $enableTimer -eq 0 ]; then
		enableTimer=1
		initTime=$SECONDS
		echo $(timestamp) "[ALERT] SHUTDOWN IN ${shutTime} SECONDS"
		echo $(timestamp) "[ALERT] SHUTDOWN IN ${shutTime} SECONDS" >> log.txt

	elif [ $shutdown -eq 0 -a $enableTimer -eq 1 ]; then
		enableTimer=0
		timer=0
		initTime=0
		echo $(timestamp) "[INFO] UPS BACK ONLINE"
		echo $(timestamp) "[INFO] UPS BACK ONLINE" >> log.txt
	
	elif [ $shutdown -eq 1 -a $enableTimer -eq 1 ]; then
		timer=$(( (initTime+shutTime) - $SECONDS  ))
		if [ $timer -le 60 ]; then
			echo $(timestamp) "[ALERT] SHUTDOWN IN ${timer} SECONDS"
			echo $(timestamp) "[ALERT] SHUTDOWN IN ${timer} SECONDS" >> log.txt
		fi
		
		if [ $timer -le 0 ]; then
			j=1
			echo $(timestamp) "[CRITICAL] SHUTDOWN NOW"
			echo $(timestamp) "[CRITICAL] SHUTDOWN NOW" >> log.txt
#			sshpass -p <password> ssh -o StrictHostKeyChecking=no root@<esxihost> '/sbin/shutdown.sh && /sbin/poweroff'
		fi
	else
		true
		#echo "AC OK"
	fi	

	sleep 10
	
done
