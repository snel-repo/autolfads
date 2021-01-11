from __future__ import print_function
from __future__ import division
#from matplotlib.pyplot import plt
import subprocess
import itertools
import time
from pbt_utils import DatabaseConnection
import warnings
from builtins import range
import numpy as np
import random
import numbers
#import sys
#import shutil
import os
import math
import types
import json
from itertools import cycle
import sys
import copy
import signal
from tensorflow.python.lib.io import file_io

outlog_fid = -1
worklog_fid = -1
hplog_fid = -1


def printer(data):
    sys.stdout.write("\r\x1b[K" + data.__str__())
    sys.stdout.flush()


def outlogger(*args):
    global outlog_fid
    if not file_io.file_exists(outlog_fid):
        with file_io.FileIO(outlog_fid, 'w') as f:
            f.write("")
    #assert outlog_fid > 0, "Cannot open the log file!"
    with file_io.FileIO(outlog_fid, 'a') as f:
        strtext = (('{} ' * len(args)).format(*args))[:-1]
        print(strtext, file=f)
        print(strtext)


def wlogger(wlog):
    global worklog_fid
    if not file_io.file_exists(worklog_fid):
        with file_io.FileIO(worklog_fid, 'w') as f:
            f.write("")
    #assert worklog_fid > 0, "Cannot open the log file!"
    w_lines = "".join(wlog)
    with file_io.FileIO(worklog_fid, 'a') as f:
        print('{}'.format(w_lines), file=f)


def hplogger(hplog):
    global hplog_fid
    if not file_io.file_exists(hplog_fid):
        with file_io.FileIO(hplog_fid, 'w') as f:
            f.write("")
    #assert hplog_fid > 0, "Cannot open the log file!"
    hp_lines="".join(hplog)
    with file_io.FileIO(hplog_fid, 'a') as f:
        print('{}'.format(hp_lines), file=f)


class Computer:
    """ Construct a Computer object. Collection of several processes"""
    def __init__(self, machine_list):
        self.machine_list = machine_list
        self.running_processes = []
        self.process_list = []

    def start_process(self, db_name, docker_name, server_ip):
        for m in self.machine_list:
             # for each machine
             for i in range(0, m['max_processes']):
                # send shell command to machine
                p = Process(m['id'], m['ip'], m['process_start_cmd'], db_name, m['zone'], docker_name, server_ip)
                outlogger('Starting process {} on machine {}'.format(p.process_uid, m['id']))
                wait_for_process_start = m['wait_for_process_start']
                start_success = p.start_on_host(wait_for_process_start)
                if start_success and wait_for_process_start:
                    # if successful add to process list
                    outlogger('Successfully started process {} on machine {}'.format(p.process_uid, m['id']))
                    self.process_list.append(p)
                elif start_success:
                    outlogger('Assigned process {} to machine {}'.format(p.process_uid, m['id']))
                    self.process_list.append(p)
                else:
                    warnings.warn('Could not start process {} on {}:{}'.format(i, m['id'], m['ip']))
        if not self.process_list:
            outlogger('No process could be started on any machine! Terminating PBT...')
            assert 0, 'No process could be started on any machine! Terminating PBT...'

    def get_free_process(self):
        f_count = 0
        for p in self.process_list:
            s = p.get_status()
            if s == 'free':
                return p
            elif s == 'failed':
                f_count += 1
                if f_count == len(self.process_list):
                    assert 0, 'All processes are failed! Restart PBT!'
        return None

    def assign_worker(self, w):
        cir_char = cycle(['-', '\\', '|', '/'])
        os.system('setterm -cursor off')
        p = None
        while p is None:
            printer('Waiting for free process to assign Worker {} ... {}'.format(w.worker_uid, next(cir_char)))
            p = self.get_free_process()
            if p is None: time.sleep(0.2)
        p.set_worker(w)            
        os.system('setterm -cursor on')

    def kill_processes(self):
        # Kill the clients
        outlogger('\n Sending Kill Signal to all the Clients...')
        for p in self.process_list:
            p.kill_process()
        outlogger('Kill Signal sent! Waiting for the Clients to stop...')
        k = []
        for _ in range(10):
            for p in self.process_list:
                if p.get_status() == 'killed' or p.get_status() == 'failed':
                    if not p.process_uid in k:
                        k.append(p.process_uid)
                        print('Process {} at {} stopped!'.format(p.process_uid, p.host_id))
            if len(k) == len(self.process_list):
                outlogger('All client Processes stopped!')
                break
            time.sleep(1)
        if len(k) != len(self.process_list):
            outlogger('Time out! Some Client Processes were not stopped!')


