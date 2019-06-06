import multiprocessing as mp
import random
import string
import time
import argparse
import os
import sys


p = mp.Pool(mp.cpu_count())
result = dict()
def rand_string(dut_ip, cbFlash = "test"):
    d = dict()
    time.sleep(5)
    d[dut_ip] = cbFlash
    print (d)
    result.update(d)

    


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

test_var = "test1234"
for i in ip_list:
    result123 = p.apply_async(rand_string(i, cbFlash = test_var),ip_list, 1)

print ("END")
print(result)     
