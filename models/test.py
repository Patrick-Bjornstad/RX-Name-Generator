import torch
import sys
import os

# Custom module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.lstm import LSTMGenerator

# Load a pretrained model
model = LSTMGenerator(128, 2)
model.load_state_dict(torch.load('models/trained/lstm2_hs128_bs128_ep100_sw0-05.pt'))
    
# Predict some new name
print(model.predict('nicm'))
