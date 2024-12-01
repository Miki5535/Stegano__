from random import seed
from PIL import Image
import numpy as np
import cv2
from scipy.fftpack import dct, idct
import os



def string_to_binary(message):
    return ''.join(format(byte, '08b') for byte in message.encode('utf-8'))

def binary_to_string(binary):
    try:
        return "<font color='green'>"+bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "<font color='red'>ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"
    

def binary_to_string_P(binary):
    try:
        # แปลง binary กลับเป็น bytes แล้วถอดรหัสเป็น UTF-8
        byte_data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        return "<font color='green'>"+byte_data.decode('utf-8')
    except Exception as e:
        return f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}"

def binary_to_string_T(binary):
    try:
        # ตัดข้อมูล Binary ให้เป็นชุดละ 8 บิต
        byte_data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        # ถอดรหัส UTF-8
        return byte_data.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"ข้อผิดพลาดในการถอดรหัส UTF-8: {str(e)}")
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"
    except ValueError as e:
        print(f"ข้อผิดพลาดในการแปลง Binary: {str(e)}")
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"

    
def binary_to_string2(binary):
    try:
        return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"

def hide_message_lsb_from_steganography(image_path, message, output_path):
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


def hide_message_transform_domain_from_steganography(image_path, message, output_path):
    binary_message = string_to_binary(message) + '0' * 8  # เพิ่มตัวจบข้อความ
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    # แปลงภาพเป็น DCT
    dct_transformed = dct(dct(img.T, norm='ortho').T, norm='ortho')
    
    # ฝังข้อความในค่าสัมประสิทธิ์ DCT
    idx = 0
    for i in range(1, dct_transformed.shape[0]):  # เริ่มจาก i=1 เพื่อหลีกเลี่ยงค่าสัมประสิทธิ์ DC
        for j in range(1, dct_transformed.shape[1]):  # เริ่มจาก j=1
            if idx < len(binary_message):
                if dct_transformed[i, j] != 0:  # เลี่ยงตำแหน่งที่ค่าเป็น 0
                    dct_transformed[i, j] += int(binary_message[idx]) - (dct_transformed[i, j] % 2)
                    idx += 1
            else:
                break
        if idx >= len(binary_message):
            break

    # แปลงกลับเป็นภาพ
    reconstructed_img = idct(idct(dct_transformed.T, norm='ortho').T, norm='ortho')
    reconstructed_img = np.clip(reconstructed_img, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, reconstructed_img)




