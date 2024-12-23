from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QFileDialog, QTextEdit
import os
import shutil
import struct

class FileAndFileTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.files_to_append = []  
    
    def initUI(self):
        layout = QVBoxLayout()

        # ส่วนแสดงข้อมูลไฟล์
        group_box_info = QGroupBox("การจัดการไฟล์และข้อมูลไฟล์")
        group_layout_info = QVBoxLayout()
        
        self.info_label = QLabel("ไม่มีไฟล์ที่เลือก")
        self.file_content_display = QTextEdit()
        self.file_content_display.setReadOnly(True)
        
        self.button_select_files = QPushButton("เลือกไฟล์หลายไฟล์")
        self.button_select_files.clicked.connect(self.select_files)

        self.button_append_files = QPushButton("ต่อท้ายไฟล์ไปยังภาพ")
        self.button_append_files.clicked.connect(self.file_to)

        self.button_extract_files = QPushButton("ถอดไฟล์ที่ถูกต่อท้าย")
        self.button_extract_files.clicked.connect(self.ex_file)

        group_layout_info.addWidget(self.info_label)
        group_layout_info.addWidget(self.file_content_display)
        group_layout_info.addWidget(self.button_select_files)
        group_layout_info.addWidget(self.button_append_files)
        group_layout_info.addWidget(self.button_extract_files)
        group_box_info.setLayout(group_layout_info)

        layout.addWidget(group_box_info)
        self.setLayout(layout)

    def file_to(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        try:
            files_to_append = self.files_to_append
            
            modified_image = self.append_files_to_image(image_path, files_to_append)
            self.file_content_display.setPlainText(f"ภาพที่แก้ไขถูกบันทึกที่: {modified_image}")
            
            # ตรวจสอบไฟล์ที่ต่อท้าย
            appended_files = self.verify_appended_files(modified_image)
            
            # พิมพ์รายละเอียดไฟล์ที่ถูกต่อท้าย
            if appended_files:
                details = "ไฟล์ที่ถูกต่อท้าย:\n"
                for file_info in appended_files:
                    details += f"- ประเภท: {file_info['type']}\n"
                    details += f"  ตำแหน่ง: {file_info['positions']}\n"
                self.file_content_display.setPlainText(details)
            else:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ต่อท้าย")
        
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")

    def ex_file(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพที่ถูกแก้ไข", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return

        output_folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์สำหรับบันทึกไฟล์ที่ถูกถอด")
        if not output_folder:
            self.file_content_display.setPlainText("กรุณาเลือกโฟลเดอร์สำหรับบันทึกไฟล์")
            return
        try:
            os.makedirs(output_folder, exist_ok=True)
            
            extracted_files = self.extract_appended_files(image_path, output_folder)
            
            # พิมพ์รายการไฟล์ที่ถูกถอด
            if extracted_files:
                details = "ไฟล์ที่ถูกถอด:\n"
                for extracted_file in extracted_files:
                    details += f"- {extracted_file}\n"
                self.file_content_display.setPlainText(details)
            else:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ถูกถอด")
        
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")

    def select_files(self):
        # เปิดไฟล์ไดอะล็อกเพื่อเลือกไฟล์หลายไฟล์
        file_paths, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์", "", "All Files (*.*)")
        if file_paths:
            self.files_to_append = file_paths
            self.info_label.setText(f"เลือกไฟล์ {len(file_paths)} ไฟล์")
            self.file_content_display.setPlainText("\n".join(self.files_to_append))

    def append_files_to_image(self, image_path, files_to_append):
        """
        ฟังก์ชันสำหรับต่อท้ายไฟล์ต่างๆ ไปยังไฟล์ภาพ
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ภาพ: {image_path}")
        
        modified_image_path = os.path.splitext(image_path)
        modified_image_path = f"{modified_image_path[0]}_modified{modified_image_path[1]}"
        shutil.copy2(image_path, modified_image_path)
        
        with open(modified_image_path, 'ab') as image_file:
            # เขียนหมายเลขของไฟล์ที่ต่อท้าย
            image_file.write(struct.pack('<I', len(files_to_append)))
            
            for file_path in files_to_append:
                if not os.path.exists(file_path):
                    self.file_content_display.setPlainText(f"คำเตือน: ไม่พบไฟล์ {file_path}")
                    continue
                
                # ตรวจสอบนามสกุลไฟล์
                file_ext = os.path.splitext(file_path)[1][1:].encode('ascii', errors='ignore').decode('ascii')
                
                # อ่านข้อมูลไฟล์
                with open(file_path, 'rb') as append_file:
                    file_data = append_file.read()
                
                # เขียนนามสกุลไฟล์และขนาดไฟล์
                image_file.write(struct.pack('<I', len(file_ext)))
                image_file.write(file_ext.encode('ascii'))
                image_file.write(struct.pack('<Q', len(file_data)))
                
                # เขียนข้อมูลไฟล์
                image_file.write(file_data)
        
        return modified_image_path

    def verify_appended_files(self, image_path):
        """
        ฟังก์ชันตรวจสอบไฟล์ที่ถูกต่อท้าย
        """
        appended_files = []
        
        try:
            with open(image_path, 'rb') as f:
                # อ่านข้อมูลทั้งหมดของไฟล์
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                f.seek(0)
                file_data = f.read()
                
                # อ่านจำนวนไฟล์ที่ต่อท้าย
                original_image_size = os.path.getsize(image_path.replace('_modified', ''))
                f.seek(original_image_size)
                
                num_files = struct.unpack('<I', f.read(4))[0]
                current_position = original_image_size + 4
                
                for _ in range(num_files):
                    # อ่านนามสกุลไฟล์
                    ext_len = struct.unpack('<I', f.read(4))[0]
                    file_ext = f.read(ext_len).decode('ascii', errors='ignore')
                    
                    # อ่านขนาดไฟล์
                    file_size = struct.unpack('<Q', f.read(8))[0]
                    
                    # บันทึกข้อมูลไฟล์ที่ต่อท้าย
                    appended_files.append({
                        'type': file_ext, 
                        'positions': [current_position]
                    })
                    
                    # ข้ามไปยังไฟล์ถัดไป
                    current_position += 4 + ext_len + 8 + file_size
        
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
        
        return appended_files

    def extract_appended_files(self, image_path, output_folder):
        """
        ฟังก์ชันสำหรับถอดไฟล์ที่ถูกต่อท้ายจากไฟล์ภาพ
        """
        extracted_files = []

        try:
            with open(image_path, 'rb') as f:
                # หาขนาดภาพต้นฉบับ
                original_image_size = os.path.getsize(image_path.replace('_modified', ''))
                f.seek(original_image_size)
                
                # อ่านจำนวนไฟล์
                num_files = struct.unpack('<I', f.read(4))[0]
                
                for _ in range(num_files):
                    # อ่านนามสกุลไฟล์
                    ext_len = struct.unpack('<I', f.read(4))[0]
                    file_ext = f.read(ext_len).decode('ascii', errors='ignore')
                    
                    # อ่านขนาดไฟล์
                    file_size = struct.unpack('<Q', f.read(8))[0]
                    
                    # อ่านข้อมูลไฟล์
                    file_data = f.read(file_size)
                    
                    # บันทึกไฟล์
                    extracted_file_path = os.path.join(output_folder, f"extracted_file_{len(extracted_files) + 1}.{file_ext}")
                    
                    with open(extracted_file_path, 'wb') as output_file:
                        output_file.write(file_data)
                    
                    extracted_files.append(extracted_file_path)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการถอดไฟล์: {e}")

        return extracted_files