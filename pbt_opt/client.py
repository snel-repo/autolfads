from __future__ import print_function
from __future__ import division
import time
from pbt_utils import DatabaseConnection
import csv
import sys, traceback
import os
from itertools import cycle
import builtins
from multiprocessing.pool import ThreadPool
from tensorflow.python.lib.io import file_io
#import shutil
#import os

def outlogger(log_path, *args):
    if not file_io.file_exists(log_path):
        file_io.create_dir(log_path)
    outlog_file = os.path.join(log_path, 'out_log.txt')
    if not file_io.file_exists(outlog_file):
        f = file_io.FileIO(outlog_file, 'w')
        f.write("")
        f.close()
    with file_io.FileIO(outlog_file, 'a') as f:
        strtext = (('{} ' * len(args)).format(*args))[:-1]
        print(strtext, file=f)
        print(strtext)

def printer(data):
    sys.stdout.write("\r\x1b[K" + data.__str__())
    sys.stdout.flush()

def write_to_csv(filepath, listdict):
    if isinstance(listdict[0], dict):
        keys = listdict[0].keys()
        with file_io.FileIO(filepath, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys, extrasaction='ignore')
            dict_writer.writeheader()
            dict_writer.writerows(listdict)
    else:
        with file_io.FileIO(filepath, 'wb') as output_file:
            wr = csv.writer(output_file, dialect='excel')
            wr.writerows([[v] for v in listdict])


