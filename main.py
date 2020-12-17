from main.switcher import Switcher
from ota_update.main.ota_updater import OTAUpdater
import config

def download_and_install_update_if_available():
    o = OTAUpdater(config.GIT_URL)
    o.check_for_update_to_install_during_next_reboot()
    o.download_and_install_update_if_available(config.WIFI_SSID, config.WIFI_PWD)
    

def start():
    # main program
    sw = Switcher()
    sw.run()


def boot():
    # runs on boot to check for updates
    download_and_install_update_if_available()
    start()


boot()



