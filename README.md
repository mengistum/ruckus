# Network automation scripts - written for Ruckus SCG200

SUMMARY: This script runs different change commands to the Ruckus controller and Access Points which are controlled by the controller. 

WHAT YOU WILL NEED: You can download and use these codes for Ruckus controllers running version 3.5. Here is the list of files you will need:

- mm\_common\_funcs.py ==> contains functions which are common for the rest of the scripts

- mm\_ruckus.py ==> a class contains all the attributes and methods needed to create a ruckus object.

- mm\_ruckus\_auth\_modify.py ==> a script to change the 802.1X authentication servers on each zone in the controller.

- mm\_ruckus\_ap\_login\_modify.py ==> a script to change the AP Login for each AP controlled by the Controller.

- mm\_ruckus\_channelfly\_modify.py ==> a script to change the ChannelFly setup on each zone in the controller. 


REQUIREMENTS: This script was written and run using the following:
			python 3.8.7
			requests
			

USAGE: 
1) If you want it to run on Windows OS, Mac OS, or Linux OS, please install all packages listed under REQUIREMENTS section. Run the script of your choice and follow the prompts.

2) You can also run it on a DOCKER environment. Please pull the container to your docker environment as follows: "docker pull useth2020/ruckus-scg200" without the quotation marks. Then, "run docker run -ti useth2020/ruckus-scg200:latest" without quotation marks, change directory to /src/ruckus (cd /src/ruckus); modify either commands\_show.txt and devices.txt files; and run "python3 <choice of your script>". You will be prompted to enter choices (whether to turn ON/OFF ChannelFly, turn ON BackgroundScanning; on which Channel to work on 2.4/5/both), enter what you want to do, and enter your SSH username and password.


OUTPUT: If you enter correct information, the result will be written to a file.