class Client:
    def __init__(self, name, u_id, server_ip='localhost', port=27017, mongo_user='', mongo_passwd='',
                 idle_timeout=5*60*60):
        self.u_id = u_id
        self.status = 'init'
        global DB
        DB = DatabaseConnection(name, server_ip, port, mongo_user, mongo_passwd)
        self.run_save_path = ''
        self.train_func = None
        self.worker_uid = None
        self.current_worker = {}
        self.idle_timeout = idle_timeout    # in seconds

    def set_train_func(self, train_func):
        self.train_func = train_func

    def set_status(self, status):
        self.status = status
        DB.write_one('process', self.u_id, 'status', status)
        #DB.write_one('process', self.u_id, 'last_update', time.time())

    def check_for_worker(self):
        self.current_worker = None
        worker_uid = DB.read_one('process', self.u_id, 'worker_uid')
        if worker_uid == None or worker_uid < 0:
            return False
        worker_status = DB.read_one('worker', worker_uid, 'status')
        # this has been taken care of in the server
        if worker_status != 'new':
            return False

        self.current_worker = {}
        self.current_worker['status'] = worker_status
        self.current_worker['performance'] = None #DB.read_one('worker', worker_uid, 'performance')
        self.current_worker['epochs_per_generation'] = DB.read_one('worker', worker_uid, 'epochs_per_generation')
        self.current_worker['hps'] = DB.read_one('worker', worker_uid, 'hyperparams')
        self.current_worker['run_save_path'] = DB.read_one('worker', worker_uid, 'run_save_path')
        self.current_worker['ckpt_load_path'] = DB.read_one('worker', worker_uid, 'ckpt_load_path')
        # you can initialize self.current_worker['ckpt_save_file'] = None
        # this can be obtained by run_save_path as well (based on directory structure)
        # added for more flexible use
        self.current_worker['ckpt_save_file'] = None #DB.read_one('worker', worker_uid, 'ckpt_save_file')
        self.current_worker['hp_trace'] = DB.read_one('worker', worker_uid, 'hps_history')
        self.current_worker['generation'] = DB.read_one('worker', worker_uid, 'generation')
        self.current_worker['perf_history'] = DB.read_one('worker', worker_uid, 'perf_history')
        if not self.current_worker['perf_history']:
            self.current_worker['perf_history'] = []
        self.worker_uid = worker_uid
        return True

    def do_kill(self):
        return DB.read_one('process', self.u_id, 'do_kill')
        # explicit in case
        #if val:
        #    return True
        #else:
        #    return False

    def write_worker_db(self):
        DB.write_one('worker', self.worker_uid, 'status', self.current_worker['status'])
        DB.write_one('worker', self.worker_uid, 'performance', self.current_worker['performance'])
        DB.write_one('worker', self.worker_uid, 'ckpt_save_file', self.current_worker['ckpt_save_file'])
        DB.write_one('worker', self.worker_uid, 'perf_history', self.current_worker['perf_history'])
        # make sure to update the status the last thing
        DB.write_one('worker', self.worker_uid, 'status', self.current_worker['status'])
        #DB.write_one('worker', self.worker_uid, 'epochs_per_generation', self.epochs_per_generation)
        #DB.write_one('worker', self.worker_uid, 'hyperparams', self.current_worker['hps'])
        #DB.write_one('worker', self.worker_uid, 'run_save_path', self.run_save_path)
        #DB.write_one('worker', self.worker_uid, 'ckpt_load_path', self.ckpt_load_path)
        #DB.write_one('worker', self.worker_uid, 'hps_history', self.hps_trace)
        #DB.write_one('worker', self.worker_uid, 'generation', self.generation)

    def run_worker(self):
        start_time = time.time()
        assert self.current_worker != None, 'worker is None!'
        w_path = self.current_worker['run_save_path']

        self.set_status('busy')
        self.current_worker['status'] = 'running'
        self.write_worker_db()
        outlogger(w_path, '')
        outlogger(w_path, '====================================')
        outlogger(w_path, 'Process {} is running Worker {} in Generation {}'
              .format(self.u_id, self.worker_uid, self.current_worker['generation']))
        outlogger(w_path, 'Checkpoint load path: {}'.format(self.current_worker['ckpt_load_path']))
        outlogger(w_path, 'Job save path: {}'.format(self.current_worker['run_save_path']))

        # run the model for certain number of steps and return performance and ckpt file path
        # with error handling
        try:
        #if True:
            performance, ckpt_save_file = self.train_func(self.current_worker['hps'],
                                                          self.current_worker['run_save_path'],
                                                          self.current_worker['ckpt_load_path'],
                                                          self.current_worker['epochs_per_generation'])
            performance = float(performance)
            DB.write_one('process', self.u_id, 'time_taken', time.time() - start_time)
            outlogger(w_path, 'process {} finished running worker {}'.format(self.u_id, self.worker_uid))
            self.current_worker['status'] = 'ready'
        except:
            outlogger(w_path, '###################################### Exception Message:')
            outlogger(w_path, 'Exception occurred in Worker {} at Generation {}. Skipping it. Details:'
                  .format(self.worker_uid, self.current_worker['generation']))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            var = traceback.format_exc()
            outlogger(w_path, '{}'.format(var))
            outlogger(w_path, '###################################### End of Exception Message.')
            performance = None
            #ckpt_save_file = '{} {}'.format(repr(exc_type), repr(exc_value)) # use this to pass the error value
            ckpt_save_file = '{}'.format(var)
            self.current_worker['status'] = 'error'

        self.current_worker['performance'] = performance
        self.current_worker['perf_history'].append(self.current_worker['performance'])
        self.current_worker['ckpt_save_file'] = ckpt_save_file

        self.write_worker_db()
        # write HP history
        if 'kind' in self.current_worker:
            if self.current_worker['kind'] != 'posterior_sample_and_average':
                write_to_csv(os.path.join(self.current_worker['run_save_path'], 'hp_history.csv'),
                         self.current_worker['hp_trace'])
                write_to_csv(os.path.join(self.current_worker['run_save_path'], 'perf_history.csv'),
                         self.current_worker['perf_history'])
        else:
            write_to_csv(os.path.join(self.current_worker['run_save_path'], 'hp_history.csv'),
                        self.current_worker['hp_trace'])
            write_to_csv(os.path.join(self.current_worker['run_save_path'], 'perf_history.csv'),
                        self.current_worker['perf_history'])

        DB.write_one('process', self.u_id, 'worker_uid', -1)
        self.set_status('free')


    def keep_alive(self):
        # Update the time stamp in the db
        while True:
            if self.do_kill():
                self.set_status('killed')
                print("Kill signal received from the Sever!")
                self.shutdown()
            DB.write_one('process', self.u_id, 'last_update', time.time())
            time.sleep(5)

    def start_loop(self):
        assert self.train_func != None, 'No function to train!'
        #cir_char = cycle(['-', '\\', '|', '/'])
        #os.system('setterm -cursor off')

        # start a thread to continuously update the database with the lasted time stamp
        print('================ Process started...')
        pool = ThreadPool(processes=1)
        pool.apply_async(self.keep_alive)
        while True:
            # waiting for worker
            self.set_status('free')
            print("")
            print('Process {} is free! Waiting for worker...'.format(self.u_id))
            print("")
            time_last_assigned = time.time()
            while not (self.check_for_worker()):
                # Moved this up to prevent cluttering the log file
                #printer('Process {} is free! Waiting for worker... {}'.format(self.u_id, next(cir_char)))
                time.sleep(0.2)
                if time.time() - time_last_assigned > self.idle_timeout:
                    print('Process has been idle for {0:0.0f} minutes!'.format(self.idle_timeout//60))
                    self.set_status('killed')
                    self.shutdown()
            # run the worker
            self.run_worker()

    def shutdown(self):
        # put your shutdown script here
        print("Shutting down!")
        os._exit(1)