class Process:
    """ Construct a Process object. Each Machine can have several Processes"""
    newid = itertools.count().next
    def __init__(self, host_id, host_ip, start_cmd, db_name, host_zone, docker_name="pbt_container", server_ip="0.0.0.0"):
        self.process_uid = Process.newid()
        self.host_id = host_id
        self.host_ip = host_ip
        self.start_cmd = start_cmd
        #self.client_shell_pid = -1
        self.tmux_name = ''
        self.do_kill = False
        self.db_name = db_name
        self.host_zone = host_zone
        self.status = '' # free/busy/fail
        self.time_last_update = 0           # reported by host, epoch time in seconds
        self.time_taken_to_ready = None     # in seconds reported by host process,
        self._CLIENT_UPDATE_INTERVAL = 30      # max initial run time (in seconds) for a worker to be marked as fail
        self.assigned_worker = None
        self._time_last_retry = 0
        self._num_retries = 0
        self._RETRY_INTERVAL = 2*60   # seconds
        self._MAX_RETRIES = 5
        self.server_ip=server_ip
        self.docker_name=docker_name

    def start_on_host(self, wait_for_client_start):
        # ssh keys must be set
        # Ports are handled in ~/.ssh/config since we use OpenSSH
        self.do_kill = False
        DB.write_many('process', self.process_uid, ['do_kill'], [False])
        # DB.write_one('process', self.process_uid, 'do_kill', False)
        cmd = self.start_cmd
        tmux_name = '{}_{}'.format(self.db_name, self.process_uid)
        p_name = '{}_{}'.format(self.host_id, self.process_uid)
        ip = self.host_ip
        zone = self.host_zone
        sh_command = "sh {} {} {} {} {}".format(cmd, self.process_uid, tmux_name, p_name , self.db_name)
        if self.docker_name:
            server_address = " {}".format(self.server_ip)
            docker_command = "docker exec {} ".format(self.docker_name)
            sh_command = docker_command + sh_command + server_address
        command = 'gcloud compute ssh %s --command=\'%s\' --zone=%s' %(ip, sh_command, zone)


        #command = "sh {} {} {} {}".format(cmd, tmux_name, p_name, self.db_name)
        #command1 = 'gcloud compute ssh %s --command=\'export PYTHONPATH=/code/lfadslite:$PYTHONPATH; export TPU_NAME=%s; sh /code/PBT_HP_opt/pbt_opt/run_lfads_client.sh %s %s %s\' --zone=us-central1-f' %(ip, ip, tmux_name, p_name, self.db_name)
        ssh = subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        error = ssh.stderr.readlines()
        result = ssh.stdout.readlines()
        if error:
            #error = ssh.stderr.readlines()
            outlogger("ERROR: {}".format(error))
            self.status = 'failed'
            #return False
        else:
            #outlogger("OUTPUT: {}".format(result))
            self.status = ''
            self.tmux_name = tmux_name
            # check if the session starts for 10 seconds
        if wait_for_client_start:
            for _ in range(100):
                # self.status = DB.read_one('process', self.process_uid, 'status')
                read_status = DB.read_many('process', self.process_uid, ['status'])
                self.status = read_status['status']
                if self.status == 'free':
                    return True
                time.sleep(0.5)
        else:
            return True
        outlogger('TIMEOUT!')
        return False

    def kill_process(self):
        self.do_kill = True
        #DB.write_one('process', self.process_uid, 'do_kill', True)
        #DB.write_one('process', self.process_uid, 'status', 'killed')
        DB.write_many('process', self.process_uid, ['do_kill', 'status'], [True, 'killed'])
        self.status = 'killed'

    def restart(self):
        outlogger('Restarting Process {} on {}! (Retry {})'
                  .format(self.process_uid, self.host_id, self._num_retries))
        self.kill_process()
        if self.start_on_host(False):
            outlogger('Successfully assigned Process {}'.format(self.process_uid))
        else:
            outlogger('Failed to assign Process {}'.format(self.process_uid))

    def get_status(self):
        # self.status = DB.read_one('process', self.process_uid, 'status')
        read_status = DB.read_many('process', self.process_uid, ['status'])
        self.status = read_status['status']
        if self.status is None:
            return None
        # time taken by the Process to run a worker until Ready
        read_time_taken = DB.read_many('process', self.process_uid, ['time_taken'])
        self.time_taken_to_ready = read_time_taken['time_taken']
        # initial time_taken

        # time stamp of the last status update by the Process
        read_time_last_update = DB.read_many('process', self.process_uid, ['last_update'])
        self.time_last_update = read_time_last_update['last_update']
        # if it takes trice than usual running time, mark the process as fail
        if (time.time() - self.time_last_update > self._CLIENT_UPDATE_INTERVAL) and (not self.do_kill):
            if self.status != 'failed':
                # mark the process as failed and reassign its worker
                outlogger('No response from process {}. Marking as failed.'.format(self.process_uid))
                if self.assigned_worker is not None and self.assigned_worker.status != 'ready':
                    outlogger('Re-assigning Worker {}'.format(self.assigned_worker.worker_uid))
                    self.assigned_worker.set_status('new')
                else:
                    outlogger("No Worker was assigned to this Process! Worker won't restart!" )
                    self.do_kill = True
                self.status = 'failed'
                # DB.write_one('process', self.process_uid, 'status', self.status)
                DB.write_many('process', self.process_uid, ['status'], [self.status])
            else:
                # if the process is already marked as failed, try to restart it
                if (time.time() - self._time_last_retry > self._RETRY_INTERVAL) and \
                        (self._num_retries <= self._MAX_RETRIES):
                    self._num_retries += 1
                    outlogger('Trying to restart Process {} on {}! (Retry {})'
                              .format(self.process_uid, self.host_id, self._num_retries))
                    if self.start_on_host(False):
                        outlogger('Successfully assigned Process {}'.format(self.process_uid))
                    else:
                        outlogger('Failed to assign Process {}'.format(self.process_uid))
                    self._time_last_retry = time.time()

        return self.status

    def set_worker(self, worker):
        self.get_status()
        if self.status == 'free':
            self.assigned_worker = worker
            # DB.write_one('process', self.process_uid, 'worker_uid', worker.worker_uid)
            DB.write_many('process', self.process_uid, ['worker_uid'], [worker.worker_uid])
            # to avoid the worker to be assigned quickly again
            # wait max 10 seconds for the process to start processing the worker
            for _ in range(50):
                if self.get_status() == 'busy':
                    self.assigned_worker.set_status('running')
                    return True #successful assignment
                time.sleep(0.2)
            #DB.write_one('process', self.process_uid, 'status', 'busy')
            outlogger('\nProcess {} on {} failed to start Worker {}'.format(self.process_uid, self.host_id, worker.worker_uid))
            self.restart()
        return False #unsuccessful assignment


