import torch
from tqdm import tqdm
import os
import numpy as np
from model import Network
import torch.utils.data as data
from dataloader import Mahjong
from tensorboardX import SummaryWriter
from torch.nn.init import xavier_uniform
import torch.nn.functional as F

print(1)
batch_size = 1000

dataset = Mahjong()
net = Network()

def weights_init(m):
    classname=m.__class__.__name__
    if classname.find('Conv') != -1:
        xavier_uniform(m.weight.data)
        xavier_uniform(m.bias.data)
net.apply(weights_init)

print(2)

dataLoader = torch.utils.data.DataLoader(dataset=dataset, batch_size=batch_size, num_workers=2, shuffle=True)
optim = torch.optim.Adam(net.parameters(), lr=0.1, betas=(0.5, 0.999))

fixed_x, fixed_label = dataset.get_fixed()

print(3)

for epoch in range(100):
    for i, data in tqdm(enumerate(dataLoader, 0)):
        net.zero_grad()
        x = data[0]
        label = data[1]
        y = net(x)
        loss = F.cross_entropy(y, label)
        loss.backward()
        optim.step()

        print('loss: ', loss.mean())

    test_y = net(fixed_x)
    real = torch.argmax(fixed_label)
    predict = torch.argmax(test_y, dim=1)
    acc = torch.sum(predict == real) / len(real)
    print('acc: ', acc)

