import torch
from torch.nn.functional import softmax
import numpy as np

from utils import encode_onehot, alphabet, letter_dict
from lstm import LSTMGenerator

model = LSTMGenerator(128, 2)
model.load_state_dict(torch.load('models/trained/lstm2_hs128_bs128_ep100.pt'))

def predict(model, seed, num_letters):
    model.eval()

    num_predict = num_letters - len(seed)
    state_h = torch.zeros(model.num_layers, model.hidden_size)
    state_c = torch.zeros(model.num_layers, model.hidden_size)

    name = seed
    for i in range(num_predict):
        x = encode_onehot(name).T
        x = torch.from_numpy(x).float()
        y, (state_h, state_c) = model(x, (state_h, state_c), train=False)
        print(i, y)
        y_next = y[-1, :]
        probs_next = softmax(y_next, dim=0).detach().numpy()
        letter_ind = np.random.choice(26, p=probs_next)
        letter = letter_dict[letter_ind]
        name += letter

    return name
    
print(predict(model, 'bya', 9))