class Worker:
    """ Construct a Worker object i.e. a member of the population
    """
    newid = itertools.count().next
    newid2 = itertools.count().next
    def __init__(self, worker_save_path, epochs_per_generation, worker_uid=None):
        if not self.init_existing_db():
            self.worker_uid = worker_uid if worker_uid is not None else Worker.newid()
            self.epochs_per_generation = epochs_per_generation
            self.worker_save_path = worker_save_path
            self.run_save_path = ''
            self.performance = None
            # self.eval
            self.hps = {}  # dictionary of the hyperparameters name:value
            self.status = 'new'  # 'running', 'ready', 'new'
            self.generation = 0
            self.hps_trace = []
            self.perf_history = []
            self.ckpt_save_file = ''
            self.ckpt_load_path = ''
            self.time_assigned_to_process = 0
            self.times_failed = 0
            self.MAX_FAILS = 1
            #self.assigned_process_id = -1
            self.init_new_db()

    def init_new_db(self):
        # DB.write_one('worker', self.worker_uid, 'performance', self.performance)
        # DB.write_one('worker', self.worker_uid, 'epochs_per_generation', self.epochs_per_generation)
        # DB.write_one('worker', self.worker_uid, 'status', self.status)
        # DB.write_one('worker', self.worker_uid, 'hyperparams', self.hps)
        # DB.write_one('worker', self.worker_uid, 'run_save_path', self.run_save_path)
        # DB.write_one('worker', self.worker_uid, 'ckpt_load_path', self.ckpt_load_path)
        # DB.write_one('worker', self.worker_uid, 'hps_history', self.hps_trace)
        # DB.write_one('worker', self.worker_uid, 'perf_history', self.perf_history)
        # DB.write_one('worker', self.worker_uid, 'generation', self.generation)
        flds = ['performance', 'epochs_per_generation', 'status', 'hyperparams', 'run_save_path', 'ckpt_load_path', 'hps_history', 'perf_history', 'generation']
        vals = [self.performance, self.epochs_per_generation, self.status, self.hps, self.run_save_path, self.ckpt_load_path, self.hps_trace, self.perf_history, self.generation]
        DB.write_many('worker', self.worker_uid, flds, vals)

    def init_existing_db(self):
        # todo,  test this
        try:
            # self.performance = DB.read_one('worker', self.worker_uid, 'performance')
            # self.epochs_per_generation = DB.read_one('worker', self.worker_uid, 'epochs_per_generation')
            # self.status = DB.read_one('worker', self.worker_uid, 'status')
            # self.hps = DB.read_one('worker', self.worker_uid, 'hyperparams')
            # self.run_save_path = DB.read_one('worker', self.worker_uid, 'run_save_path')
            # self.ckpt_load_path = DB.read_one('worker', self.worker_uid, 'ckpt_load_path')
            # self.hps_trace = DB.read_one('worker', self.worker_uid, 'hps_history')
            # self.perf_history = DB.read_one('worker', self.worker_uid, 'perf_history')
            # self.generation = DB.read_one('worker', self.worker_uid, 'generation')
            flds = ['performance', 'epochs_per_generation', 'status', 'hyperparams', 'run_save_path', 'ckpt_load_path', 'hps_history', 'perf_history', 'generation']
            read_vals = DB.read_many('worker', self.worker_uid, flds)
            self.performance = read_vals['performance']
            self.epochs_per_generation = read_vals['epochs_per_generation']
            self.status = read_vals['status']
            self.hps = read_vals['hyperparams']
            self.run_save_path = read_vals['run_save_path']
            self.ckpt_load_path = read_vals['ckpt_load_path']
            self.hps_trace = read_vals['hps_history']
            self.perf_history = read_vals['perf_history']
            self.generation = read_vals['generation']
            # check if the db existed
            if self.epochs_per_generation is None or \
                self.generation is None:
                return False
            else:
                return True
        except:
            return False

    def get_worker_status(self):
        # self.status = DB.read_one('worker', self.worker_uid, 'status')
        read_status = DB.read_many('worker', self.worker_uid, ['status'])
        self.status = read_status['status']
        # check_save_file_path = DB.read_one('worker', self.worker_uid, 'ckpt_save_file')
        if self.status == 'ready':
            # check_save_file_path = DB.read_one('worker', self.worker_uid, 'ckpt_save_file')
            read_check_save_file_path = DB.read_many('worker', self.worker_uid, ['ckpt_save_file'])
            check_save_file_path = read_check_save_file_path['ckpt_save_file']
            if check_save_file_path is None:
                c = 0
                while c < 5:
                    # print("ckpt_save_file is {}. Trial {}".format(check_save_file_path, c))
                    time.sleep(.2)
                    check_save_file_path = DB.read_one('worker', self.worker_uid, 'ckpt_save_file')
                    # check_save_file_path = DB.read_many('worker', self.worker_uid, ['ckpt_save_file'])
                    c += 1
                    if check_save_file_path:
                        break
            self.ckpt_save_file = check_save_file_path
        else:
            self.ckpt_save_file = DB.read_one('worker', self.worker_uid, 'ckpt_save_file')
            # self.ckpt_save_file = DB.read_many('worker', self.worker_uid, ['ckpt_save_file'])
        # self.performance = DB.read_one('worker', self.worker_uid, 'performance')
        read_performance = DB.read_many('worker', self.worker_uid, ['performance'])
        self.performance = read_performance['performance']
        return self.status

    def set_status(self, status):
        self.status = status
        # DB.write_one('worker', self.worker_uid, 'status', self.status)
        DB.write_many('worker', self.worker_uid, ['status'], [self.status])

    def write_worker_data(self):
        # DB.write_one('worker', self.worker_uid, 'performance', self.performance)
        # DB.write_one('worker', self.worker_uid, 'epochs_per_generation', self.epochs_per_generation)
        # DB.write_one('worker', self.worker_uid, 'status', self.status)
        # DB.write_one('worker', self.worker_uid, 'hyperparams', self.hps)
        # DB.write_one('worker', self.worker_uid, 'run_save_path', self.run_save_path)
        # DB.write_one('worker', self.worker_uid, 'ckpt_load_path', self.ckpt_load_path)
        # DB.write_one('worker', self.worker_uid, 'ckpt_save_file', self.ckpt_save_file)
        # DB.write_one('worker', self.worker_uid, 'hps_history', self.hps_trace)
        # DB.write_one('worker', self.worker_uid, 'generation', self.generation)
        # DB.write_one('worker', self.worker_uid, 'status', self.status)
        flds = ['performance', 'epochs_per_generation', 'status', 'hyperparams', 'run_save_path', 'ckpt_load_path', 'ckpt_save_file', 'hps_history', 'generation']
        vals = [self.performance, self.epochs_per_generation, self.status, self.hps, self.run_save_path, self.ckpt_load_path, self.ckpt_save_file, self.hps_trace, self.generation]
        DB.write_many('worker', self.worker_uid, flds, vals)

    def assign_job(self, job):
        self.get_worker_status()
        if self.status == 'running':
            warnings.warn("Cannot assign job to worker {} in 'running' status!".format(self.worker_uid))
            return False    # unsuccessful assignments
        else:
            hps, ckpt_load_path = job   # get hyperparams and init_ckpt_load_path
            self.generation += 1
            self.performance = None
            self.hps = hps   # dictionary of the hyperparameters name:value
            self.assigned_job_id = Worker.newid2()
            #self.run_save_path = '{}_jid{}'.format(self.worker_save_path, self.assigned_job_id)
	    kind_flag = 1
	    if 'kind' in hps:
		if hps['kind'] == 'posterior_sample_and_average':
		    kind_flag = 0
	    if kind_flag:
	            self.run_save_path = os.path.join(self.worker_save_path,
                                                            'g{:03d}_w{:02d}'.format(self.generation, self.worker_uid))
            self.status = 'new'
            self.times_failed = 0
            self.ckpt_save_file = ''
            self.ckpt_load_path = ckpt_load_path
            #self.assigned_process_id = -1
            self.hps_trace.append(hps)
            self.write_worker_data()
            return True     # successful assignment


