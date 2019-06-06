import argparse
import os
import sys
import time
import tarfile
import glob
import multiprocessing as mp
from ChromeTestLib import ChromeTestLib

import subprocess
import shlex
from collections import defaultdict
from scapy.all import srp, Ether, ARP, conf


p = mp.Pool(mp.cpu_count())


cwd = os.getcwd()
bin_location = cwd + "/latest"
print (bin_location)

test = ChromeTestLib()

def createFolders(absFolderPath):
    try:
        os.makedirs(absFolderPath)
        return True
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}".format(errno, strerror))
        sys.exit(1)
    except OSError as e:
        print ("Exception found!!!")
        print (e)
        sys.exit(1)

def find_and_return_latest_binaries(binaries_folder_location):
    d = dict()
    
    try:
        files_array = os.listdir(binaries_folder_location)
    except OSError as e:
        print (e)
        return False

    if not files_array or len(files_array) > 2:  #it should have max 2 files inside.
        return False

    for file in files_array:
        if file.endswith(".bin"):
            file_path = os.path.join(binaries_folder_location, file)
            print os.path.getsize(file_path)
            file_size = os.path.getsize(file_path)
            if 500000 < file_size < 600000:
                print ("ec file path is: ", file_path)
                abs_ec_image_path = file_path
                d["ec"] = abs_ec_image_path
            if 15000000 < file_size < 17000000:
                print ("cb file path is: ", file_path)
                abs_cb_image_path = file_path
                d["cb"] = abs_cb_image_path

    if not d:
        print ("cb/ec images are not copied to binaries folder.")
        return False
    else:
        return d

def FlashBinaries(dut_ip, cbImageSrc = "", ecImageSrc = ""):
    flashDict = dict()
    flashing_status = "FAIL"
    cbFlashStatus = False
    ecFlashStatus = False
    if cbImageSrc:
        cbImageDest = "/tmp/autoflashCB.bin"
        copy_cb = test.copy_file_from_host_to_dut(cbImageSrc, cbImageDest, dut_ip)
        cbCmd = "flashrom -p host -w " + cbImageDest
        cbCmd = "ls -l " + cbImageDest
        cbFlashStatus = test.run_command_to_check_non_zero_exit_status(cbCmd, dut_ip)

    if ecImageSrc:
        ecImageDest = "/tmp/autoflashEC.bin"
        copy_ec = test.copy_file_from_host_to_dut(ecImageSrc, ecImageDest, dut_ip)
        ecCmd = "flashrom -p ec -w " + ecImageDest
        ecCmd = "ls -l " + ecImageDest
        ecFlashStatus = test.run_command_to_check_non_zero_exit_status(ecCmd, dut_ip)
        if not ecFlashStatus:
            flashDict[dut_ip] = flashing_status
            resultDict.update(flashDict)
            return flashDict
    
    if cbFlashStatus or ecFlashStatus:
        # test.run_async_command("sleep 2; reboot > /dev/null 2>&1", dut_ip)
        print("")
        print("Keep checking for 60 secs for DUT to come back on!")
        print("")
        time.sleep(5)
        for i in range(60):
            if test.check_if_remote_system_is_live(dut_ip):
                time.sleep(3)
                flashing_status = "PASS"
                flashDict[dut_ip] = flashing_status
                return flashDict
            time.sleep(1)
        flashDict[dut_ip] = flashing_status
        resultDict.update(flashDict)
        return flashDict
    
    flashDict[dut_ip] = flashing_status
    resultDict.update(flashDict)
    return flashDict   


if __name__ == "__main__":
    flash_ec = flash_cb = False
    #CHECK if destination folder exist else exit
    if not os.path.isdir(bin_location):
        print ("Binaries folder doesn't exist. Creating one. Copy binaries into folder named latest and rerun flashing script!")
        createFolders(bin_location)
        sys.exit(1)
    
    bin_location = cwd + "/latest"
    binaryDict = find_and_return_latest_binaries(bin_location)
    if binaryDict:
        if not "ec" in binaryDict:
            binaryDict["ec"] = ""
        if not "cb" in binaryDict:
            binaryDict["cb"] = ""
    else:
        print ("Binaries are not available. Copy binaries into folder named latest and rerun flashing script!")
        sys.exit(1)

    #START IP list given from the cmd line
    parser = argparse.ArgumentParser()
    parser.add_argument('--IP', dest='ip_addresses', help='provide remote system ip/s', nargs='+')
    args = parser.parse_args()

    if args.ip_addresses:
        ip_list = args.ip_addresses
    else:
        ip_list = False
        print ("check --help or give cmd argument --IP <ip_address>")
        sys.exit(1)
    print (ip_list)
    # END IP list given from the cmd line
    resultDict = dict()    
    for i in ip_list:
        if test.check_if_remote_system_is_live(i):
            # p.apply_async(FlashBinaries(i, resultDict, cbImageSrc = binaryDict["cb"], ecImageSrc = binaryDict["ec"]), ip_list, 1)
            currentResult = FlashBinaries(i, cbImageSrc = binaryDict["cb"], ecImageSrc = binaryDict["ec"])
            resultDict.update(currentResult)
    print ("*************************************************************")
    print (resultDict)               

