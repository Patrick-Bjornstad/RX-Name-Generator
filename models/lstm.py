import json
import torch
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader

from utils import encode_label, encode_onehot

# Assign to GPU if there is one available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# Define our dataset class
class BrandNameDataset(Dataset):

    def __init__(self, names_array):
        self.names_array = names_array
        
    def __len__(self):
        return len(self.names_array)
    
    def __getitem__(self, idx):
        name = self.names_array[idx]
        encoded_x = encode_onehot(name)
        encoded_y = encode_label(name)
        return encoded_x, encoded_y


# Define the model
class LSTMGenerator(nn.Module):

    def __init__(self, hidden_size, num_layers=1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            26,                     # each character will be a one hot encoded vector of length 26
            self.hidden_size,       # num of features in the hidden state, main hyperparameter
            self.num_layers,        # only use a single LSTM by default
            batch_first=True
        )
        self.lin = nn.Linear(hidden_size, 26)

    def forward(self, x, prev_states=None):

        output, states = self.lstm(x, prev_states)
        x = x.reshape(-1, self.hidden_size)
        output = self.lin(x)

        return output, states


# Define our training function
def train(dataset, model, batch_size, epochs, lr):

    model = model.to(device)
    dataloader = DataLoader(dataset, batch_size=batch_size)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(epochs):

        model.train()
        train_loss = 0
        states = None

        for batch_num, (encoded_x, encoded_y) in enumerate(dataloader):

            encoded_x.to(device)
            encoded_y.to(device)

            optimizer.zero_grad()
            pred_y, states = model(encoded_x, states)
            loss = loss_fn(pred_y, encoded_y)

            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            print({'epoch': epoch, 'batch': batch_num, 'loss': loss.item()})
            

# uh

with open('../data/names_clean.json', 'r') as f:
    names = json.load(f)

dataset = BrandNameDataset(names)
model = LSTMGenerator(64, 1)

train(dataset, model, 128, 100, 0.01)
