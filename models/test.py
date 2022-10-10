import torch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.lstm import LSTMGenerator

model = LSTMGenerator(128, 2)
model.load_state_dict(torch.load('models/trained/lstm2_hs128_bs128_ep100.pt'))
    
print(model.predict_max('lemon', 10))
