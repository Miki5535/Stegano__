import os
import shutil
import re

def append_files_to_image(image_path, files_to_append):
    """
    ฟังก์ชันสำหรับต่อท้ายไฟล์ต่างๆ ไปยังไฟล์ภาพ
    
    :param image_path: พาธของไฟล์ภาพหลัก
    :param files_to_append: รายการไฟล์ที่ต้องการต่อท้าย
    :return: พาธของไฟล์ภาพที่ถูกแก้ไข
    """
    # ตรวจสอบว่าไฟล์ภาพมีอยู่จริง
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"ไม่พบไฟล์ภาพ: {image_path}")
    
    # สร้างไฟล์สำเนาเพื่อป้องกันการแก้ไขไฟล์ต้นฉบับ
    modified_image_path = os.path.splitext(image_path)
    modified_image_path = f"{modified_image_path[0]}_modified{modified_image_path[1]}"
    shutil.copy2(image_path, modified_image_path)
    
    # เปิดไฟล์ภาพในโหมดเขียนแบบต่อท้าย
    with open(modified_image_path, 'ab') as image_file:
        for file_path in files_to_append:
            # ตรวจสอบว่าไฟล์ที่ต้องการต่อท้ายมีอยู่จริง
            if not os.path.exists(file_path):
                print(f"คำเตือน: ไม่พบไฟล์ {file_path}")
                continue
            
            # อ่านและต่อท้ายข้อมูลไฟล์
            with open(file_path, 'rb') as append_file:
                image_file.write(append_file.read())
    
    return modified_image_path

def verify_appended_files(image_path):
    """
    ฟังก์ชันตรวจสอบไฟล์ที่ถูกต่อท้าย
    
    :param image_path: พาธของไฟล์ภาพที่ถูกแก้ไข
    :return: รายการไฟล์ที่ถูกต่อท้าย
    """
    # ลายเซ็นต์ของไฟล์ประเภทต่างๆ 
    file_signatures = {
        'png': b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',
        'jpg': b'\xFF\xD8\xFF',
        'pdf': b'\x25\x50\x44\x46',
        'zip': b'\x50\x4B\x03\x04',
        'txt': b'\x54\x65\x78\x74'
    }
    
    appended_files = []
    
    try:
        with open(image_path, 'rb') as f:
            # อ่านข้อมูลทั้งหมดของไฟล์
            file_data = f.read()
            
            # ค้นหาลายเซ็นต์ไฟล์
            for file_type, signature in file_signatures.items():
                # ค้นหาลายเซ็นต์ที่อยู่ต่อจากข้อมูลภาพเดิม
                original_image_size = os.path.getsize(image_path.replace('_modified', ''))
                matches = [m.start() for m in re.finditer(re.escape(signature), file_data)]
                
                # กรองเฉพาะลายเซ็นต์ที่อยู่หลังขนาดภาพเดิม
                valid_matches = [match for match in matches if match > original_image_size]
                
                if valid_matches:
                    appended_files.append({
                        'type': file_type, 
                        'positions': valid_matches
                    })
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
    
    return appended_files



def extract_appended_files(image_path, output_folder):
    """
    ฟังก์ชันสำหรับถอดไฟล์ที่ถูกต่อท้ายจากไฟล์ภาพ
    
    :param image_path: พาธของไฟล์ภาพที่ถูกแก้ไข
    :param output_folder: โฟลเดอร์สำหรับบันทึกไฟล์ที่ถูกถอด
    :return: รายการไฟล์ที่ถูกถอด
    """
    file_signatures = {
        'png': b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',
        'jpg': b'\xFF\xD8\xFF',
        'pdf': b'\x25\x50\x44\x46',
        'zip': b'\x50\x4B\x03\x04',
    }

    extracted_files = []

    try:
        with open(image_path, 'rb') as f:
            file_data = f.read()
        
        # ค้นหาขนาดไฟล์ภาพต้นฉบับ
        original_image_size = os.path.getsize(image_path.replace('_modified', ''))
        current_position = original_image_size
        
        # ค้นหาไฟล์ที่ถูกต่อท้าย
        while current_position < len(file_data):
            for file_type, signature in file_signatures.items():
                if file_data[current_position:current_position+len(signature)] == signature:
                    # หาตำแหน่งสิ้นสุดของไฟล์
                    next_position = file_data.find(signature, current_position + len(signature))
                    if next_position == -1:
                        next_position = len(file_data)
                    
                    # แยกข้อมูลไฟล์
                    extracted_file_data = file_data[current_position:next_position]
                    extracted_file_path = os.path.join(output_folder, f"extracted_file_{len(extracted_files) + 1}.{file_type}")
                    
                    # บันทึกไฟล์
                    with open(extracted_file_path, 'wb') as output_file:
                        output_file.write(extracted_file_data)
                    
                    extracted_files.append(extracted_file_path)
                    current_position = next_position
                    break
            else:
                # กรณีที่ไม่มีลายเซ็นต์ตรงกัน
                current_position += 1

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการถอดไฟล์: {e}")

    return extracted_files

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    try:
        # ต่อท้ายไฟล์ไปยังภาพ
        image_path = r'C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfs.png'
        files_to_append = [
            r'C:\Users\65011\Desktop\Segano\work00002\photoexample\output\20241201161719_5dc8e875.png', 
            r'C:\Users\65011\Desktop\Segano\work00002\photoexample\output\20241201161751_8e6256d5.png', 
            r'C:\Users\65011\Desktop\Segano\work00002\photoexample\output\20241201161900_2c09759e.png', 
        ]
        
        modified_image = append_files_to_image(image_path, files_to_append)
        print(f"ภาพที่แก้ไขถูกบันทึกที่: {modified_image}")
        
        # ตรวจสอบไฟล์ที่ต่อท้าย
        appended_files = verify_appended_files(modified_image)
        
        # พิมพ์รายละเอียดไฟล์ที่ถูกต่อท้าย
        if appended_files:
            print("ไฟล์ที่ถูกต่อท้าย:")
            for file_info in appended_files:
                print(f"- ประเภท: {file_info['type']}")
                print(f"  ตำแหน่ง: {file_info['positions']}")
        else:
            print("ไม่พบไฟล์ที่ต่อท้าย")
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        
    try:
        # ถอดไฟล์ที่ถูกต่อท้ายจากภาพ
        image_path = r'C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfs_modified.png'
        output_folder = r'C:\Users\65011\Desktop\Segano\work00002\photoexample\extracted_files'
        os.makedirs(output_folder, exist_ok=True)
        
        extracted_files = extract_appended_files(image_path, output_folder)
        
        # พิมพ์รายการไฟล์ที่ถูกถอด
        if extracted_files:
            print("ไฟล์ที่ถูกถอด:")
            for extracted_file in extracted_files:
                print(f"- {extracted_file}")
        else:
            print("ไม่พบไฟล์ที่ถูกถอด")
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")