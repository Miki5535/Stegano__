from random import seed
from PIL import Image
import numpy as np
import cv2
from scipy.fftpack import dct, idct
import os
from scipy.signal import convolve2d
import struct
import zlib 



def string_to_binary(message):
    return ''.join(format(byte, '08b') for byte in message.encode('utf-8'))

def binary_to_string(binary):
    try:
        return "<font color='green'>"+bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8)).decode('utf-8')
    except UnicodeDecodeError:
        return "<font color='red'>ไม่มีข้อความ หรือ ข้อความไม่ถูกต้อง"
    

def validate_binary(binary):
    # ตรวจสอบความยาวของ Binary และเติมข้อมูลให้ครบ 8 บิต
    if len(binary) % 8 != 0:
        print(f"Warning: Binary data length ({len(binary)}) is not a multiple of 8")
        # เติม 0 เพื่อให้ข้อมูลมีขนาดที่เป็นทวีคูณของ 8
        binary = binary + '0' * (8 - len(binary) % 8)
    return binary

def binary_to_string_P(binary):
    try:
        # ตรวจสอบและเติมข้อมูลให้ครบ
        binary = validate_binary(binary)  # เติมข้อมูลให้ครบ 8 บิต
        
        # แปลง Binary กลับเป็น bytes
        byte_data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        print(f"Decoded Byte Data: {byte_data}")  # Debug
        return "<font color='green'>" + byte_data.decode('utf-8', errors='ignore')  # ใช้ 'ignore' เพื่อข้ามตัวที่ไม่สามารถแปลงได้
    except UnicodeDecodeError as e:
        print(f"Error decoding UTF-8: {e}")  # Debug
        return "<font color='red'>ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debug
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
    img = Image.open(image_path).convert('RGB')  # บังคับเป็น RGB เพื่อลดปัญหา
    arr = np.array(img)

    binary_message = string_to_binary(message) + '0' * 8  # เติม 8 บิตท้ายสุดเป็น 0
    required_bits = len(binary_message)

    height, width, channels = arr.shape
    max_bits = height * width * 3  # ใช้เฉพาะ RGB channels (ไม่รวม Alpha)
    
    if required_bits > max_bits:
        raise ValueError(f"ข้อความยาวเกินไป! ต้องการ {required_bits} บิต แต่ภาพรองรับได้แค่ {max_bits} บิต")

    idx = 0
    for i in range(height):
        for j in range(width):
            for k in range(3):  # ใช้เฉพาะ 3 ช่องสี (RGB)
                if idx < required_bits:
                    arr[i, j, k] = (arr[i, j, k] & 254) | int(binary_message[idx])
                    idx += 1
                if idx >= required_bits:
                    break
            if idx >= required_bits:
                break
        if idx >= required_bits:
            break

    Image.fromarray(arr).save(output_path, format='PNG')
    print(f"ฝังข้อความสำเร็จ! บันทึกที่ {output_path}")

def hide_message_transform_domain_from_steganography(image_path, message, output_path):
    # แปลงข้อความเป็น Binary
    binary_message = string_to_binary(message) + '0' * 8  # เพิ่มตัวจบข้อความ
    print(f"Binary Message: {binary_message[:64]}...")  # Debug: แสดงข้อความบางส่วน
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    print(f"Image Shape: {img.shape}")  # Debug: แสดงขนาดของภาพ
    
    # ตรวจสอบขนาดของภาพเพื่อให้แน่ใจว่าเพียงพอสำหรับการแปลง DCT
    if img.shape[0] < 8 or img.shape[1] < 8:
        raise ValueError("ขนาดของภาพเล็กเกินไปสำหรับการฝังข้อความ")

    # แปลงภาพเป็น DCT
    dct_transformed = dct(dct(img.T, norm='ortho').T, norm='ortho')
    
    print(f"DCT Shape: {dct_transformed.shape}")  # Debug: แสดงขนาดของ DCT

    # ฝังข้อความในค่าสัมประสิทธิ์ DCT
    idx = 0
    for i in range(1, dct_transformed.shape[0]):  # เริ่มจาก i=1 เพื่อหลีกเลี่ยงค่าสัมประสิทธิ์ DC
        for j in range(1, dct_transformed.shape[1]):  # เริ่มจาก j=1
            if idx < len(binary_message):
                if dct_transformed[i, j] != 0:  # เลี่ยงตำแหน่งที่ค่าเป็น 0
                    print(f"Embedding at ({i}, {j}): {dct_transformed[i, j]} -> {int(dct_transformed[i, j]) + int(binary_message[idx]) - (int(dct_transformed[i, j]) % 2)}")  # Debug
                    dct_transformed[i, j] = int(dct_transformed[i, j]) + int(binary_message[idx]) - (int(dct_transformed[i, j]) % 2)
                    idx += 1
            if idx >= len(binary_message):
                break
        if idx >= len(binary_message):
            break

    # แปลงกลับเป็นภาพ
    reconstructed_img = idct(idct(dct_transformed.T, norm='ortho').T, norm='ortho')
    reconstructed_img = np.clip(reconstructed_img, 0, 255).astype(np.uint8)
    
    cv2.imwrite(output_path, reconstructed_img)
    print(f"Image saved to: {output_path}")  # Debug: แสดงที่อยู่ของไฟล์ที่บันทึก

