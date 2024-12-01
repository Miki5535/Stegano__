from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QFileDialog, QTextEdit
import os
import shutil
import re


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

    def file_to (self):
        image_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        try:
        # ต่อท้ายไฟล์ไปยังภาพ
            # image_path = r'C:\Users\65011\Desktop\Segano\work00002\photoexample\output\sfs.png'
            files_to_append = self.files_to_append
            
            modified_image = self.append_files_to_image(image_path, files_to_append)
            self.file_content_display.setPlainText(f"ภาพที่แก้ไขถูกบันทึกที่: {modified_image}")
            
            # ตรวจสอบไฟล์ที่ต่อท้าย
            appended_files = self.verify_appended_files(modified_image)
            
            # พิมพ์รายละเอียดไฟล์ที่ถูกต่อท้าย
            if appended_files:
                print("ไฟล์ที่ถูกต่อท้าย:")
                for file_info in appended_files:
                    self.file_content_display.setPlainText(f"- ประเภท: {file_info['type']}")
                    self.file_content_display.setPlainText(f"  ตำแหน่ง: {file_info['positions']}")
            else:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ต่อท้าย")
        
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")

    def ex_file (self):
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
                self.file_content_display.setPlainText("ไฟล์ที่ถูกถอด:")
                for extracted_file in extracted_files:
                    self.file_content_display.setPlainText(f"- {extracted_file}")
            else:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ถูกถอด")
        
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")

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
                    self.file_content_display.setPlainText(f"คำเตือน: ไม่พบไฟล์ {file_path}")
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

    def extract_appended_files(self,image_path, output_folder):
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
