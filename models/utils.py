import string
import numpy as np
from torch import from_numpy
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence

# Global variables
ALPHABET = list(string.ascii_lowercase)
LABEL_DICT = {letter: index for index, letter in enumerate(ALPHABET)}
LETTER_DICT = {index: letter for index, letter in enumerate(ALPHABET)}


def encode_char_onehot(char):
    '''
    Encodes a single character using one-hot encoding.

        Parameters:
            char (str): single letter to encode

        Returns:
            encoded (np.array): 1D array representing the one hot encoded vector
    '''

    index = LABEL_DICT[char]
    encoded = np.eye(1, 26, index)[0]
    return encoded


def encode_onehot(string):
    '''
    Encodes an entire (lowercase English alphabet) string using one-hot encoding.

        Parameters:
            string (str): string to encode

        Returns:
            encoded (np.array): 2D array representing a set of one-hot vectors
    '''

    encoded = list(map(encode_char_onehot, list(string)))
    encoded = np.array(encoded)
    encoded = encoded.T
    return encoded


def encode_label(string):
    '''
    Encodes an entire (lowercase English alphabet) string using label encoding.

        Parameters:
            string (str)L string to encode

        Returns:
            encoded (np.array): 1D array representing the string's letters encoded as indices
    '''

    encoded = [LABEL_DICT[ch] for ch in list(string)]
    encoded = np.array(encoded)
    return encoded


def collate_pad(batch):
    '''
    Custom collation function to override the PyTorch default.
    Generates fixed-size batches from variable length inputs using padding.

        Parameters:
            batch (tuple): unmodified single batch in the form of x,y pair
        
        Returns:
            batch_x (torch.Tensor): padded/fixed-length batch of one-hot encoded strings
            batch_y (torch.Tensor): padded/fixed-length batch of label encoded strings
    '''

    x_arr = [from_numpy(elem[0].T) for elem in batch]
    y_arr = [from_numpy(elem[1]) for elem in batch]
    lengths = [len(y) for y in y_arr]
    batch_x = pad_sequence(x_arr, batch_first=True, padding_value=-1)
    batch_y = pad_sequence(y_arr, batch_first=True, padding_value=-1)
    batch_x = pack_padded_sequence(batch_x, lengths, batch_first=True, enforce_sorted=False)
    batch_x = batch_x.float()
    batch_y = batch_y.long()
    return batch_x, batch_y