class Workers:
    """ Construct a collection of Workers (to conveniently assign multiple jobs)
    """
    newid = itertools.count().next
    def __init__(self, num_workers, run_save_path, epochs_per_generation):
        self.num_workers = num_workers
        self.epochs_per_generation = epochs_per_generation
        self.run_save_path = run_save_path
        self.workers = []
        self.allready = False
        self.allnew = True
        #self.best_performance = None
        self.status = 'new'     #'running', 'ready', 'new'
        self.generation = 0
        w_uids = DB.read_all('worker', '_uid') # returns list
        # an empty list is False in python
        w_uids = w_uids if w_uids else range(0, self.num_workers)
        # Construct a list of workers
        for uid in w_uids:
            self.workers.append(Worker(self.run_save_path, self.epochs_per_generation, uid))

        # write to DB table
    def assign_jobs(self, jobs):
        """
        receive a list of jobs to assign to workers
        :param job: list of tuples in the form (hyperparameters, ckpt_ckpt_path)
        :return:
        """
        # enforce one-to-one job-worker assignment (in simple initial implementation, can be modified later)
        assert len(jobs) == self.num_workers, 'number of jobs to be assigned must be equal to number of workers!'

        self.get_workers_status()
        if self.status == 'somerunning':
            warnings.warn("Cannot assign jobs! Wait for all the workers to become 'ready'!")
            return False    # unsuccessful assignments
        else:
            succ_assign = []
            for idx, job in enumerate(jobs):
                succ_assign.append(self.workers[idx].assign_job(job))
            return all(succ_assign)     # successful assignment

    def get_workers_status(self):
        for wk in self.workers:
            status = wk.get_worker_status()
            # in case of error in the model function at the client side
            if status == 'error':
                print("")
                outlogger('Error in Worker {}, Gen {}! Error: {}'.format(wk.worker_uid, wk.generation,
                                                                                          wk.ckpt_save_file))
                wk.times_failed += 1
                if wk.times_failed < wk.MAX_FAILS:
                    outlogger("Re-assigning it!")
                    wk.set_status('new')
                else:
                    wk.set_status('bad')
                    outlogger('Worker {}, Gen {} failed {} times! Marking as bad!'
                              .format(wk.worker_uid, wk.generation, wk.times_failed))


        if all([wk.status == 'ready' for wk in self.workers]):
            self.status = 'allready'
        elif all([wk.status == 'new' for wk in self.workers]):
            self.status = 'allnew'
        elif all([wk.status in ['ready', 'bad'] for wk in self.workers]):
            self.status = 'allready+error'
        # first time reading from the database
        #elif all([wk.status == None for wk in self.workers]):
        #    self.status = 'allready'
        else:
            self.status = 'somerunning'
        return self.status

    def process_workers(self, computer):
        """
        assignes workers to the processes and wait until all the workers are assigned
        """
        # generator over new workers
        new_workers = [w for w in self.workers if w.status == 'new']
        for w in new_workers:
            computer.assign_worker(w)
        if len(new_workers) > 0:
            printer('\r')
            outlogger('Finished assigning all the Workers!                             ')


