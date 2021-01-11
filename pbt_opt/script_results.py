import csv
import os
import sys
import glob
import pandas as pd
import argparse
import matplotlib.pyplot as plt
"""
example usage:
python script_results.py --topdir /snel/share/runs/PBT/lorenz_spike/test_pbt/ --hplist learning_rate_init
"""

def gather_run_csv(path, hp_names):
    outpath = path
    # get performance history for each worker and concatenate into a single file
    flist = list(glob.iglob(os.path.join(path, '*/perf_history.csv')))
    dnames = [os.path.basename(os.path.split(file)[0]) for file in flist]
    # unique generators
    gnames = list(set([get_digits(d.split('_')[0]) for d in dnames]))
    gnames.sort(key=int)
    flist = list(glob.iglob(os.path.join(path, 'g' + gnames[-1] + '_w*/perf_history.csv')))
    flist.sort()
    allperf = pd.concat([pd.read_csv(file, index_col=None, header=None,
                                     names=[os.path.basename(os.path.split(file)[0])]) for file in flist], axis=1)

    allperf.to_csv(os.path.join(path, 'allperf_history.csv'), index=False)

    # get HP history for each generation and concatenate into a single file
    #flist = list(glob.iglob(os.path.join(path, '*/hp_history.csv')))
    flist = list(glob.iglob(os.path.join(path, 'g' + gnames[-1] + '_w*/hp_history.csv')))
    flist.sort()
    for hp in hp_names:
        allhp = pd.concat([pd.read_csv(file, index_col=None, header=0,  usecols=[hp], squeeze=True) for file in flist], axis=1)
        allhp.to_csv(os.path.join(outpath, hp + '.csv'), index=False)
    print("Files saved in {}".format(path))

def get_digits(instring):
    '''
    Extract digits from a string: abc234de56 --> 23456
    :param instring:
    :return:
    '''
    d = ''.join([c for c in instring if c.isdigit()])
    return d

def concat_logfit(path):
    outpath = path
    flist = list(glob.iglob(os.path.join(path, '*/fitlog.csv')))
    dnames = [os.path.basename(os.path.split(file)[0]) for file in flist]
    # unique generators
    gnames = list(set([get_digits(d.split('_')[0]) for d in dnames]))
    gnames.sort(key=int)
    # unique workers
    wnames = list(set([get_digits(d.split('_')[1]) for d in dnames]))
    wnames.sort(key=int)
    # concatenate the fitlog for each worker
    for w in wnames:
        with open(os.path.join(outpath, 'w' + w + "_fitlog.csv"), 'w') as fout:
            for g in gnames:
                file = list(glob.iglob(os.path.join(path, 'g' + g + '_w' + w + '/fitlog.csv')))
		if not file:
		    break
		else:
		    file = file[0]
                with open(file, 'r') as logfile:
                    fout.write(logfile.read())


#    allperf = pd.concat([pd.read_csv(file, index_col=None, header=None,
#                                     names=[os.path.basename(os.path.split(file)[0])]) for file in flist], axis=1)


CLI=argparse.ArgumentParser()
CLI.add_argument(
  "--topdir",  # name on the CLI - drop the `--` for positional/required parameters
  nargs="*",  # 0 or more values expected => creates a list
  type=str,
  default='.',  # default if nothing is provided
)
CLI.add_argument(
  "--hplist",
  nargs="*",
  type=str,  # any type/callable can be used here
  default=[],
)



# parse the command line
args = CLI.parse_args()

gather_run_csv(args.topdir[0], args.hplist)
concat_logfit(args.topdir[0])









