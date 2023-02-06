from BasicPackage.basic_func import *
import gce
import time
import threading
import c_rcon
import random

vacations = ["23 03 01", "23 05 05", "23 05 27", "23 06 06", "23 08 15", "23 09 28", "23 09 29", "23 09 30", "23 10 03",
             "23 10 09", "23 12 25"]

config_path = "/rust-ds-scheduler-config/config.cfg"

GCE_ID = get_config(config_path, "GCE_ID")
GCE_PW = get_config(config_path, "GCE_PW")
GCE_PR = get_config(config_path, "GCE_PR")

gce_driver = gce.get_driver(GCE_ID, GCE_PW, GCE_PR)
the_node = gce.get_node(gce_driver, "rust-ds-with-wlb")

item_mode = True if get_config(config_path, "ITEM_MODE_ACTIVATED") == "true" else False
if get_config(config_path, "ITEM_MODE_ACTIVATED") == "true":
    print("Item Mode Activated")
else:
    print("Item Mode Deactivated")
flag_server_on = True if str(the_node.state) == "running" else False
if str(the_node.state) == "running" :
    print("The DS is already running")

schedule_timer_indicator = 0
item_timer_indicator = 0

flag_15 = False
flag_30 = False
flag_45 = False
flag_00 = False

workbench_tier1 = []
workbench_tier2 = []
workbench_tier3 = []
with open("/rust-ds-scheduler-config/workbench/tier1") as f:
    workbench_tier1 = f.read().splitlines()
with open("/rust-ds-scheduler-config/workbench/tier2") as f:
    workbench_tier2 = f.read().splitlines()
with open("/rust-ds-scheduler-config/workbench/tier3") as f:
    workbench_tier3 = f.read().splitlines()


def give_item(workbench: list, many: int):
    item = "inventory.giveall " + random.choice(workbench) + " " + str(many)
    c_rcon.send_rcon(item)
    print(item)


def send_item():
    global workbench_tier1
    global workbench_tier2
    global workbench_tier3
    global flag_15
    global flag_30
    global flag_45
    global flag_00
    global item_timer_indicator
    item_timer_indicator += 5

    if not flag_00 and str(time.strftime("%H %M")) == "00 00":
        flag_15 = False
        flag_30 = False
        flag_45 = False
        flag_00 = True
        give_item(workbench_tier3, 1)
    elif not flag_00 and int(time.strftime("%M")) == 0:
        flag_15 = False
        flag_30 = False
        flag_45 = False
        flag_00 = True
        give_item(workbench_tier2, 1)
    elif not flag_15 and int(time.strftime("%M")) == 15:
        flag_15 = True
        flag_00 = False
        give_item(workbench_tier1, 2)
    elif not flag_30 and int(time.strftime("%M")) == 30:
        flag_30 = True
        give_item(workbench_tier1, 2)
    elif not flag_45 and int(time.strftime("%M")) == 45:
        flag_45 = True
        give_item(workbench_tier1, 2)

    if item_timer_indicator > 3600:
        item_timer_indicator = 0
        print("Item Checked")
    threading.Timer(5, send_item).start()


def start_node():
    global flag_server_on
    global gce_driver
    global the_node

    flag_server_on = True
    gce_driver.start_node(the_node)
    print("Server Started")


def stop_node():
    global flag_server_on
    global gce_driver
    global the_node
    flag_server_on = False
    c_rcon.send_rcon("server.writecfg")
    time.sleep(5)
    c_rcon.send_rcon("server.save")
    time.sleep(5)
    c_rcon.send_rcon("global.quit")
    time.sleep(60)
    gce_driver.stop_node(the_node)


def do_schedule():
    global gce_driver
    global flag_server_on
    global the_node
    global schedule_timer_indicator

    schedule_timer_indicator += 5
    t_day = str(time.strftime("%A")).lower()

    if not flag_server_on and t_day == "friday" and int(time.strftime("%H")) == 15:
        start_node()
    elif not flag_server_on and int(time.strftime("%H")) == 18:
        start_node()

    if flag_server_on and int(time.strftime("%H")) == 2:
        # 공휴일이 아니며
        print("1")
        if not str(time.strftime("%y %m %d")) in vacations:
            print("2")
            # 토요일이나 일요일도 아니라면
            if not (t_day == "saturday" or t_day == "sunday"):
                print("3")
                stop_node()

    if schedule_timer_indicator > 3600:
        schedule_timer_indicator = 0
        print("Timer Checked")
    threading.Timer(5, do_schedule).start()


threading.Timer(5, do_schedule).start()
if item_mode:
    threading.Timer(5, send_item).start()