class HyperParams:
    """
    Collection of all the hyperparamters
    """
    def __init__(self):
        self.n_hps = 0
        self.n_hps_explorable = 0
        self.hp_dict = {}
        #self.hp_archive = []

    def add_hp(self, name, value, dtype=np.float32, init_sample_mode='rand', explorable=False, explore_method='perturb',
               explore_param=None, limit_explore=False):
        if name in self.hp_dict:
            print('Warning: Hyperparameter "%s" already exists! Overwriting the value.' % name)
        self.hp_dict[name] = HyperParam(name, value, dtype, init_sample_mode, explorable, explore_method, explore_param, limit_explore)
        self.n_hps += 1
        self.n_hps_explorable += int(self.hp_dict[name].explorable)

    def sample_hps(self, mode, num_samples=1):
        """
        Sample all the hyper-parameters
        :param mode: 'init', 'rand' or 'grid'. 'init' uses the mode defined in HyperParam. using 'rand' or 'grid'
                     overrides that
        :param num_samples: number of samples to be generated
        :return: format  [{hp1: val11, hp2:val12, ..}, {hp1:val21, hp2:val22,...}, ..., {hp1:valN1, hp2:valN2,...}]
        """
        # invoke the .sample() method for each object in the dictionary
        hp_samps = map(lambda v: v[1].sample(mode, num_samples), list(self.hp_dict.items()))
        # format the output as [{hp1: val11, hp2:val12, ..}, {hp1:val21, hp2:val22,...}]
        hp_names = [n.keys()[0] for n in hp_samps]  # get the hp names
        values_mat = [q.values()[0] for q in hp_samps]  # prepare the value matrix
        # put the single sample in a list (to avoid error in transpose)
        if not isinstance(values_mat[0], list):
            values_mat = [[v] for v in values_mat]
        # transpose list of list
        values_mat = map(list, zip(*values_mat))
        hp_dict = [dict(zip(tuple(hp_names), tuple(h))) for h in values_mat]
        if num_samples == 1:
            hp_dict = hp_dict[0]
        return hp_dict

    def get_explorable_mask(self):
        return [hp.explorable for (_, hp) in list(self.hp_dict.items())]


class HyperParam:
    """
    Defines the properties for a single hyperparameter
    """
    def __init__(self, name, value, dtype=np.float32,
                 init_sample_mode='rand', explorable=False, explore_method='perturb',
                 explore_param=None, limit_explore=False):
        """
        Defines the properties for a single hyper parameter
        :param value: use tuple to indicate range, or list/nparray for allowable values
        :param dtype: data type
        :param init_sample_mode: 'rand' or 'grid', mode of preferred initialization
        :param explorable: True or False, whether the 'explore' action should apply to this hyperparameter
        """
        self.name = name
        self.value = value # tuple to indicate range, list/nparray for allowable values
        self.dtype = dtype  # numpy dtype
        #self.default_value = None   # sample_fn overrides this
        self.explorable = explorable
        self.init_sample_mode = init_sample_mode
        self.explore_param = explore_param
        self.explore_method = explore_method
        self.limit_explore = limit_explore

    def sample(self, mode, num_samples):
        """
        Generate sample for hyperparameter
        :param mode: 'rand', 'grid', 'init'
        :param num_samples: number of samples to generate
                           if mode=='grid', number of grids
        :return: sampled hyperparameter value(s)
        """
        if mode == 'init':
            mode = self.init_sample_mode
        if isinstance(mode, list):
            # repeat the same value for all the samples
            samp = mode * num_samples
        elif mode == 'rand':
            if isinstance(self.value, tuple): # value is range
                samp = (self.value[1] - self.value[0]) * np.random.rand(num_samples) + self.value[0]
                samp = [np.asscalar(v) for v in samp.astype(self.dtype)]
            else:
                samp = [random.choice(self.value) for _ in range(num_samples)]
        elif mode == 'logrand':
            if isinstance(self.value, tuple): # value is range
                samp = np.power(10, (np.log10(self.value[1]) - np.log10(self.value[0]))
                                 * np.random.rand(num_samples) + np.log10(self.value[0]))
                samp = [np.asscalar(v) for v in samp.astype(self.dtype)]
            else:
                #samp = [random.choice(self.value) for _ in range(num_samples)]
                assert 0, 'You must provide a tuple for logrand!'
        elif mode == 'grid':
            if isinstance(self.value, tuple): # value is range
                samp = np.linspace(self.value[0], self.value[1], num_samples)
                samp = [np.asscalar(v) for v in samp.astype(self.dtype)]
            else:
                values = self.value
                # -+0.5 to get the balanced number at the edges
                samp = values[np.rint(np.linspace(-0.5, len(values)-0.5, num_samples)-0.5).astype(np.int32)]
        else:
            assert 0, 'Sample mode not recognized!'

        if num_samples == 1:
            samp = samp[0]

        return {self.name: samp}

    def fixvalue(self, value):
        if (isinstance(self.value, tuple) and self.limit_explore):
            if value < self.value[0]:
                value = self.value[0]
            elif value > self.value[1]:
                value = self.value[1]
            #pass
        elif isinstance(self.value, list):
            value = min(self.value, key=lambda x:abs(x-value))
        value = np.asscalar(np.array(value).astype(self.dtype))
        return value

