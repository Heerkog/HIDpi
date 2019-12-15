from hidpi.connect import bt
import time # Used for pausing the process


if __name__ == '__main__':
    adv = bt.Advertiser()
    adv.advertise()
    client = adv.accept()
    adv.disconnect(client)
    adv.close()