from client import Client
from builtins import range
import sys

arg = sys.argv[1]

name = 'fixedname2'

p_uid = int(arg.split('_')[1])

clnt = Client(name,p_uid,'cortex.bme.emory.edu')

print('client {}, id:{} is running'.format(arg, p_uid))

# this is how the function input/output should look like
def dummyfunc(hps, run_save_path, ckpt_load_path, epochs_per_generation):
    h1 = hps['h1']
    h2 = hps['h2']
        #for i in range(0,epochs_per_generation):
        #pass

    performance = -( (h1+3)**2 + (h2-5)**2 )

    ckpt_save_path = ckpt_load_path
    return performance, ckpt_save_path


clnt.set_train_func(dummyfunc)

clnt.start_loop()