class Population:
    """ The total Population consisting of all the Workers"""
    def __init__(self, computer, hyperparams,
                 num_workers, epochs_per_generation, run_save_path,
                 max_generations, exploit_method, exploit_param,
                 explore_method, explore_param, mode, num_no_best_to_stop, min_change_to_stop,
                 server_log_path):
        self.computer = computer
        self.server_log_path = server_log_path if server_log_path else run_save_path
        self.mode = mode
        self.num_workers = num_workers
        self.hyperparams = hyperparams
        self.mean_performance = []
        self.best_performance = []
        self.max_generations = max_generations
        self.min_worker_generation = 0
        self.exploit_method = exploit_method  # 'truncationselection' , 'binarytournament'
        self.explore_method = explore_method  # 'perturb' or 'resample'
        self.exploit_param = exploit_param
        self.explore_param = explore_param
        self.workers = Workers(self.num_workers, run_save_path, epochs_per_generation)
        self.num_no_best_to_stop = num_no_best_to_stop # stop the training if the change in the mean performance in less than this
        self.min_change_to_stop = min_change_to_stop

    def initialize(self):
        """
        Initialize the Population
        :param num_workers: number of simultaneous workers in the Population.
                            For each Worker hyperparameters are initialized
                            based on the 'init' property of each hyperparameter
        :return: loads the active_workers with the initialized workers
        """
        # sample the hyperparameters based on their 'init' mode
        hps_init = self.hyperparams.sample_hps('init', self.num_workers)
        # convert list of hyperparameters to list of job tuples an assign to workers
        # job = (hp, ckpt_load_path)
        #self.workers.assign_jobs([(hp,'') for hp in hps_init])
        return [(hp, '') for hp in hps_init]


    def run_generation_ps(self):
        # run workers on the processess
        self.workers.process_workers(self.computer)
        # wait until all the workers become ready (change this part to allow explore/exploit
        # between different generations ie. all workers need not to reach same generation to be
        # considered for explore/exploit)
        cir_char = cycle(['-', '\\', '|', '/'])
        #os.system('setterm -cursor off')

        # todo, check gets stuck in this loop
        # todo, add time-out for the worker and reassign the job
        cnt = 0
        while True:
            printer('Waiting for Workers to finish... {}'.format(next(cir_char)))
            self.workers.process_workers(self.computer)
            for p in self.computer.process_list: p.get_status()
            w_status = self.workers.get_workers_status()
            if  w_status == 'allready':
                outlogger('\rFinished processing all Workers.                        ')
                break
            elif w_status == 'allready+error':
                outlogger('\rFinished processing all Workers. Some Workers existed with Error!')
                break
            time.sleep(0.5)

    def run_generation(self):
        # run workers on the processess
        self.workers.process_workers(self.computer)
        # wait until all the workers become ready (change this part to allow explore/exploit
        # between different generations ie. all workers need not to reach same generation to be
        # considered for explore/exploit)
        cir_char = cycle(['-', '\\', '|', '/'])
        #os.system('setterm -cursor off')

        # todo, check gets stuck in this loop
        # todo, add time-out for the worker and reassign the job
        cnt = 0
        while True:
            printer('Waiting for Workers to finish... {}'.format(next(cir_char)))
            self.workers.process_workers(self.computer)
            for p in self.computer.process_list: p.get_status()
            w_status = self.workers.get_workers_status()
            if  w_status == 'allready':
                outlogger('\rFinished processing all Workers.                        ')
                break
            elif w_status == 'allready+error':
                outlogger('\rFinished processing all Workers. Some Workers existed with Error!')
                break
            time.sleep(0.5)

        #os.system('setterm -cursor on')

        # track the performance of the population
        p = [w.performance for w in self.workers.workers]
        if None in p:
            outlogger('One or more Workers returned None. This usually '
                      'means an error has occurred in the call function at the client side!')

        # remove None when calculating the mean, min and max
        p = [pp for pp in p if (pp is not None) and not math.isnan(pp)]

        # best performance is defined max or min performance?
        self.best_performance.append(max(p) if self.mode == 'maximize' else min(p))
        self.mean_performance.append(np.mean(p))
        self.min_worker_generation = min([w.generation for w in self.workers.workers])
        jobs = []
        hpl_lines=[]
        wl_lines=[]
        for w in self.workers.workers:
            #if w.get_worker_status() == 'ready': # useful for for semi-sync
            # exploit on weights and hps
            #outlogger('Processing Generation:', w.generation, ', Worker:', w.worker_uid)
            (job, hp_changed, worker_select) = self.exploit(w)
            # explore only when hps are changed
            if hp_changed:
                (hps, ckpt_load_path) = job
                hps = self.explore(hps)
                job = (hps, ckpt_load_path)
            # assign the worker new job based on the exploited/explored hps
            jobs.append(job)

            wlog_list = ['Gen', w.generation, 'Worker', w.worker_uid, 'Exploited', hp_changed,
                        'Exploited_from', worker_select.worker_uid if hp_changed else '',
                        'Perf_source', w.performance, 'Perf_compare', worker_select.performance]
            wlog_join = ", ".join([str(x) for x in wlog_list]) + "\n"
            wl_lines.append(wlog_join)
            hplog='{}, {}\n'.format(w.hps, job[0])
            hpl_lines.append(hplog)
        wlogger(wl_lines)
        hplogger(hpl_lines)
        return jobs
    
    def exploit(self, worker):
        hp_changed = False
        if self.exploit_method == 'binarytournament':
            # randomly select a worker from other members of population
            sane_workers = [w for w in self.workers.workers
                            if w.performance is not None and
                            not math.isnan(w.performance) and
                            w.worker_uid != worker.worker_uid
                            ]
            try:
                worker_select = random.choice(sane_workers)
            except:
                per_w = [w.performance for w in self.workers.workers]
                uid_w = [w.worker_uid for w in self.workers.workers]
                print("per_w, uid_w", per_w, uid_w)
            ## getting the best Worker
            #if (self.mode == 'maximize'):
            #    best_worker = max(sane_workers, key=lambda x: x.performance)
            #elif (self.mode == 'minimize'):
            #    best_worker = min(sane_workers, key=lambda x: x.performance)
            #else:
            #    assert 0, 'Mode error. Must be maximize or minimize!'
            # worker_select.get_worker_status # if we want to do semi-sync
            if worker.performance is None or math.isnan(worker.performance):
                outlogger('Worker {}, performance is None or NaN! Forcing exploit!'.format(worker.worker_uid))
                job = (worker_select.hps.copy(), (worker_select.ckpt_save_file +'.')[:-1])
                hp_changed = True
            elif ((self.mode == 'maximize') and (worker_select.performance > worker.performance)) or \
                    ((self.mode == 'minimize') and (worker_select.performance < worker.performance)):
                try:
                    job = (worker_select.hps.copy(), (worker_select.ckpt_save_file +'.')[:-1])
                except:
                    print("(Case 1) CKPT save file ", worker_select.ckpt_save_file, worker_select.worker_uid, worker_select.performance)
                hp_changed = True
            else:
                # copy the same hps and ckpt path (not changed)
                try:
                    job = (worker.hps.copy(), (worker.ckpt_save_file +'.')[:-1])
                except:
                    print("(Case 2) CKPT save file ", worker.ckpt_save_file, worker.worker_uid, worker.performance)

        elif self.exploit_method == 'truncationselection':
            # to be implemented
            assert 0, 'not implemented'

        elif self.exploit_method == 'roulettewheel':
            allperfs = [w.performance for w in self.workers.workers]
            assert 0, 'not implemented'

        else:
            assert 0, "Invalid exploit method: {}".format(self.explore_method)
        return job, hp_changed, worker_select

    def explore(self, hps):
        def isalambda(v):
            LAMBDA = lambda: 0
            return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__

        for hp_name, hp_val in list(hps.items()):
            hp_obj = self.hyperparams.hp_dict[hp_name]
            if hp_obj.explorable:
                if hp_obj.explore_method == 'perturb':
                    if isalambda(hp_obj.explore_param):
                        scale = hp_obj.explore_param
                    else:
                        #scale = random.choice([1.0 - self.explore_param, 1.0 + self.explore_param])
                        rnd_val = random.uniform(-0.5, 0.5)
                        rnd_val = rnd_val if abs(rnd_val) > 0.001 else 0.001 * np.sign(rnd_val)
                        scale = 1.0 + 2 * hp_obj.explore_param * rnd_val
                    hps[hp_name] = hp_obj.fixvalue(hp_val * scale)
                elif hp_obj.explore_method == 'resample':
                    if isinstance(hp_obj.explore_param, dict):
                        samp_mode = hp_obj.explore_param['sample_mode']
                        samp_prob = hp_obj.explore_param['sample_prob']
                    else:
                        #samp_mode = 'rand'
                        samp_prob = 1.0
                        samp_mode = hp_obj.explore_param if isinstance(hp_obj.explore_param, basestring) else \
                         (hp_obj.init_sample_mode if isinstance(hp_obj.init_sample_mode, basestring) else 'rand')
                    if np.random.rand() < samp_prob:
                        samp = hp_obj.sample(samp_mode, 1)
                        hps[hp_name] = samp[hp_name]
                    else:
                        hps[hp_name] = hp_val
                else:
                    assert 0, "Invalid explore method: {}".format(self.explore_method)
        return hps  # or use the hps changed in-place
                
    def end_training(self):
        if self.min_worker_generation >= self.max_generations:
            outlogger('Maximum generation reached. Stopping PBT...')
            return True
        num_last_gen = self.num_no_best_to_stop

        perfs = np.array(self.best_performance)

        if perfs.shape[0] < num_last_gen:
            return False

        #if self.mode == 'maximize':
        #    pass
        if self.mode == 'minimize':
            perfs = - perfs

        best_perf = np.max(perfs)
        #if self.mode == 'maximize' and np.mean(best_perf[-5:-1]) * (1. + stop_perc_change) < best_perf[-1] or \
        #   self.mode == 'minimize' and np.mean(best_perf[-5:-1]) * (1. - stop_perc_change) > best_perf[-1]:
        #   idx_stop =  len(best_perf)
        percent_change = (best_perf - perfs[-num_last_gen]) / np.mean(np.abs(perfs[-num_last_gen:]))

        if percent_change <= self.min_change_to_stop:
        #if (len(best_perf) - best_idx) > num_last_gen:
            outlogger('No or very small improvement on performance for last {} generations. Stopping PBT...'.format(num_last_gen))
            return True

        return False

        # mean change over the last few generations as percentage of the performance
        #thresh = np.mean(abs(self.best_performance[-1])) * self.num_no_best_to_stop
        #if np.mean(abs(np.diff(self.best_performance[-num_last_gen:]))) < thresh:
        #    outlogger('No improvement on performance for last {} generations. Stopping PBT...'.format(num_last_gen))
        #    return True
        #else:
        #    return False

    def train(self):
        """
        main training loop for population
        :return:
        """
        try:
            # todo, don't initialize when loading previous run
            # initialize population
            outlogger("Initializing Population... ")
            jobs = self.initialize()
            # run generation until training end criteria met
            best_worker_list = []
            #w = {'generation':-1, 'worker_uid':None, 'performance':None, 'run_save_path':''}
            best_sofar = None
            while not self.end_training():
                self.workers.assign_jobs(jobs)
                outlogger('==================================')
                outlogger('Running Generation {} ...'.format(self.workers.workers[0].generation))
                time_get_start = time.time()
                jobs = self.run_generation()
                time_taken = time.time() - time_get_start
                outlogger('Time taken: {0:0.0f} min, {1:0.0f} sec'.format(*divmod(time_taken, 60)))

                best_worker = [w for w in self.workers.workers if w.performance == self.best_performance[-1]]
                best_worker_list.append(copy.deepcopy(best_worker[0]))
                for w in best_worker:
                    outlogger('Best Worker: Gen {}, Worker {}, Performance {}'.format(w.generation, w.worker_uid, w.performance))
                if self.mode == 'maximize':
                    minmax_fun = max
                elif self.mode == 'minimize':
                    minmax_fun = min
                best_sofar= copy.deepcopy(minmax_fun(best_worker_list, key=lambda x: x.performance))
                with file_io.FileIO(os.path.join(self.server_log_path, 'best_worker.sofar'), 'wb') as f:
                    print('{}'.format(best_sofar.run_save_path), file=f)
            outlogger('Finished training!')
        except KeyboardInterrupt:
            outlogger('Training interrupted by the user!!')

        # final best worker
        w = best_sofar # min(best_worker_list, key=lambda x:x.performance)
        if best_sofar is not None:
            outlogger('==================================')
            outlogger('Final Best Worker: Gen {}, Worker {}, Performance {}'.format(w.generation, w.worker_uid, w.performance))
        # return the final best worker
        return w

