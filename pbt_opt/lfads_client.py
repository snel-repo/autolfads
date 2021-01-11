from client import Client
from lfads_wrapper.lfads_wrapper import lfadsWrapper
import subprocess

import sys
import os

arg = sys.argv[1]
name = sys.argv[2]
server_ip=sys.argv[4]

if "MONGOSERVER" in os.environ: # if MONGOSERVER is env var then don't use multiple vm + multiple tpu flag
    p_uid = int(sys.argv[3])
    server_id = os.environ["MONGOSERVER"]
else:
    p_uid = int(sys.argv[3])

clnt = Client(name, p_uid, server_ip=server_ip, port=27017, mongo_user='pbt_user', mongo_passwd='pbt0Pass')

print('client {}, id:{} is running'.format(arg, p_uid))

# this is how the function input/output should look like

wrapper = lfadsWrapper()

def obj_func(hps, run_save_path, ckpt_load_path, num_epoch):
    if 'kind' in hps:
        if hps['kind'] == 'posterior_sample_and_average':
            wrapper.posterior_mean_sample(hps, ckpt_load_path)
            return (0, ckpt_load_path)
    hps['kind'] = 'train'
    return wrapper.train(hps, run_save_path, ckpt_load_path, num_epoch)

clnt.set_train_func(obj_func)

clnt.start_loop()
