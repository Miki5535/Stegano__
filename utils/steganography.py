from PIL import Image
import numpy as np


# Encryption functions (AES, RSA, Blowfish, Fernet)
# def binary_to_string2(binary):
#     """แปลง binary string กลับเป็นข้อความ"""
#     try:
#         binary = binary.replace(' ', '')
#         return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
#     except Exception as e:
#         print(f"Error converting from binary: {str(e)}")
#         return None

def string_to_binary(message):
    return ''.join(format(byte, '08b') for byte in message.encode('utf-8'))

def binary_to_string(binary):
    try:
        return "<font color='green'>"+bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "<font color='red'>ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"
    
def binary_to_string2(binary):
    try:
        return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"

def hide_message(image_path, message, output_path):
    img = Image.open(image_path)
    arr = np.array(img)

    binary_message = string_to_binary(message) + '0' * 8

    idx = 0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            for k in range(min(3, arr.shape[2])):  # RGB channels
                if idx < len(binary_message):
                    arr[i, j, k] = (arr[i, j, k] & 254) | int(binary_message[idx])
                    idx += 1
                if idx >= len(binary_message):
                    break
            if idx >= len(binary_message):
                break
        if idx >= len(binary_message):
            break

    output_format = 'PNG' if output_path.lower().endswith('.png') else 'JPG'
    Image.fromarray(arr).save(output_path, format=output_format)

def retrieve_message(image_path):
    img = Image.open(image_path)
    arr = np.array(img)

    binary_message = ""
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            for k in range(min(3, arr.shape[2])):  # RGB channels
                binary_message += str(arr[i, j, k] & 1)
                if len(binary_message) % 8 == 0 and len(binary_message) >= 8:
                    if binary_message[-8:] == '00000000':
                        return binary_to_string(binary_message[:-8])
    return None