#[w. for w in #self.workers.workers.hps_trace[-2]
#if w.performance==self.best_performance[-1]])


class Server:
    def __init__(self, name, run_save_path, num_workers=40, epochs_per_generation=100,
                 max_generations=20, exploit_method='binarytournament', exploit_param=[],
                 explore_method='perturb', explore_param=0.2, mode='minimize', force_overwrite=True,
                 mongo_server_ip='localhost', port=27017, mongo_user='pbt_user', mongo_passwd='pbt0Pass',
                 server_log_path='./', num_no_best_to_stop=5, min_change_to_stop=0.0005, docker_name="pbt_container"):
        global DB
        DB = DatabaseConnection(name, mongo_server_ip, port, mongo_user, mongo_passwd)
        DB.db['process'].remove()
        global outlog_fid
        global worklog_fid
        global hplog_fid
        if not file_io.file_exists(server_log_path):
            file_io.create_dir(server_log_path)
        outlog_fid = os.path.join(server_log_path, 'out_log.txt')
        worklog_fid = os.path.join(server_log_path, 'decision_log.csv')
        # the reason for using csv there is that json is not good for appending on disk
        # (whole data must be available before dump unless if we want to do read append write
        # anyway with an script we can easily read this format {dict}, {dict}
        hplog_fid = os.path.join(server_log_path, 'hp_log.csv')
        if force_overwrite:
            DB.db['worker'].remove()
            with file_io.FileIO(outlog_fid, 'w') as f:
                f.write("")
            with file_io.FileIO(worklog_fid, 'w') as f:
                f.write("")
            with file_io.FileIO(hplog_fid, 'w') as f:
                f.write("")
            # open(outlog_fid, 'w').close()
            # open(worklog_fid, 'w').close()
            # open(hplog_fid, 'w').close()
        self.mongo_server_ip = mongo_server_ip
        self.force_overwrite = force_overwrite
        self.name = name
        self.server_log_path = server_log_path
        self.run_save_path = run_save_path
        self.computer = None
        self.num_workers = num_workers
        self.hyperparams = HyperParams()
        #self.population =  None
        self.epochs_per_generation = epochs_per_generation
        self.max_generations = max_generations
        self.exploit_method = exploit_method
        self.exploit_param = exploit_param
        self.explore_method = explore_method
        self.explore_param = explore_param
        assert any(mode in s for s in ['maximize', 'minimize']), "Invalid mode! choose 'maximize' or 'minimize'"
        self.mode = mode
        self.perv_C = False
        self.num_no_best_to_stop = num_no_best_to_stop
        self.min_change_to_stop = min_change_to_stop
        self.docker_name=docker_name
        self.server_ip=mongo_server_ip

    def add_computers(self, computers):
        self.computer = Computer(computers)

    def add_hp(self, name, value, dtype=np.float32, init_sample_mode='rand', explorable=False,
               explore_method=None, explore_param=None, limit_explore=False):
        if explore_param is None:
            explore_param = self.explore_param
        if not explore_method:
            explore_method = self.explore_method
        self.hyperparams.add_hp( name, value, dtype, init_sample_mode, explorable, explore_method, explore_param, limit_explore)
    """
    def signal_handler(self, signal, frame):
        '''To handle Ctrl+C and kill the clients
        '''
        #user_inp = raw_input('Are you sure you want to stop PBT training? This will kill all the client processes.\n')
        if self.perv_C:
            outlogger('Force killing the Server...')
            sys.exit(0)
        self.perv_C = True

        outlogger('\nPBT Training interrupted! Sending Kill Signal to all the Client processes...')
        for p in self.computer.process_list:
            p.kill_process()
        outlogger('Kill Signal sent! Waiting for the Clients to stop...')
        k = []
        for _ in range(3*60):
            for p in self.computer.process_list:
                if p.get_status() == 'killed':
                    if not p.process_uid in k:
                        k.append(p.process_uid)
                        outlogger('Process {} at {} stopped!'.format(p.process_uid, p.host_id))
            if len(k) == len(self.computer.process_list):
                outlogger('All client Processes stopped!')
                sys.exit(0)
            time.sleep(1)
        outlogger('Time out! Some Client Processes were not stopped!')
        sys.exit(0)
    """

    def start_pbt(self):
        if not self.force_overwrite and file_io.file_exists(os.path.join(self.server_log_path, 'best_worker.done')):
            with file_io.FileIO(os.path.join(self.server_log_path, 'best_worker.done'), 'r') as f:
                return {'run_save_path':f.read()[:-1]}
        self.computer.start_process(db_name=self.name, docker_name=self.docker_name, server_ip=self.server_ip)

        # to capture Crtl+C and kill clients
        #signal.signal(signal.SIGINT, self.signal_handler)

        #outlogger('===== Computer Object Values: ')
        #outlogger(self.computer.__dict__)
        popl = Population(self.computer, self.hyperparams, self.num_workers, self.epochs_per_generation, self.run_save_path,
                          self.max_generations, self.exploit_method, self.exploit_param,
                          self.explore_method, self.explore_param, self.mode, self.num_no_best_to_stop, self.min_change_to_stop, self.server_log_path)

        outlogger('===== Server Object Values: ')
        # get all parameters except those that are class instances
        param_dict = {}
        for p, v in self.__dict__.items():
            if type(v) is not types.InstanceType:
                param_dict[p] = v

        outlogger(param_dict)

        with file_io.FileIO(os.path.join(self.server_log_path, 'pbt_params.json'), 'w') as jsonfile:
            json.dump(param_dict, jsonfile)

        # Start PBT training
        best_worker = popl.train()
        os.system('setterm -cursor on')
        if best_worker:
            with file_io.FileIO(os.path.join(self.server_log_path, 'best_worker.done'), 'wb') as f:
                print('{}'.format(best_worker.run_save_path), file=f)

        # self.computer.kill_processes()

        return best_worker, popl



    def kill_processes(self):
	self.computer.kill_processes()
