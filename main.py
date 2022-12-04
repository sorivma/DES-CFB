from des import *

iv = "1111000111001000000001101110111001000010011000101000000001011101"

str_msg_representation = input("Введите текст сообщения: ")
str_key_representation = input("Веедите ключ: ")
bin_msg = get_string_binary(str_msg_representation, "UTF-8")
bin_key = get_string_binary(str_key_representation, "UTF-8")

if len(bin_key) > 64:
    bin_key = bin_key[:64]
if len(bin_key) < 64:
    bin_key = grouper(64, bin_key)[0]

encryption = des_cfb_encrypt(iv, bin_msg, bin_key)
print(f"Зашифрованное сообщение: {bitarray(encryption).tobytes().decode('latin-1')}")
decryption = des_cfb_decrypt(iv, encryption, bin_key)
decryption = decryption.rstrip("0")
print(f"Расшифрованное сообщение: {bitarray(decryption).tobytes().decode('UTF-8')}")
