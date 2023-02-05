from BasicPackage.basic_func import *
from rcon.source import Client

config_path = "/rust-ds-scheduler/config/config.cfg"

DSWWLB_IP = get_config(config_path, "DSWWLB_IP")
DSWWLB_RCON_PORT = get_config(config_path, "DSWWLB_RCON_PORT")
DSWWLB_RCON_PWD = get_config(config_path, "DSWWLB_RCON_PWD")

def send_rcon(command: str):
    try :
        with Client(DSWWLB_IP, int(DSWWLB_RCON_PORT), passwd=DSWWLB_RCON_PWD) as client:
            response = client.run(command)
            # print(response)
    except Exception as e:
        pass