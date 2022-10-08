import torch

from lstm import LSTMGenerator

model = LSTMGenerator(128, 2)
model.load_state_dict(torch.load('models/trained/lstm2_hs128_bs128_ep100.pt'))
    
print(model.predict('lemon', 10))
