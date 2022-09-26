import string
import numpy as np
from torch import from_numpy
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence

alphabet = list(string.ascii_lowercase)
label_dict = {letter: index for index, letter in enumerate(alphabet)}
letter_dict = {index: letter for index, letter in enumerate(alphabet)}

def encode_char_onehot(char):
    index = label_dict[char]
    return np.eye(1, 26, index)[0]

def encode_onehot(string):
    encoded = list(map(encode_char_onehot, list(string)))
    encoded = np.array(encoded)
    encoded = encoded.T
    return encoded

def encode_label(string):
    encoded = [label_dict[ch] for ch in list(string)]
    encoded = np.array(encoded)
    return encoded

def collate_pad(batch):
    x_arr = [from_numpy(elem[0].T) for elem in batch]
    y_arr = [from_numpy(elem[1]) for elem in batch]
    lengths = [len(y) for y in y_arr]
    batch_x = pad_sequence(x_arr, batch_first=True, padding_value=-1)
    batch_y = pad_sequence(y_arr, batch_first=True, padding_value=-1)
    batch_x = pack_padded_sequence(batch_x, lengths, batch_first=True, enforce_sorted=False)
    batch_x = batch_x.float()
    batch_y = batch_y.long()
    return batch_x, batch_y
