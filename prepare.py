import numpy as np
import os
import h5py
from config import cfg
from utils import get_mean_std
from data import SEIDataset
import pickle
def gen_dataset(data_dir, saved_file_name, sample_len, train_sample_num, test_sample_num, train_test_from_same=True, test_data_dir=None):
    train_label_index_dict = {}
    test_label_index_dict = {}
    if train_test_from_same:
        files = os.listdir(data_dir)
        for file in files:
            if file.split('.')[1] != 'dat':
                continue
            print('processing {} ...'.format(file))
            with open(os.path.join(data_dir, file), 'rb') as f:
                label_index = float(file.split('.')[0])
                data = np.fromfile(f, dtype=np.float64)
                data = data[0:] 
                I = data[0:data.size:2]
                Q = data[1:data.size:2]
                data_len = min(I.size, Q.size)
                I = I[0:data_len]
                Q = Q[0:data_len]
                IQ = np.concatenate(([I], [Q]), axis=0)
                start_index = 0
                samples = []
                labels = []
                numa=0
                while start_index + sample_len < data_len and numa<cfg['sum']:
                    sample = IQ[:, start_index:start_index+sample_len]
                    start_index += sample_len - cfg['sample_overlap']
                    label = np.array([label_index], dtype=np.float32)
                    samples.append(sample)
                    labels.append(label)
                shuffled_index = list(range(cfg['sum']))
                train_index = shuffled_index[:train_sample_num]
                test_index = shuffled_index[train_sample_num:train_sample_num+test_sample_num]
                with h5py.File(saved_file_name, 'a') as hf:  
                    hf['train_data'].resize(hf['train_data'].shape[0] + len(train_index), axis=0)
                    hf['train_label'].resize(hf['train_label'].shape[0] + len(train_index), axis=0)
                    hf['train_data'][-len(train_index):] = [samples[i] for i in train_index]
                    hf['train_label'][-len(train_index):] = [labels[i] for i in train_index]
                    for i in train_index:
                        if labels[i][0] not in train_label_index_dict.keys():
                            train_label_index_dict[labels[i][0]] = [i]
                        else:
                            train_label_index_dict[labels[i][0]].append(i)
                    hf['test_data'].resize(hf['test_data'].shape[0] + len(test_index), axis=0)
                    hf['test_label'].resize(hf['test_label'].shape[0] + len(test_index), axis=0)
                    hf['test_data'][-len(test_index):] = [samples[i] for i in test_index]
                    hf['test_label'][-len(test_index):] = [labels[i] for i in test_index]
                    for i in test_index:
                        if labels[i][0] not in test_label_index_dict.keys():
                            test_label_index_dict[labels[i][0]] = [i]
                        else:
                            test_label_index_dict[labels[i][0]].append(i)
                print('generating {} train samples, {} test samples'.format(len(train_index), len(test_index)))

    
    
