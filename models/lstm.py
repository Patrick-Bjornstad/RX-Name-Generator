import json
import torch
from torch import nn, optim, index_select
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from torch.nn.functional import softmax
import numpy as np

from utils import encode_label, encode_onehot, collate_pad, letter_dict

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

    def forward(self, x, prev_states, train=True):

        x, (state_h, state_c) = self.lstm(x, prev_states)
        if train:
            x, _ = pad_packed_sequence(x, batch_first=True, padding_value=-1)
        x = x.reshape(-1, self.hidden_size)
        output = self.lin(x)

        return output, (state_h, state_c)

    def predict(self, seed, num_letters):
        self.eval()

        num_predict = num_letters - len(seed)
        state_h = torch.zeros(self.num_layers, self.hidden_size)
        state_c = torch.zeros(self.num_layers, self.hidden_size)

        name = seed
        for i in range(num_predict):
            x = encode_onehot(name).T
            x = torch.from_numpy(x).float()
            y, (state_h, state_c) = self(x, (state_h, state_c), train=False)
            y_next = y[-1, :]
            probs_next = softmax(y_next, dim=0).detach().numpy()
            letter_ind = np.random.choice(26, p=probs_next)
            letter = letter_dict[letter_ind]
            name += letter

        return name


# Define our training function
def train(dataset, model, batch_size, epochs, lr):

    model = model.to(device)
    dataloader = DataLoader(dataset, batch_size=batch_size, collate_fn=collate_pad)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(epochs):

        model.train()
        train_loss = 0
        state_h = torch.zeros(model.num_layers, batch_size, model.hidden_size).to(device)
        state_c = torch.zeros(model.num_layers, batch_size, model.hidden_size).to(device)

        for batch_num, (batch_x, batch_y) in enumerate(dataloader):

            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            pred_y, (state_h, state_c) = model(batch_x, (state_h, state_c))
            batch_y_flat = batch_y.flatten()
            padded_indices = (batch_y_flat != -1).nonzero().flatten()
            pred_y_nopads = index_select(pred_y, 0, padded_indices)
            batch_y_flat_nopads = index_select(batch_y_flat, 0, padded_indices)
            loss = loss_fn(pred_y_nopads[0:-1,:], batch_y_flat_nopads[1:])

            state_h = state_h.detach()
            state_c = state_c.detach()

            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            print(device, {'epoch': epoch, 'batch': batch_num, 'loss': loss.item()})
            

# Train and export a model if the file is called directly
def main():

    hidden_size = 128
    lstm_layers = 2
    batch_size = 128
    epochs = 100
    learning_rate = 0.01

    mname = f'lstm{lstm_layers}_hs{hidden_size}_bs{batch_size}_ep{epochs}'

    with open('data/names_clean.json', 'r') as f:
        names = json.load(f)

    dataset = BrandNameDataset(names)
    model = LSTMGenerator(hidden_size, lstm_layers)

    train(dataset, model, batch_size, epochs, learning_rate)
    torch.save(model.state_dict(), f'models/trained/{mname}.pt')


if __name__ == '__main__':
    main()
