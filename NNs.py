import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch as T
import os
import numpy as np

class DQ_nn(nn.Module):
    def __init__(self,lr, n_actions, input_dims, name, chkpt_dir):
        # Inherit properties of nn object to this object we are creating
        super(DQ_nn, self).__init__()
        # Where to save models
        self.checkpoint_dir = chkpt_dir
        self.checkpoint_file = os.path.join(self.checkpoint_dir, name)

        # nn layers that we will use
        # Input_dims[0] is the number of chanels
        self.conv1 = nn.Conv2d(input_dims[0], 32, (8, 8), stride=4)
        self.conv2 = nn.Conv2d(32, 64, (4, 4), stride=2)
        self.conv3 = nn.Conv2d(64, 64, (3, 3), stride=1)
        fc_input_dims = self.calculate_conv_output_dims(input_dims)
        self.fullc1 = nn.Linear(fc_input_dims, 512)
        self.fullc2 = nn.Linear(512, n_actions)

        # set optimizer and loss function
        self.optimizer = optim.RMSprop(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()

        # Set the device where we will run the code (GPU or CPU)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def calculate_conv_output_dims(self,input_dims):
        state = T.zeros(1, *input_dims)
        dims = self.conv1(state)
        dims = self.conv2(dims)
        dims = self.conv3(dims)
        return int(np.prod(dims.size()))

    def forward(self, state):
        # Define forward pass of the nn
        conv1 = F.relu(self.conv1(state))
        conv2 = F.relu(self.conv2(conv1))
        conv3 = F.relu(self.conv3(conv2))
        # conv3 shape is BS x n_filters x H x W
        conv_state = conv3.view(conv3.size()[0], -1)
        fc1 = F.relu(self.fullc1(conv_state))
        actions = self.fullc2(fc1)

        return actions
    
    def save_checkpoint(self):
        print('...Saving checkpoint...')
        T.save(self.state_dict(), self.checkpoint_file)

    def load_checkpoint(self):
        print('...Loading checkpoint...')
        self.load_state_dict(T.load(self.checkpoint_file))