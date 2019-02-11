import tensorflow as tf
from tensorflow.python import debug as tf_debug
import numpy as np
import os,sys,time,datetime
from os.path import expanduser
import pdb
home = expanduser("~")

ZYTHON_PATH = "{}/Projects/".format(home)
sys.path.insert(0, ZYTHON_PATH)


import subprocess
git_rev = subprocess.Popen("git rev-parse --short HEAD", shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]
git_branch = subprocess.Popen("git symbolic-ref --short -q HEAD", shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]

timestamp = time.time()
timestamp = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')




# Set random seed
#seed = 123
#np.random.seed(seed)
#tf.set_random_seed(seed)


flags = tf.app.flags
FLAGS = flags.FLAGS
# Settings
flags.DEFINE_boolean('log_device_placement', False, "Whether to log device placement.")
flags.DEFINE_string('data_prefix', '', 'prefix identifying training data. must be specified.')
flags.DEFINE_string('base_log_dir', '.', 'base directory for logging and saving embeddings')
flags.DEFINE_integer('gpu', -1234, "which gpu to use.")
flags.DEFINE_integer('print_every', 15, "How often to print training info.")
flags.DEFINE_integer('max_total_steps', 10**10, "Maximum total number of iterations")

flags.DEFINE_string('train_config', '', "path to the configuration of training (*.yml)")
flags.DEFINE_string('model','','pretrained model')
flags.DEFINE_string('dtype','s','d for double, s for single precision floating point')

# to be run with ./exp/dse.py
flags.DEFINE_string('spreadsheet','','spreedsheet for systematic hyper-param tuning')


#flags.DEFINE_string('restore_file', '', "path to model to be restored")
#flags.DEFINE_string('db_name', 'data.db', 'name of the database which stores the training log')



gpu_selected = FLAGS.gpu
if gpu_selected == -1234:
    # auto detect gpu by filtering on the nvidia-smi command output
    gpu_stat = subprocess.Popen("nvidia-smi",shell=True,stdout=subprocess.PIPE,universal_newlines=True).communicate()[0]
    gpu_avail = set([str(i) for i in range(8)])
    for line in gpu_stat.split('\n'):
        if 'python' in line:
            if line.split()[1] in gpu_avail:
                gpu_avail.remove(line.split()[1])
            if len(gpu_avail) == 0:
                gpu_selected = -2
            else:
                gpu_selected = sorted(list(gpu_avail))[0]
    if gpu_selected == -1:
        gpu_selected = '0'

if int(gpu_selected) >= 0:
    os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"]=str(gpu_selected)
    GPU_MEM_FRACTION = 0.8
else:
    os.environ["CUDA_VISIBLE_DEVICES"]="-1"

f_mean = lambda l: sum(l)/len(l)

_ACT = {'lin': lambda x:x,
        'relu': tf.nn.relu}


DTYPE = tf.float32 if FLAGS.dtype=='s' else tf.float64
FNAME_RET = '__ret.pickle'
