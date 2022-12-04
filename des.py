from itertools import zip_longest

from bitarray import bitarray

# Permutation and translation tables for DES
__pc1 = [56, 48, 40, 32, 24, 16, 8,
         0, 57, 49, 41, 33, 25, 17,
         9, 1, 58, 50, 42, 34, 26,
         18, 10, 2, 59, 51, 43, 35,
         62, 54, 46, 38, 30, 22, 14,
         6, 61, 53, 45, 37, 29, 21,
         13, 5, 60, 52, 44, 36, 28,
         20, 12, 4, 27, 19, 11, 3
         ]

# number left rotations of pc1
__left_rotations = [
    1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1
]

# permuted choice key (table 2)
__pc2 = [
    13, 16, 10, 23, 0, 4,
    2, 27, 14, 5, 20, 9,
    22, 18, 11, 3, 25, 7,
    15, 6, 26, 19, 12, 1,
    40, 51, 30, 36, 46, 54,
    29, 39, 50, 44, 32, 47,
    43, 48, 38, 55, 33, 52,
    45, 41, 49, 35, 28, 31
]

# initial permutation IP
__ip = [57, 49, 41, 33, 25, 17, 9, 1,
        59, 51, 43, 35, 27, 19, 11, 3,
        61, 53, 45, 37, 29, 21, 13, 5,
        63, 55, 47, 39, 31, 23, 15, 7,
        56, 48, 40, 32, 24, 16, 8, 0,
        58, 50, 42, 34, 26, 18, 10, 2,
        60, 52, 44, 36, 28, 20, 12, 4,
        62, 54, 46, 38, 30, 22, 14, 6
        ]

# Expansion table for turning 32 bit blocks into 48 bits
__expansion_table = [
    31, 0, 1, 2, 3, 4,
    3, 4, 5, 6, 7, 8,
    7, 8, 9, 10, 11, 12,
    11, 12, 13, 14, 15, 16,
    15, 16, 17, 18, 19, 20,
    19, 20, 21, 22, 23, 24,
    23, 24, 25, 26, 27, 28,
    27, 28, 29, 30, 31, 0
]

# The (in)famous S-boxes

# S1
S1 = [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
      [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
      [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
      [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]]

# S2
S2 = [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
      [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
      [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
      [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]]

# S3
S3 = [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
      [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
      [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
      [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]]

# S4
S4 = [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
      [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
      [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
      [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]]

S5 = [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
      [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
      [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
      [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]]

S6 = [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
      [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
      [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
      [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]]

S7 = [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
      [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
      [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
      [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]]

# S8
S8 = [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
      [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
      [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
      [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]

# 32-bit permutation function P used on the output of the S-boxes
__p = [
    15, 6, 19, 20, 28, 11,
    27, 16, 0, 14, 22, 25,
    4, 17, 30, 9, 1, 7,
    23, 13, 31, 26, 2, 8,
    18, 12, 29, 5, 21, 10,
    3, 24
]

# final permutation IP^-1
__fp = [
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
    32, 0, 40, 8, 48, 16, 56, 24
]


def get_string_binary(string: str, encoding: str):
    bits = bitarray()
    bits.frombytes(string.encode(encoding))
    return bits.to01()


def grouper(n, iterable, padvalue="0"):
    grouped = zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)
    blocks = []
    for group in grouped:
        blocks.append("".join(group))
    return blocks


def initial_permutation(block: str):
    out_block = ""
    for index in __ip:
        out_block += block[index]
    return out_block


def split_on_l_r(p_block: str):
    return p_block[:32], p_block[32:]


def expand_function(right_part: str) -> str:
    output = ""
    for index in __expansion_table:
        output += right_part[index]
    return output


def xor_strings(expanded_block: str, key: str) -> str:
    output = ""
    for a, b in zip(expanded_block, key):
        if (a == "0" and b == "0") or (a == "1" and b == "1"):
            output += "0"
        else:
            output += "1"
    return output


def encryption_f(right_part: str, key: str):
    expanded_block = expand_function(right_part)
    xored = xor_strings(expanded_block, key)
    six_bit_blocks = grouper(6, xored)
    compressed_block = ""
    counter = 0
    for six_bit_block in six_bit_blocks:
        row = int(six_bit_block[0] + six_bit_block[5], 2)
        col = int(six_bit_block[1] + six_bit_block[2] + six_bit_block[3] + six_bit_block[4], 2)
        if counter == 0:
            s_box = S1
        elif counter == 1:
            s_box = S2
        elif counter == 2:
            s_box = S3
        elif counter == 3:
            s_box = S4
        elif counter == 4:
            s_box = S5
        elif counter == 5:
            s_box = S6
        elif counter == 6:
            s_box = S7
        elif counter == 7:
            s_box = S8
        else:
            raise IndexError("Такого S-блока не существует")

        compressed_block += "{0:04b}".format(s_box[row][col])
        counter += 1
    p_compressed_block = ""
    for index in __p:
        p_compressed_block += compressed_block[index]
    return p_compressed_block


def prepare_key(key: str) -> tuple[str, str]:
    output = ""
    for index in __pc1:
        output += key[index]
    return output[:28], output[28:]


def twist_key(key: str, iteration: int):
    rotation = __left_rotations[iteration]
    return key[rotation:] + key[:rotation]


def second_key_permutation(c_key: str, d_key: str):
    full_key = c_key + d_key
    output = ""
    for index in __pc2:
        output += full_key[index]
    return output


def generate_keys(key: str):
    prepared_key = prepare_key(key)
    unprepared_keys = []
    for index in __left_rotations:
        unprepared_keys.append((twist_key(prepared_key[0], index), twist_key(prepared_key[1], index)))
        prepared_key = (twist_key(prepared_key[0], index), twist_key(prepared_key[1], index))

    final_keys = []
    for unprepared_key in unprepared_keys:
        final_key = second_key_permutation(unprepared_key[0], unprepared_key[1])
        final_keys.append(final_key)

    return final_keys


def final_permutation(final_block: str):
    output = ""
    for index in __fp:
        output += final_block[index]
    return output


def des_encrypt(key: str, block: str):
    keys = generate_keys(key)
    permuted_block = initial_permutation(block)
    l_part, r_part = split_on_l_r(permuted_block)
    for i in range(16):
        l_part, r_part = r_part, xor_strings(l_part, encryption_f(r_part, keys[i]))
    result = r_part + l_part
    return final_permutation(result)


def des_decrypt(key: str, block: str):
    keys = generate_keys(key)
    permuted_block = initial_permutation(block)
    l_part, r_part = split_on_l_r(permuted_block)
    for i in range(15, -1, -1):
        l_part, r_part = r_part, xor_strings(l_part, encryption_f(r_part, keys[i]))
    result = r_part + l_part
    return final_permutation(result)


def des_cfb_encrypt(iv: str, message: str, key: str):
    blocks = grouper(64, message)
    output = ""
    shift_register = iv
    for block in blocks:
        xored = xor_strings(block, des_encrypt(key, shift_register))
        output += xored
        shift_register = xored
    return output


def des_cfb_decrypt(iv: str, message: str, key: str):
    blocks = grouper(64, message)
    output = ""
    shift_register = iv
    for block in blocks:
        xored = xor_strings(block, des_encrypt(key, shift_register))
        output += xored
        shift_register = block
    return output