def retrieve_message_transform_domain_from_steganography(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")

    print(f"Image Shape: {img.shape}")  # Debug: แสดงขนาดของภาพ
    
    # แปลงกลับเป็น DCT
    dct_transformed = dct(dct(img.T, norm='ortho').T, norm='ortho')
    
    print(f"DCT Shape: {dct_transformed.shape}")  # Debug: แสดงขนาดของ DCT
    
    # อ่านข้อความจากค่าสัมประสิทธิ์ DCT
    binary_message = ""
    for i in range(1, dct_transformed.shape[0]):
        for j in range(1, dct_transformed.shape[1]):
            if dct_transformed[i, j] != 0:
                bit = str(int(dct_transformed[i, j]) % 2)
                binary_message += bit
                print(f"Extracting bit at ({i}, {j}): {bit}")  # Debug
                if len(binary_message) % 8 == 0 and binary_message[-8:] == '00000000':  # ตรวจสอบตัวจบ
                    print(f"End of message detected.")  # Debug: ตรวจพบจุดสิ้นสุดข้อความ
                    try:
                        return binary_to_string_T(binary_message[:-8])  # ตัดตัวจบและแปลงข้อความ
                    except ValueError as e:
                        print(f"Error decoding message: {e}")
                        return "ข้อความไม่สามารถถอดรหัสได้"
    
    return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"


def hide_message_masking_filtering_from_steganography(image_path, message, output_path):
    """ซ่อนข้อความในบริเวณขอบภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    # แปลงข้อความเป็นบิต + เพิ่มตัวกำหนดความยาว
    message_bits = string_to_binary(message)
    length_bits = format(len(message_bits), '032b')  # 32-bit เก็บความยาว
    full_message = length_bits + message_bits  # ใส่ความยาวข้อความไว้ต้นสุด
    bit_idx = 0

    # ตรวจจับขอบด้วย Canny
    edges = cv2.Canny(cv2.imread(image_path, cv2.IMREAD_GRAYSCALE), 100, 200)
    edge_pixels = np.count_nonzero(edges)
    required_bits = len(full_message)

    # ตรวจสอบว่าข้อความยาวเกินไปไหม
    if required_bits > edge_pixels:
        raise ValueError(f"⚠️ ข้อความยาวเกินไป! ต้องใช้ {required_bits} บิต แต่มีแค่ {edge_pixels} บิต")

    embedded_pixels = 0
    for i in range(edges.shape[0]):
        for j in range(edges.shape[1]):
            if edges[i, j] > 0 and bit_idx < required_bits:
                img[i, j, 0] = (img[i, j, 0] & 0b11111110) | int(full_message[bit_idx])  # ตั้งค่า LSB
                bit_idx += 1
                embedded_pixels += 1
            if bit_idx >= required_bits:
                break
        if bit_idx >= required_bits:
            break

    # บันทึกผลลัพธ์
    cv2.imwrite(output_path, img)




def retrieve_message_masking_filtering_from_steganography(image_path):
    """ดึงข้อความที่ซ่อนไว้ในขอบภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    edges = cv2.Canny(cv2.imread(image_path, cv2.IMREAD_GRAYSCALE), 100, 200)
    binary_message = ""
    length = None  # ป้องกัน UnboundLocalError

    for i in range(edges.shape[0]):
        for j in range(edges.shape[1]):
            if edges[i, j] > 0:
                binary_message += str(img[i, j, 0] & 1)
                # อ่านค่า length 32 บิตแรก
                if length is None and len(binary_message) == 32:
                    length = int(binary_message, 2)
                    binary_message = ""  # รีเซ็ตเพื่อเริ่มอ่านข้อความจริง
                # ถ้าอ่านครบ `length` บิตแล้ว ให้ถอดรหัส
                elif length is not None and len(binary_message) == length:
                    return binary_to_string(binary_message)
    return "ไม่มีข้อความ หรือข้อมูลผิดพลาด"










def hide_message_palette_based_from_steganography(image_path, message, output_path):
    # แปลงภาพต้นฉบับเป็น PNG
    img = Image.open(image_path).convert("RGB")
    temp_png_path = "temp_image.png"
    img.save(temp_png_path, format="PNG")
    print(f"Loaded image: {image_path}, temporary PNG created at {temp_png_path}")
    
    try:
        # เปิดภาพ PNG ที่แปลงแล้วและแปลงเป็น Palette-based
        img = Image.open(temp_png_path).convert("P")
        palette = img.getpalette()
        print(f"Palette size: {len(palette)}")  # Debug: แสดงขนาดพาเลต
        
        # แปลงข้อความเป็น binary พร้อมตัวคั่นและตัวจบข้อความ
        binary_message = '0' * 8 + string_to_binary(message) + '0' * 8
        print(f"Binary message length: {len(binary_message)}")  # Debug
        
        # ตรวจสอบขนาดข้อความ
        if len(binary_message) > len(palette):
            raise ValueError(f"ข้อความยาวเกินขีดจำกัดของพาเลต (ข้อความ={len(binary_message)} บิต, พาเลต={len(palette)} สี)")
        
        # ฝังข้อความลงในพาเลต
        for i in range(len(binary_message)):
            if i < len(palette):
                original_value = palette[i]
                palette[i] = (palette[i] & ~1) | int(binary_message[i])  # ฝังบิตลงใน palette
                print(f"Embedding bit {binary_message[i]} at palette index {i}: {original_value} -> {palette[i]}")  # Debug
        
        img.putpalette(palette)
        img.save(output_path, format="PNG")
        print(f"Message successfully embedded in {output_path}")

    finally:
        # ลบไฟล์ชั่วคราว
        if os.path.exists(temp_png_path):
            os.remove(temp_png_path)
            print(f"Temporary file {temp_png_path} removed")
    



def hide_message_spread_spectrum_from_steganography(image_path, message, output_path):
    # อ่านภาพ
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")
    
    # แปลงข้อความเป็น Binary พร้อมตัวจบข้อความ
    message_bits = string_to_binary(message) + '0' * 8  # ใช้ string_to_binary เพื่อแปลงข้อความ
    print(f"Message bits (first 64 bits): {message_bits[:64]}")  # พิมพ์บางส่วนของข้อความที่แปลงเป็น binary เพื่อดีบัก
    
    # สร้าง Noise Signal (Pseudo-Random Binary Sequence)
    np.random.seed(42)  # กำหนดเมล็ดสำหรับการสุ่ม
    noise = np.random.choice([0, 1], size=img.shape[:2], p=[0.5, 0.5]).astype(np.uint8)

    # ฝังข้อความโดยใช้ XOR กับ Noise Signal
    idx = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if idx < len(message_bits):
                bit = int(message_bits[idx])
                
                # ก่อนการอัปเดตพิกเซล ให้พิมพ์ค่าปัจจุบันของพิกเซล
                current_value = img[i, j, 0]
                new_value = (current_value & ~1) | (bit ^ noise[i, j])
                
                # ดีบัก: พิมพ์ค่าต่าง ๆ เพื่อดูว่าเกิดอะไรขึ้น
                print(f"Pixel ({i}, {j}): current_value={current_value}, bit={bit}, noise={noise[i, j]}, new_value={new_value}")

                # ตรวจสอบว่า new_value อยู่ในช่วงที่ถูกต้อง
                if new_value < 0 or new_value > 255:
                    print(f"Error: new_value {new_value} out of bounds at pixel ({i}, {j}), current_value: {current_value}, bit: {bit}, noise: {noise[i, j]}")

                # ใช้ np.clip เพื่อให้ new_value อยู่ในขอบเขตที่ถูกต้อง
                new_value = np.clip(new_value, 0, 255)
                img[i, j, 0] = new_value
                idx += 1
            else:
                break
        if idx >= len(message_bits):
            break

    # บันทึกภาพ
    cv2.imwrite(output_path, img)
    print(f"ข้อความถูกซ่อนสำเร็จและบันทึกใน '{output_path}'")

def retrieve_message_spread_spectrum_from_steganography(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")

    # สร้าง Noise Signal (Pseudo-Random Binary Sequence)
    np.random.seed(42)  # ใช้เมล็ดเดียวกับที่ใช้ในการซ่อน
    noise = np.random.choice([0, 1], size=img.shape[:2], p=[0.5, 0.5]).astype(np.uint8)

    # อ่านข้อความที่ซ่อนอยู่
    binary_message = ""
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            bit = (img[i, j, 0] & 1) ^ noise[i, j]  # ใช้ XOR กับ Noise Signal
            binary_message += str(bit)
            if len(binary_message) % 8 == 0 and binary_message[-8:] == '00000000':  # ตรวจสอบตัวจบ
                return binary_to_string(binary_message[:-8])  # ตัดตัวจบและแปลงข้อความ
    return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"


def hide_message_alpha_channel(image_path, message, output_path):
    """ซ่อนข้อความในช่อง Alpha ของภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # โหลดภาพพร้อมช่อง Alpha
    if img is None or img.shape[2] != 4:
        raise ValueError("ภาพต้องเป็น PNG ที่มี Alpha Channel")

    # คำนวณจำนวนบิตสูงสุดที่สามารถฝังได้
    max_bits = img.shape[0] * img.shape[1]
    print(f"🔢 จำนวนบิตสูงสุดที่สามารถฝังได้: {max_bits}")

    # แปลงข้อความเป็นไบนารี พร้อมตัวจบข้อความ
    binary_message = string_to_binary(message) + '00000000'
    print(f"📏 จำนวนบิตข้อความ: {len(binary_message)}")
    # print(f"🔍 ข้อความในรูปแบบไบนารี: {binary_message}")

    # ตรวจสอบว่าข้อความยาวเกินขอบเขตหรือไม่
    if len(binary_message) > max_bits:
        raise ValueError(f"⚠️ ข้อความยาวเกินกว่าที่จะฝังได้! จำนวนบิตสูงสุดที่สามารถฝังได้: {max_bits}")

    idx = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if idx < len(binary_message):
                # ตรวจสอบและแปลงค่า Alpha Channel ให้อยู่ในขอบเขตที่ถูกต้อง
                alpha = np.uint8(img[i, j, 3])
                
                # ฝังบิตลงใน Alpha Channel
                new_alpha = np.uint8((alpha & 0xFE) | int(binary_message[idx]))  # ใช้ 0xFE แทน ~1
                img[i, j, 3] = new_alpha
                
                idx += 1
            else:
                break
        if idx >= len(binary_message):
            break

    cv2.imwrite(output_path, img)
    print(f"ข้อความถูกซ่อนใน: {output_path}")


def hide_message_edge_detection(image_path, message, output_path):
    """ซ่อนข้อความในภาพโดยใช้การตรวจจับขอบด้วย PIL"""
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    gray_img = img.convert('L')
    gray_array = np.array(gray_img)
    
    def sobel_edges(gray):
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
        grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
        edges = np.sqrt(grad_x**2 + grad_y**2)
        threshold = 30
        return edges > threshold
    
    def prepare_message(message):
        # เข้ารหัสข้อความเป็น UTF-8
        message_bytes = message.encode('utf-8')
        # คำนวณ checksum
        checksum = zlib.crc32(message_bytes) & 0xFFFFFFFF
        # เตรียมส่วนหัว: ความยาว (4 bytes) + checksum (4 bytes)
        header = struct.pack('>II', len(message_bytes), checksum)
        # รวมส่วนหัวและข้อความ
        full_data = header + message_bytes
        # แปลงเป็น binary string
        return ''.join(format(b, '08b') for b in full_data)
    
    # ตรวจจับขอบ
    edges = sobel_edges(gray_array)
    edge_pixels = np.count_nonzero(edges)
    print(f"🔍 จำนวนพิกเซลขอบที่ใช้ได้: {edge_pixels}")
    
    # เตรียมข้อความ
    binary_message = prepare_message(message)
    total_bits = len(binary_message)
    print(f"📏 จำนวนบิตข้อความ (รวม header): {total_bits}")
    
    
    img2 = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img2 is None:
        raise ValueError("ไม่สามารถโหลดภาพได้")

    gray_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    edges2 = cv2.Canny(gray_img2, 100, 200)  # ตรวจจับขอบ

    # นับจำนวนพิกเซลขอบ
    edge_pixels2 = np.count_nonzero(edges2)
    
    
    if total_bits > edge_pixels2:
        raise ValueError(f"⚠️ ข้อความยาวเกินกว่าที่จะฝังในขอบของภาพได้! (ต้องการ {total_bits} bits, มี {edge_pixels2} bits)")
    
    # ฝังข้อมูล
    edge_positions = np.column_stack(np.where(edges))
    for bit_idx, (i, j) in enumerate(edge_positions[:total_bits]):
        if bit_idx < total_bits:
            pixel_value = img_array[i, j, 0]
            new_value = (pixel_value & 0xFE) | int(binary_message[bit_idx])
            img_array[i, j, 0] = new_value
    
    print(f"📊 จำนวนพิกเซลที่ใช้ในการฝังข้อมูล: {total_bits}")
    print(f"💾 ข้อมูลทั้งหมดที่ฝัง: {total_bits} บิต")
    
    result_img = Image.fromarray(img_array)
    result_img.save(output_path)
    print(f"✅ ข้อความถูกซ่อนใน: {output_path}")



















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

# def retrieve_message_transform_domain_from_steganography(image_path):
#     img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     if img is None:
#         raise ValueError("ไม่สามารถโหลดภาพได้")

#     # แปลงกลับเป็น DCT
#     dct_transformed = dct(dct(img.T, norm='ortho').T, norm='ortho')
    
#     print(f"Initial DCT (sample): {dct_transformed[0, 0]}")  # Debug: แสดงค่า DCT เริ่มต้น
    
#     # อ่านข้อความจากค่าสัมประสิทธิ์ DCT
#     binary_message = ""
#     for i in range(1, dct_transformed.shape[0]):
#         for j in range(1, dct_transformed.shape[1]):
#             if dct_transformed[i, j] != 0:
#                 bit = str(int(dct_transformed[i, j]) % 2)
#                 binary_message += bit
#                 print(f"Extracting bit at ({i}, {j}): {bit}")  # Debug: แสดงการดึงบิตจาก DCT
#                 if len(binary_message) % 8 == 0 and binary_message[-8:] == '00000000':  # ตรวจสอบตัวจบ
#                     print(f"End of message detected.")  # Debug: ตรวจพบจุดสิ้นสุดข้อความ
#                     return binary_to_string_T(binary_message[:-8])  # ตัดตัวจบและแปลงข้อความ
    
#     return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"




def retrieve_message_palette_based_from_steganography(image_path):
    img = Image.open(image_path).convert("P")
    palette = img.getpalette()
    print(f"Loaded image: {image_path}, Palette size: {len(palette)}")  # Debug: แสดงขนาดพาเลต

    # อ่านข้อมูลจาก palette
    binary_message = ''.join(str(color & 1) for color in palette[:len(palette)])
    print(f"Extracted binary message (length={len(binary_message)}): {binary_message[:64]}...")  # Debug: แสดง binary ส่วนแรก

    # ตรวจหาตัวคั่นด้านหน้าและด้านหลัง
    if binary_message.count('00000000') >= 2:
        # แยกข้อความที่อยู่ระหว่างตัวคั่น
        binary_parts = binary_message.split('00000000')
        print(f"Binary parts split by delimiter: {binary_parts}")  # Debug: แสดง binary ที่ถูกแยก

        if len(binary_parts) > 2:  # ต้องมีข้อความอย่างน้อย 1 ส่วนระหว่างตัวคั่น
            binary_message = binary_parts[1]  # ข้อความที่อยู่ระหว่างตัวคั่น
            print(f"Binary message extracted: {binary_message}")  # Debug: แสดงข้อความหลังตัดตัวคั่น
            return binary_to_string_P(binary_message)  # แปลงกลับเป็นข้อความ
    else:
        print("Delimiter not found in binary message")  # Debug
    
    return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"




# def retrieve_message_spread_spectrum_from_steganography(image_path):
#     img = cv2.imread(image_path, cv2.IMREAD_COLOR)
#     if img is None:
#         raise ValueError("ไม่สามารถโหลดภาพได้")

#     # สร้าง Noise Signal (Pseudo-Random Binary Sequence)
#     np.random.seed(42)  # ใช้เมล็ดเดียวกับที่ใช้ในการซ่อน
#     noise = np.random.choice([0, 1], size=img.shape[:2], p=[0.5, 0.5]).astype(np.uint8)

#     # อ่านข้อความที่ซ่อนอยู่
#     binary_message = ""
#     for i in range(img.shape[0]):
#         for j in range(img.shape[1]):
#             bit = (img[i, j, 0] & 1) ^ noise[i, j]  # ใช้ XOR กับ Noise Signal
#             binary_message += str(bit)
#             if len(binary_message) % 8 == 0 and binary_message[-8:] == '00000000':  # ตรวจสอบตัวจบ
#                 return binary_to_string(binary_message[:-8])  # ตัดตัวจบและแปลงข้อความ
#     return "ไม่มีข้อความ หรือข้อความไม่ถูกต้อง"

def retrieve_message_alpha_channel(image_path):
    """ดึงข้อความที่ซ่อนไว้ในช่อง Alpha ของภาพ"""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[2] != 4:
        raise ValueError("ภาพต้องเป็น PNG ที่มี Alpha Channel")

    binary_message = ''
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            # ดึงบิตที่ต่ำสุดของ Alpha Channel
            alpha = np.uint8(img[i, j, 3])
            binary_message += str(alpha & 1)
            
            # หยุดเมื่อพบตัวจบข้อความ (8 บิต 0)
            if len(binary_message) % 8 == 0 and binary_message[-8:] == '00000000':
                return binary_to_string(binary_message[:-8])
    return binary_to_string(binary_message)

def retrieve_message_edge_detection(image_path):
    """ดึงข้อความที่ซ่อนอยู่ในภาพ"""
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    gray_img = img.convert('L')
    gray_array = np.array(gray_img)
    
    def sobel_edges(gray):
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
        grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
        edges = np.sqrt(grad_x**2 + grad_y**2)
        threshold = 30
        return edges > threshold
    
    try:
        edges = sobel_edges(gray_array)
        edge_positions = np.column_stack(np.where(edges))
        
        # อ่าน header ก่อน (8 bytes = 64 bits)
        header_bits = ""
        for i, j in edge_positions[:64]:
            header_bits += str(img_array[i, j, 0] & 1)
        
        # แปลง header bits เป็น bytes
        header_bytes = bytes(int(header_bits[i:i+8], 2) for i in range(0, 64, 8))
        message_length, expected_checksum = struct.unpack('>II', header_bytes)
        
        # อ่านข้อความตามความยาวที่ระบุ
        total_bits_needed = 64 + (message_length * 8)  # header + message
        binary_message = header_bits
        
        for i, j in edge_positions[64:total_bits_needed]:
            binary_message += str(img_array[i, j, 0] & 1)
        
        # แยกส่วน message
        message_binary = binary_message[64:]
        message_bytes = bytes(int(message_binary[i:i+8], 2) 
                            for i in range(0, len(message_binary), 8))
        
        # ตรวจสอบ checksum
        actual_checksum = zlib.crc32(message_bytes) & 0xFFFFFFFF
        if actual_checksum != expected_checksum:
            return "<font color='red'>⚠️ ข้อมูลเสียหาย: Checksum ไม่ตรงกัน</font>"
        
        return message_bytes.decode('utf-8')
        
    except (struct.error, ValueError, UnicodeDecodeError) as e:
        return f"<font color='red'>⚠️ เกิดข้อผิดพลาด: {str(e)}</font>"
    except Exception as e:
        return f"<font color='red'>⚠️ ข้อผิดพลาดที่ไม่คาดคิด: {str(e)}</font>"























