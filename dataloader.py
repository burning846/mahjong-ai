import torchvision.transforms as transforms
import numpy as np
import torch.utils.data as data
import pickle

class Mahjong(data.Dataset):
    def __init__(self):
        super(Mahjong, self).__init__()
        self.data = pickle.load(open('discard_train/1.pkl', 'rb'))
        self.label = pickle.load(open('discard_label/1.pkl', 'rb'))
        for i in range(2, 100):
            data = pickle.load(open('discard_train/%d.pkl' % i, 'rb'))
            label = pickle.load(open('discard_label/%d.pkl' % i, 'rb'))
            self.data = np.concatenate([self.data, data], axis=0)
            self.label = np.concatenate([self.label, label], axis=0)
        self.test_data = pickle.load(open('discard_train/0.pkl', 'rb'))
        self.test_label = pickle.load(open('discard_label/0.pkl', 'rb'))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return transforms.ToTensor()(self.data[index].transpose(1,2,0)),  transforms.ToTensor()(self.label[index])

    def get_fixed(self):
        return self.test_data, self.test_label