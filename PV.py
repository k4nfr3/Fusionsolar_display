from fusionsolar import Client, PandasClient
import pandas as pd
from prettytable import PrettyTable
from datetime import datetime
import time
import logging
import sys
import os
from waveshare_epd import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont
import traceback
import requests
import urllib3
import socket
import fcntl
import struct

log_level = logging.DEBUG

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}
proxies = "" # comment out this line to go through the Burp Proxy. I've used for debugging purpose
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

last_batt = 0


try:
    from _pv_conf import pv_host
except ImportError:
    try:
        from _pv_conf import pv_host
    except ImportError:
        logger.error("You should copy or rename _pv_conf_example.py to my_pv_conf.py and fill it with your actual data!")
        logger.error(sys.exc_info())
        exit()

def get_ip_address(interface: str) -> str:
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Use ioctl to get the IP address for the given interface
        ip_address = fcntl.ioctl(
            sock.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(interface[:15], 'utf-8'))
        )[20:24]
        # Convert the binary IP to a readable string
        logger.debug("Returning IP for interface : " + str(interface) + " " + str(socket.inet_ntoa(ip_address)))
        return socket.inet_ntoa(ip_address)
    except OSError as e:
        # Specifically return None if the interface has no IP address
        if e.errno == 99:  # ENONET or a similar errno indicating no IP
            logger.error("Error #99 No IP returning IP for interface : " + str(interface))
            return None
        if e.errno == 19:  # ENONET or a similar errno indicating no IP
            logger.error("Error #19 No such interface : " + str(interface))
            return None
        else:
            raise  # Re-raise unexpected errors
    else:
        # For other unexpected exceptions
        logger.error("Error returning IP for interface : " + str(interface))
        return None

def setup_logger(log_level):
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Clear any existing handlers (if the function is called multiple times)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the log level based on the input
    logger.setLevel(log_level)

    # Create handlers (console and file)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('/var/log/PV.log')

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_data():
    battery_device = client.get_dev_kpi_real(pv_host.battery, 39)
    if battery_device['success']:
        battery_level=battery_device['data'][0]['dataItemMap']['battery_soc']
    else :
        battery_level="0"
        logger.error("Error getting data" + str(battery_device['data']))

    inverter_device = client.get_dev_kpi_real(pv_host.inverter, 1)
    if inverter_device['success']:
        inverter_power=inverter_device['data'][0]['dataItemMap']['mppt_power']
        day_power=inverter_device['data'][0]['dataItemMap']['day_cap']

    else :
        inverter_power="0"
        day_power="0"
        logger.error("Error getting data" + str(inverter_power['data']))

    return  battery_level,  inverter_power, day_power

def print_device_list(station_code):
    dl = client.get_dev_list(station_code=station_code)
    table = PrettyTable()
    table.field_names = ['devName', 'softwareVersion', 'SN', 'devTypeId','id']
    table.align = 'c'
    for device in dl['data']:
        table.add_row([device['devName'], device['softwareVersion'],device['esnCode'],device['devTypeId'],device['id']])
    logger.info(table)


def print_station_code():
    sl = client.get_station_list()
    station_code = sl['data'][0]['stationCode']
    logger.info("station_code = " + str(station_code))
    return station_code


def epaper_init():
    epd = epd2in13_V4.EPD()
    epd.init()


def epaper_booting():
    logger.debug("epaper_booting()")
    epd = epd2in13_V4.EPD()
    epd.Clear(0xFF)
    picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

    draw = ImageDraw.Draw(image)
    draw.text((40, 10), 'No data yet', font=font24, fill=0)
    draw.text((40, 40), time.strftime('%H:%M', time.localtime()), font=font24, fill=0)
    wlan0_ip = get_ip_address("wlan0")
    eth0_ip = get_ip_address("eth0")
    draw.text((40, 70), 'WLAN0 :'+ str(wlan0_ip), font=font16, fill=0)
    draw.text((40, 90), 'ETH0 :'+ str(eth0_ip), font=font16, fill=0)
    rotated_image = image.rotate(180, expand=True)  # Expand=True adjusts the canvas size if needed
    epd.display(epd.getbuffer(rotated_image))


def epaper_display(batt, power, day_power):
    logger.debug("epaper_display()")
    global last_batt # access variable
    epd = epd2in13_V4.EPD()
    epd.Clear(0xFF)
    picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
    libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

    font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
    font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font20 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)


    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    draw.rectangle([(100, 18), (103, 33)], fill=0)
    draw.rectangle([(10, 0), (97, 50)], fill=0)
    draw.rectangle([(13, 3), (94, 47)], fill=1)
    if batt >= 6:
        draw.rectangle([(16, 6), (26, 44)], fill=0)
    if batt >= 20:
        draw.rectangle([(29, 6), (39, 44)], fill=0)
    if batt >= 40:
        draw.rectangle([(42, 6), (52, 44)], fill=0)
    if batt >= 60:
        draw.rectangle([(55, 6), (65, 44)], fill=0)
    if batt >= 80:
        draw.rectangle([(68, 6), (78, 44)], fill=0)
    if batt >= 95:
        draw.rectangle([(81, 6), (91, 44)], fill=0)
    draw.text((125, 10), str(batt) + '%', font=font24, fill=0)
    if ((last_batt != 0) and (last_batt < batt)):
        draw.text((145, 10), "-", font=font24, fill=0)
    elif ((last_batt != 0 ) and (last_batt > batt)):
        draw.text((145, 10), "+", font=font24, fill=0)
    last_batt = batt
    draw.text((90, 60), "Now :", font=font24, fill=0)
    draw.text((160, 60), "{:.2f} KW".format(power), font=font24, fill=0)
    draw.text((90, 80), "Day  :", font=font24, fill=0)
    draw.text((160, 80), "{:.2f} KW".format(day_power), font=font24, fill=0)
    draw.text((10, 70), time.strftime('%H:%M', time.localtime()), font=font20, fill=0)
    wlan0_ip = get_ip_address("wlan0")
    if wlan0_ip is None:	
        eth0_ip = get_ip_address("eth0")
        draw.text((10, 102), str(eth0_ip), font=font15, fill=0)
    else :
        draw.text((10, 102), str(wlan0_ip), font=font15, fill=0)
    rotated_image = image.rotate(180, expand=True)  # Expand=True adjusts the canvas size if needed
    epd.display(epd.getbuffer(rotated_image))


# Main
logger = setup_logger(log_level) # let's create the debugger


epaper_init()
epaper_booting()
time.sleep(20) # let's wait 20sec 

with PandasClient(user_name=pv_host.user, system_code=pv_host.password) as client:

    # token validity is : 30mins so if sleep is less than 30min, then no need to relogin

    station_code = pv_host.station 
    if station_code=="":
        print("Let's wait 20sec")
        station_code = print_station_code() # uncomment if you need to get the code
        print_device_list(station_code) # uncomment if you need to get the device list
        print("Copy those values to your configuration file ! ")
        sys.exit(0)


    table_history = PrettyTable()
    table_history.field_names = ['Timestamp', 'Battery [%]', 'power [KW]']
    table_history.align = 'c'

    while True:
        now = datetime.now()
        battery_level, inverter_power, day_power = get_data()
        formatted_time = now.strftime("%d/%m/%Y %H:%M")
        table_history.add_row([formatted_time,battery_level, inverter_power])
        if len(table_history.rows) >= 10:
            table_history.del_row(0)
        print(table_history)
        print("Length : " + str(len(table_history.rows)))
        epaper_display(battery_level,inverter_power,day_power )
        time.sleep(300)  # let's wait another xxx seconds before next poll

