
import sys
import os
import re
import glob
import shutil

#sys.path.insert(0, '/snel/home/mreza/projects/PBT_HP_opt/lfadslite')  # path to lfadslite

from run_lfadslite import hps_dict_to_obj, jsonify_dict
from data_funcs import load_datasets
from helper_funcs import kind_dict, kind_dict_key
from lfadslite import LFADS
import data_funcs as utils
import warnings

from tensorflow.python.lib.io import file_io
#import __builtin__

from subprocess import call
import time

#def gcp_open(name, mode='r'):
#    return file_io.FileIO(name, mode=mode)

#def gcp_write(name, mode='w'):
#    return file_io.FileIO(name, mode='w')

#__builtin__.open = gcp_open
#__builtin__.write = gcp_write

#os.path.exists = file_io.file_exists
#os.makedirs = file_io.create_dir
#shutil.rmtree = file_io.delete_recursively
#shutil.copy = file_io.copy
#glob.glob = file_io.get_matching_files


class lfadsWrapper:
    def __init__(self):
        # Below variables are used to not reload the dataset
        self.datasets = None
        self.data_dir = None
        self.data_filename_stem = None

    # copy checkpoints (exploit operation) to new run directory
    def _copy_checkpoint(self, ckpt_load_path, target_path, ckpt_name):
        # add / if doesn't exist
        target_path = os.path.join(target_path, '')
        ckpt_load_path = os.path.join(ckpt_load_path, '')
        # get the latest checkpoint files
        ckpt_file = os.path.join(ckpt_load_path, ckpt_name)
        with file_io.FileIO(ckpt_file, 'r') as f:
            first_line = f.readline()
            f.seek(0)
            filedata = f.read()
        # pattern = r'"([A-Za-z0-9_\./\\-]*)"'
        # m = re.search(pattern, first_line).group()
        m = re.findall('"([^"]*)"', first_line)[0]
        # copy the checkpoints to the new directory
        m = os.path.join(ckpt_load_path, m + '*')
        if not file_io.file_exists(target_path):
            file_io.create_dir(target_path)
        else:
            file_io.delete_recursively(target_path)
            file_io.create_dir(target_path)
            #warnings.warn('The path to the new job directory already exist! '
            #              'Are you sure you are not over-writing on an old run?')
            warnings.warn("The directory for the new job already exists! Overwriting it!")

        assert call("gsutil -m cp %s %s"% (m, target_path), shell=True)==0, "error copying checkpoints"
        
        #for file in glob.glob(m):
        #    shutil.copy(file, target_path)
        # replace the old ckpt path with the new one
        ## no need for tfestimator implementation
        #filedata = filedata.replace(ckpt_load_path, target_path)

        ckpt_file_t = os.path.join(target_path, ckpt_name)
        # create LVE_CKPT_NAME at the target dir
        with (file_io.FileIO(ckpt_file_t, 'w')) as the_file:
            the_file.write(filedata)

    def posterior_mean_sample(self, hps_dict, ckpt_load_path):
        hps = hps_dict_to_obj(hps_dict)
        assert hps.kind == "posterior_sample_and_average", 'Kind is not posterior sample and average'
        # change the kind str to kind number !!!
        hps.kind = kind_dict(hps.kind)
        hps.lfads_save_dir = ckpt_load_path
        self.load_datasets_if_necessary(hps)
        self.infer_dataset_properties(hps)
        model = self.build_model(hps, datasets=self.datasets)
        model_runs = model.write_model_runs(hps, self.datasets, None)
        return model_runs

    def train(self, hps_dict, lfads_save_path, ckpt_load_path, epochs_per_generation):
        hps = hps_dict_to_obj(hps_dict)
        assert hps.kind == "train", 'You can only envoke train with kind=train'
        hps.kind = kind_dict(hps.kind)
        if ckpt_load_path != '':
            if ckpt_load_path != lfads_save_path:
                # todo, allow different checkpoint name in lfadslite tf estimator
                # the default checkpoint name is used
                assert hps['checkpoint_pb_load_name'] == 'checkpoint', 'custom checkpoint name is not implemented in lfadslite_tfestimator'
                ckpt_name = hps['checkpoint_pb_load_name']
                self._copy_checkpoint(ckpt_load_path, lfads_save_path, ckpt_name)
        else:
            # clear the run folder if it is a new run
            if file_io.file_exists(lfads_save_path):
                warnings.warn("The directory for the new job already exists! Overwriting it!")
                file_io.delete_recursively(lfads_save_path)


        hps.lfads_save_dir = lfads_save_path
        self.load_datasets_if_necessary(hps)
        self.infer_dataset_properties(hps)

        trial_recon_cost, samp_recon_cost = self._train(hps, self.datasets, epochs_per_generation)
        if hps.val_cost_for_pbt == 'heldout_samp':
            recon_cost = samp_recon_cost
        elif hps.val_cost_for_pbt == 'heldout_trial':
            recon_cost = trial_recon_cost
        else:
            assert 0, 'You must specify a heldout_samp or heldout_trial for recon cost!'
        return recon_cost, lfads_save_path

    def load_datasets_if_necessary(self, hps):
        stem_changed = self.data_filename_stem != hps.data_filename_stem
        data_dir_changed = self.data_dir != hps.data_dir
        if stem_changed or data_dir_changed:
            self.datasets = load_datasets(hps.data_dir,
                                          hps.data_filename_stem, hps)

    def infer_dataset_properties(self, hps):
        ''' refer to main code in run_lfadslite '''
        # infer the dataset names and dataset dimensions from the loaded files
        hps.dataset_names = []
        hps.dataset_dims = {}
        for key in self.datasets:
            hps.dataset_names.append(key)
            hps.dataset_dims[key] = self.datasets[key]['data_dim']
        # also store down the dimensionality of the data
        # - just pull from one set, required to be same for all sets
        hps.num_steps = self.datasets.values()[0]['num_steps']
        hps.ndatasets = len(hps.dataset_names)

    def _train(self, hps, datasets, num_steps):
        model = self.build_model(hps, datasets=datasets)
        model.train_model(hps, run_mode='pbt', num_steps=num_steps)
        return model.trial_recon_cost, model.samp_recon_cost         # for recon cost

    def build_model(self, hps, datasets=None):
        model = LFADS(hps, datasets=datasets)

#        if not os.path.exists(hps.lfads_save_dir):
#            print("Save directory %s does not exist, creating it." % hps.lfads_save_dir)
#            os.makedirs(hps.lfads_save_dir)
        fname = ''.join(('hyperparameters', '.txt'))
        hp_fname = os.path.join(hps.lfads_save_dir, fname)
        hps_for_saving = jsonify_dict(hps)
        utils.write_data(hp_fname, hps_for_saving, use_json=True)

        return model
