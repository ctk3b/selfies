from typing import Dict, List, Tuple, Union

from selfies.utils.selfies_utils import len_selfies, split_selfies


def selfies_to_encoding(
        selfies: str,
        vocab_stoi: Dict[str, int],
        pad_to_len: int = -1,
        enc_type: str = 'both'
) -> Union[List[int], List[List[int]], Tuple[List[int], List[List[int]]]]:
    """Converts a SELFIES into its label (integer) and/or one-hot encoding.

    A label encoded output will be a list of size ``(N,)`` and a
    one-hot encoded output will be a list of size ``(N, len(vocab_stoi))``;
    where ``N`` is the symbol length of the (potentially padded) SELFIES.
    Note that SELFIES uses the special padding symbol ``[nop]``.

    :param selfies: the SELFIES to be encoded.
    :param vocab_stoi: a dictionary that maps SELFIES symbols (the keys)
        to a non-negative index. The indices of the dictionary
        must contiguous, starting from 0.
    :param pad_to_len: the length the SELFIES is be padded to.
        If ``pad_to_len`` is less than or equal to the symbol
        length of the SELFIES, then no padding is added. Defaults to ``-1``.
    :param enc_type: the type of encoding of the output:
        ``label`` or ``one_hot`` or ``both``.
        If the value is ``both``, then a tuple of the label and one-hot
        encoding are returned (in that order). Defaults to ``both``.
    :return: the label encoded and/or one-hot encoded SELFIES.

    :Example:

    >>> import selfies as sf
    >>> sf.selfies_to_encoding("[C][F]", {"[C]": 0, "[F]": 1})
    ([0, 1], [[1, 0], [0, 1]])
    """

    # some error checking
    if enc_type not in ("label", "one_hot", "both"):
        raise ValueError("enc_type must be in ('label', 'one_hot', 'both')")

    # pad with [nop]
    if pad_to_len > len_selfies(selfies):
        selfies += "[nop]" * (pad_to_len - len_selfies(selfies))

    # integer encode
    char_list = split_selfies(selfies)
    integer_encoded = [vocab_stoi[char] for char in char_list]

    if enc_type == "label":
        return integer_encoded

    # one-hot encode
    onehot_encoded = list()
    for index in integer_encoded:
        letter = [0] * len(vocab_stoi)
        letter[index] = 1
        onehot_encoded.append(letter)

    if enc_type == "one_hot":
        return onehot_encoded
    return integer_encoded, onehot_encoded


def encoding_to_selfies(
        encoded: Union[List[int], List[List[int]]],
        vocab_itos: Dict[int, str],
        enc_type: str,
) -> str:
    """Converts a label (integer) or one-hot encoded list into
    a SELFIES string.

    If the input is label encoded, then a list of size ``(N,)`` is
    expected; and if the input is one-hot encoded, then a 2D list of
    size ``(N, len(vocab_itos))`` is expected.

    :param encoded: a label or one-hot encoded list.
    :param vocab_itos: a dictionary that maps non-negative indices (the keys)
        to SELFIES symbols. The indices of the dictionary
        must be contiguous, starting from 0.
    :param enc_type: the type of encoding of the output:
        ``label`` or ``one_hot``.
    :return: the SELFIES string represented by the encoded input.

    :Example:

    >>> import selfies as sf
    >>> one_hot = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    >>> vocab_itos = {0: "[nop]", 1: "[C]", 2: "[F]"}
    >>> sf.encoding_to_selfies(one_hot, vocab_itos, enc_type="one_hot")
    '[C][F][nop]'

    """

    if enc_type not in ("label", "one_hot"):
        raise ValueError("enc_type must be in ('label', 'one_hot')")

    if enc_type == "one_hot":  # Get integer encoding
        integer_encoded = []
        for row in encoded:
            integer_encoded.append(row.index(1))
    else:
        integer_encoded = encoded

    # Integer encoding -> SELFIES
    char_list = [vocab_itos[i] for i in integer_encoded]
    selfies = "".join(char_list)

    return selfies


def batch_selfies_to_flat_hot(
        selfies_batch: List[str],
        vocab_stoi: Dict[str, int],
        pad_to_len: int = -1,
) -> List[List[int]]:
    """Converts a list of SELFIES into a list of
    flattened one-hot encodings.

    Returned is a list of size ``(batch_size, N * len(vocab_stoi))``;
    where ``N`` is the symbol length of the (potentially padded) SELFIES.
    Note that SELFIES uses the special padding symbol ``[nop]``.

    :param selfies_batch: a list of SELFIES to be converted.
    :param vocab_stoi: a dictionary that maps SELFIES symbols (the keys)
        to a non-negative index. The indices of the dictionary
        must contiguous, starting from 0.
    :param pad_to_len: the length that each SELFIES is be padded to.
        If ``pad_to_len`` is less than or equal to the symbol
        length of the SELFIES, then no padding is added. Defaults to ``-1``.
    :return: the flattened one-hot encoded representations of the SELFIES
        from the batch. This is a 2D list of size
        ``(batch_size, N * len(vocab_stoi))``.

    :Example:

    >>> import selfies as sf
    >>> batch = ["[C]", "[C][C]"]
    >>> vocab_stoi = {"[nop]": 0, "[C]": 1}
    >>> sf.batch_selfies_to_flat_hot(batch, vocab_stoi, 2)
    [[0, 1, 1, 0], [0, 1, 0, 1]]

    """

    hot_list = list()

    for selfies in selfies_batch:
        one_hot = selfies_to_encoding(selfies, vocab_stoi, pad_to_len,
                                      enc_type="one_hot")
        flattened = [elem for vec in one_hot for elem in vec]
        hot_list.append(flattened)

    return hot_list


def batch_flat_hot_to_selfies(
        one_hot_batch: List[List[int]],
        vocab_itos: Dict[int, str],
) -> List[str]:
    """Converts a batch of flattened one-hot encodings into
    a list of SELFIES.

    We expect ``one_hot_batch`` to be a list of size ``(batch_size, S)``,
    where ``S`` is divisible by the length of the vocabulary.

    :param one_hot_batch: a list of flattened one-hot encoded representations.
    :param vocab_itos: a dictionary that maps non-negative indices (the keys)
        to SELFIES symbols. We expect the indices of the dictionary
        to be contiguous and starting from 0.
    :return: a list of SELFIES strings.

    :Example:

    >>> import selfies as sf
    >>> batch = [[0, 1, 1, 0], [0, 1, 0, 1]]
    >>> vocab_itos = {0: "[nop]", 1: "[C]"}
    >>> sf.batch_flat_hot_to_selfies(batch, vocab_itos)
    ['[C][nop]', '[C][C]']

    """

    selfies_list = []

    for flat_one_hot in one_hot_batch:

        # Reshape to an N x M array where each column represents an alphabet
        # entry and each row is a position in the selfies
        one_hot = []

        M = len(vocab_itos)
        if len(flat_one_hot) % M != 0:
            raise ValueError("size of vector in one_hot_batch not divisible "
                             "by the length of the vocabulary.")
        N = len(flat_one_hot) // M

        for i in range(N):
            one_hot.append(flat_one_hot[M * i: M * (i + 1)])

        selfies = encoding_to_selfies(one_hot, vocab_itos, enc_type="one_hot")
        selfies_list.append(selfies)

    return selfies_list