def hide_message_masking_filtering_from_steganography(image_path, message, output_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    # แปลงข้อความเป็นบิต
    message_bits = ''.join(format(ord(i), '08b') for i in message)
    bit_idx = 0

    # ฝังข้อความในบริเวณขอบที่ชัดเจน
    edges = cv2.Canny(img, 100, 200)
    for i in range(edges.shape[0]):
        for j in range(edges.shape[1]):
            if edges[i, j] > 0 and bit_idx < len(message_bits):
                new_value = (img[i, j, 0] & ~1) | int(message_bits[bit_idx])
                img[i, j, 0] = np.clip(new_value, 0, 255)  # บังคับให้อยู่ในช่วง 0-255
                bit_idx += 1

    cv2.imwrite(output_path, img)




def hide_message_palette_based_from_steganography(image_path, message, output_path):
    # แปลงภาพต้นฉบับเป็น PNG
    img = Image.open(image_path).convert("RGB")
    temp_png_path = "temp_image.png"
    img.save(temp_png_path, format="PNG")
    
    try:
        # เปิดภาพ PNG ที่แปลงแล้วและแปลงเป็น Palette-based
        img = Image.open(temp_png_path).convert("P")
        palette = img.getpalette()
        
        # แปลงข้อความเป็น binary พร้อมตัวจบข้อความ
        binary_message = string_to_binary(message) + '0' * 8

        # ฝังข้อความลงในพาเลต
        for i in range(len(binary_message)):
            if i < len(palette):
                palette[i] = (palette[i] & ~1) | int(binary_message[i])  # ฝังบิตลงใน palette

        img.putpalette(palette)
        img.save(output_path, format="PNG")
        print(f"ข้อความถูกฝังสำเร็จใน {output_path}")

    finally:
        # ลบไฟล์ชั่วคราว
        if os.path.exists(temp_png_path):
            os.remove(temp_png_path)
            print(f"ลบไฟล์ชั่วคราว {temp_png_path} สำเร็จ")





def hide_message_spread_spectrum_from_steganography(image_path, message, output_path):
    # อ่านภาพ
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    # แปลงข้อความเป็น Binary พร้อมตัวจบข้อความ
    message_bits = ''.join(format(ord(c), '08b') for c in message) + '0' * 8
    
    # สร้าง Noise Signal (Pseudo-Random Binary Sequence)
    np.random.seed(seed)
    noise = np.random.choice([0, 1], size=img.shape[:2], p=[0.5, 0.5]).astype(np.uint8)

    # ฝังข้อความโดยใช้ XOR กับ Noise Signal
    idx = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if idx < len(message_bits):
                bit = int(message_bits[idx])
                img[i, j, 0] = (img[i, j, 0] & ~1) | (bit ^ noise[i, j])  # ฝังข้อความในช่องสีน้ำเงิน
                idx += 1
            else:
                break
        if idx >= len(message_bits):
            break

    # บันทึกภาพ
    cv2.imwrite(output_path, img)
















def retrieve_message_lsb_from_steganography(image_path):
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


def retrieve_message_transform_domain_from_steganography(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")

    # แปลงกลับเป็น DCT
    dct_transformed = dct(dct(img.T, norm='ortho').T, norm='ortho')
    
    # อ่านข้อความจากค่าสัมประสิทธิ์ DCT
    binary_message = ""
    for i in range(1, dct_transformed.shape[0]):
        for j in range(1, dct_transformed.shape[1]):
            if dct_transformed[i, j] != 0:
                binary_message += str(int(dct_transformed[i, j]) % 2)
                if len(binary_message) % 8 == 0 and binary_message[-8:] == '00000000':  # ตรวจสอบตัวจบ
                    valid_binary_message = binary_message[:-8]  # ตัดตัวจบข้อความ
                    print("Binary ที่เกี่ยวข้อง:", valid_binary_message)
                    return binary_to_string_T(valid_binary_message)

    return "ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"





def retrieve_message_masking_filtering_from_steganography(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")

    # คำนวณขอบภาพ
    edges = cv2.Canny(img, 100, 200)

    # อ่านข้อความจากบริเวณขอบ
    bits = []
    for i in range(edges.shape[0]):
        for j in range(edges.shape[1]):
            if edges[i, j] > 0:
                bits.append(img[i, j, 0] & 1)

    # รวมบิตและแปลงเป็นข้อความ
    byte_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message = ''.join(chr(int(''.join(map(str, byte)), 2)) for byte in byte_list if int(''.join(map(str, byte)), 2) != 0)

    return message


def retrieve_message_palette_based_from_steganography(image_path):
    img = Image.open(image_path).convert("P")
    palette = img.getpalette()

    # อ่านข้อมูลจาก palette
    binary_message = ''.join(str(color & 1) for color in palette[:len(palette)])

    # แปลงจาก binary เป็นข้อความ
    if '00000000' in binary_message:
        binary_message = binary_message.split('00000000')[0]  # ตัดตัวจบข้อความ
        return binary_to_string_P(binary_message)  # แปลงกลับเป็นข้อความ
    else:
        return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"




def retrieve_message_spread_spectrum_from_steganography(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")

    # สร้าง Noise Signal (Pseudo-Random Binary Sequence)
    np.random.seed(seed)
    noise = np.random.choice([0, 1], size=img.shape[:2], p=[0.5, 0.5])

    # อ่านข้อความที่ซ่อนอยู่
    bits = []
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            bit = (img[i, j, 0] & 1) ^ noise[i, j]
            bits.append(bit)

    # แปลงบิตเป็นข้อความ
    binary_message = ''.join(map(str, bits))
    if '00000000' in binary_message:
        binary_message = binary_message.split('00000000')[0]  # ตัดตัวจบข้อความ
        byte_list = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
        try:
            return ''.join(chr(int(byte, 2)) for byte in byte_list)
        except ValueError:
            return "ข้อความที่ซ่อนไว้ไม่ถูกต้อง"
    else:
        return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"
