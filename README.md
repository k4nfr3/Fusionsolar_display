# Little Raspberry Pi to dsiplay Huawei FusionSolar Battery status and day stats
![box](./waveshare_display.jpeg?raw=true "Little Raspberry Pi Zero + Waveshare 2´´13")

## Estimated price 23.- CHF
Around 25$
I've found this one : [www.berrybase.ch](https://www.berrybase.ch/waveshare-2-13-e-paper-display-fuer-raspberry-pi-zero-5-punkt-touch-250-122-pixel-abs-gehaeuse)

## Northbound API
To get the data, create a API account
[Huawei Forum on how to](https://forum.huawei.com/enterprise/intl/en/thread/how-to-create-a-api-account/671733393529913344?blogId=671733393529913344)

# Installation steps
## Step 1, generate a new Rasbperry OS on the SD card
see other forums on how to

## Step 2, clone waveshare SDK
git clone https://github.com/waveshareteam/e-Paper

## Step 3, clone my script
git clone https://github.com/k4nfr3/Fusionsolar_display
cd Fusionsolar_display
cp * /home/admin/e-Paper/RaspberryPi_JetsonNano/python/examples
cd /home/admin/e-Paper/RaspberryPi_JetsonNano/python/examples

## Step 4, install required python modules

## Step 5 , enter API details
change the details in file : pv_conf.ini

## Step 6, get station_code and device_code
uncomment lines 222 and 226 and run the python script

## Step 7, modify ini file with the correct IDs to be interrogated

## Step 8, create autoboot service

## Step 9, add crontab tasks
