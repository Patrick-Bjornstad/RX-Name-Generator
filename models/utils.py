import string
import numpy as np

alphabet = list(string.ascii_lowercase)
label_dict = {letter: label for label, letter in enumerate(alphabet)}

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
