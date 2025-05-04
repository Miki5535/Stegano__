def hide_text_in_png(png_path, output_path, secret_text):
    """
    ซ่อนข้อความหลังไฟล์ PNG
    
    Args:
        png_path (str): พาธของไฟล์ PNG ต้นฉบับ
        output_path (str): พาธของไฟล์ PNG ที่จะบันทึกผลลัพธ์
        secret_text (str): ข้อความที่ต้องการซ่อน
    """
    try:
        # อ่านไฟล์ PNG ต้นฉบับ
        with open(png_path, 'rb') as f:
            png_data = f.read()
            
        # แปลงข้อความเป็น bytes
        secret_bytes = secret_text.encode('utf-8')
        
        # สร้างไฟล์ใหม่ที่มีข้อความซ่อนอยู่
        with open(output_path, 'wb') as f:
            # เขียนข้อมูล PNG
            f.write(png_data)
            # เขียนข้อความที่ต้องการซ่อน
            f.write(secret_bytes)
            
        print(f"ซ่อนข้อความสำเร็จ! บันทึกไว้ที่: {output_path}")
        return True
        
    except FileNotFoundError:
        print(f"ไม่พบไฟล์: {png_path}")
        return False
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return False

def read_hidden_text(png_path):
    """
    อ่านข้อความที่ซ่อนอยู่หลังไฟล์ PNG
    
    Args:
        png_path (str): พาธของไฟล์ PNG ที่มีข้อความซ่อนอยู่
        
    Returns:
        str: ข้อความที่ซ่อนอยู่
    """
    try:
        with open(png_path, 'rb') as f:
            data = f.read()
        
        # หาตำแหน่งของ IEND chunk
        iend_pos = data.find(b'IEND')
        if iend_pos == -1:
            print("ไม่พบ IEND chunk ไฟล์อาจไม่ใช่ PNG ที่ถูกต้อง")
            return None
            
        # ข้ามส่วน IEND chunk และ CRC
        end_of_png = iend_pos + 8
        
        # อ่านข้อมูลที่ซ่อนอยู่
        hidden_data = data[end_of_png:]
        
        if hidden_data:
            # แปลงกลับเป็นข้อความ
            return hidden_data.decode('utf-8')
        else:
            print("ไม่พบข้อความที่ซ่อนอยู่")
            return None
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # ซ่อนข้อความ
    
    # hide_text_in_png(
    #     r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfds.png",
    #     r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfds_out.png",
    #     "นี่คือข้อความลับ!"
    # )
    
    
    out=r"C:\Users\65011\Desktop\Segano\work00002\photoexample\output\dsfds_modified.png"
    # อ่านข้อความที่ซ่อนอยู่
    secret = read_hidden_text(out)
    if secret:
        print("ข้อความที่ซ่อนอยู่:", secret)












