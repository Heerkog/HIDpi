from hidpi.service import BTHIDService
import os
import sys


if __name__ == '__main__':
    if not os.geteuid() == 0:
        sys.exit("Only root can run this script")

    myservice = BTHIDService()
