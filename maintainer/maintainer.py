import logging
import configuration
from time import sleep
from channels import ChannelsMaintanance


def main():
    maintenance = ChannelsMaintanance(7)
    while True:
        maintenance.channels_to_quarantine()
        maintenance.delete_children()
        maintenance.delete_parents()
        time.sleep(180)


if __name__ == "__main__":
    main()
