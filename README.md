# Little Raspberry Pi to dsiplay Huawei FusionSolar Battery status and day stats
![box](./waveshare_display.jpeg?raw=true "Little Raspberry Pi Zero + Waveshare 2´´13")

## Estimated price 23.- CHF
Cost is around 25$
I've found this one : [www.berrybase.ch](https://www.berrybase.ch/waveshare-2-13-e-paper-display-fuer-raspberry-pi-zero-5-punkt-touch-250-122-pixel-abs-gehaeuse)  

![box2](./waveshare_display2.jpg?raw=true "Fairly cheap box for the job")

## Northbound API
To get the data, create a API account  
[Huawei Forum on how to](https://forum.huawei.com/enterprise/intl/en/thread/how-to-create-a-api-account/671733393529913344?blogId=671733393529913344)

# Installation steps
## Step 1, generate a new Rasbperry OS on the SD card
see other forums on how to

[raspberry pi download](https://www.raspberrypi.com/software/operating-systems/)

## Step 2, clone waveshare SDK
cd /home/admin  
git clone https://github.com/waveshareteam/e-Paper

## Step 3, clone my script
git clone https://github.com/k4nfr3/Fusionsolar_display  
cd Fusionsolar_display  
cp *.py /home/admin/e-Paper/RaspberryPi_JetsonNano/python/examples  
cd /home/admin/e-Paper/RaspberryPi_JetsonNano/python/examples  

## Step 4, clone fusionsolar python client
git clone https://github.com/EnergieID/FusionSolar  

## Step 4, install required python modules
- pandas
- PIL
- requests
- urllib3
- socket
  
## Step 5 , enter API details
change the details in file : pv_conf.ini  
Fill-in user and password  

## Step 6, get station_code and device_code
run manually the script :
python PV.py  
It should test the screen and connect with the Northbound API.
It will show you the devices you have access.

## Step 7, modify ini file with the correct IDs to be interrogated
Add the missing information in the config file :
- Add the Battery ID  (for example : battery=100000000001561112)
- Add the Inverter ID (for example : inverter=10000000001551111)
- Add the StationCode (for example : station="NE-12345678")
  
## Step 8, test the script and see if you see the correct data on the screen
python PV.py

## Step 9, transform the script into a PV service
cp /home/admin/FusionSolar_display/PV.service /usr/lib/systemd/system/PV.service  
chmod 644 /usr/lib/systemd/system/PV.service  
systemctl enable PV.service  

## Step 9, add crontab tasks if you want to restart the service daily the service
# m h  dom mon dow   command  
59 3 * * * /usr/sbin/service PV stop
0 3 * * * /usr/sbin/service PV start

# Tips
## Script Log file will be written 
tail -f /var/log/PV.log  

## Wifi SSHd not working ?
Add the following to /etc/ssh/sshd_config  
  IPQoS cs0 cs0
