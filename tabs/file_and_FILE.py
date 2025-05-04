import logging
import shutil
import struct
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QFileDialog, QTextEdit, QScrollArea, QGridLayout,QMessageBox,QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QUrl
import os

class FileAndFileTab(QWidget):
    def __init__(self):
        super().__init__()
        self.files_to_append = []
        self.initUI()
        
        # เปิดใช้งานการลากและวาง
        self.setAcceptDrops(True)

    def initUI(self):
        layout = QVBoxLayout()

        # ส่วนแสดงข้อมูลไฟล์
        group_box_info = QGroupBox("การจัดการไฟล์และข้อมูลไฟล์")
        group_layout_info = QVBoxLayout()

        self.info_label = QLabel("ไม่มีไฟล์ที่เลือก")
        self.file_content_display = QTextEdit()
        self.file_content_display.setReadOnly(True)

        # Scroll area for file preview
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.preview_container = QWidget()
        self.preview_layout = QGridLayout()
        self.preview_container.setLayout(self.preview_layout)
        self.scroll_area.setWidget(self.preview_container)

        # ปุ่มต่างๆ
        self.button_select_files = QPushButton("เลือกไฟล์หลายไฟล์")
        
        self.button_append_files = QPushButton("ต่อท้ายไฟล์ไปยังภาพ")
        self.button_append_files.setStyleSheet("background-color: purple; color: white;")

        self.button_extract_files = QPushButton("ถอดไฟล์ที่ถูกต่อท้าย")
        self.button_extract_files.setStyleSheet("background-color: orange; color: white;")

        # เพิ่มปุ่มลบทั้งหมด
        self.button_clear_all = QPushButton("ลบทั้งหมด")
        self.button_clear_all.setStyleSheet("""
            background-color: #dc3545;
            color: white;
            border-radius: 5px;
            padding: 5px;
        """)
        self.button_clear_all.clicked.connect(self.clear_all_files)

        # Layout สำหรับจัดปุ่มในบรรทัดเดียวกัน
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_select_files)
        button_layout.addWidget(self.button_clear_all)
        button_layout.addWidget(self.button_append_files)
        button_layout.addWidget(self.button_extract_files)
        

        # เชื่อมต่อสัญญาณปุ่มกับฟังก์ชัน
        self.button_select_files.clicked.connect(self.select_files)
        self.button_append_files.clicked.connect(self.file_to)
        self.button_extract_files.clicked.connect(self.ex_file)

        # จัดวางปุ่มและ scroll area
        group_layout_info.addWidget(self.scroll_area)
        group_layout_info.addWidget(self.info_label)
        group_layout_info.addWidget(self.file_content_display)
        group_layout_info.addLayout(button_layout)
        group_box_info.setLayout(group_layout_info)

        layout.addWidget(group_box_info)
        self.setLayout(layout)
        
        
        
    def clear_all_files(self):
        """ฟังก์ชันสำหรับลบไฟล์ทั้งหมด"""
        if not self.files_to_append:
            return
            
        reply = QMessageBox.question(
            self,
            "ยืนยันการลบ",
            "คุณต้องการลบไฟล์ทั้งหมดใช่หรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # ล้างรายการไฟล์
            self.files_to_append.clear()
            
            # ล้าง preview
            for i in reversed(range(self.preview_layout.count())):
                widget = self.preview_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # อัปเดต UI
            self.info_label.setText("ไม่มีไฟล์ที่เลือก")
            self.file_content_display.clear()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if file_paths:
            self.files_to_append.extend(file_paths)
            self.info_label.setText(f"เลือกไฟล์ {len(self.files_to_append)} ไฟล์")
            self.file_content_display.setPlainText("\n".join(self.files_to_append))
            self.update_preview(self.files_to_append)

    def select_files(self):
        # เปิดไฟล์ไดอะล็อกเพื่อเลือกไฟล์หลายไฟล์
        file_paths, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์", "", "All Files (*.*)")
        if file_paths:
            self.files_to_append.extend(file_paths)
            self.info_label.setText(f"เลือกไฟล์ {len(self.files_to_append)} ไฟล์")
            self.file_content_display.setPlainText("\n".join(self.files_to_append))
            self.update_preview(self.files_to_append)

    def update_preview(self, file_paths):
        # อัปเดตตัวอย่างของไฟล์ใน Layout
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        output_path = os.path.join(parent_directory, "photoexample", "potofle")

        icon_mapping = {
            '.zip': f'{output_path}/zip.png',
            '.docx': f'{output_path}/word.png',
            '.xlsx': f'{output_path}/excel.png',
            '.pptx': f'{output_path}/pp.png',
            '.txt': f'{output_path}/txt.png',
            '.exe': f'{output_path}/exe.png',
            '.pdf': f'{output_path}/pdf.png',
            '.xml': f'{output_path}/xml.png',
            '.bat': f'{output_path}/bat.png',
            '.gradle': f'{output_path}/gradle.png',
            '.yaml': f'{output_path}/yaml.png',
            '.iml': f'{output_path}/iml.png',
            '.html': f'{output_path}/html.png',
            '.md': f'{output_path}/md.png',
            '.msi': f'{output_path}/msi.png',
            '.js': f'{output_path}/js.png',
            '.json': f'{output_path}/json.png',
            '.pkg': f'{output_path}/pkg.png',
            '.py': f'{output_path}/py.png',
            '.vbs': f'{output_path}/vbs.png',
            '.dat': f'{output_path}/dat.png',
            '.asc': f'{output_path}/asc.png',
            '.css': f'{output_path}/css.png'
        }


        row, col = 0, 0
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            ext = os.path.splitext(file_path)[1].lower()
            icon_path = icon_mapping.get(ext, f"{output_path}/default.png")
            file_widget = self.create_file_widget(file_path, icon_path)
            self.preview_layout.addWidget(file_widget, row, col)

            col += 1
            if col > 3:
                col = 0
                row += 1

    def create_file_widget(self, file_path, icon_path):
        # สร้าง layout สำหรับไฟล์
        file_layout = QVBoxLayout()
        file_layout.setAlignment(Qt.AlignCenter)

        # สร้าง icon_label
        icon_label = QLabel()
        
        # ถ้าไฟล์เป็นภาพ, ใช้ QPixmap แสดงภาพ
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            pixmap = QPixmap(file_path).scaled(100, 100, Qt.KeepAspectRatio)
            if pixmap.isNull():
                icon_label.setText("ไม่รองรับ")  # ถ้าภาพไม่สามารถโหลดได้
            else:
                icon_label.setPixmap(pixmap)
        else:
            # ถ้าไม่ใช่ไฟล์ภาพ, ใช้ไอคอนจาก icon_path
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio)
            icon_label.setPixmap(pixmap if not pixmap.isNull() else QPixmap("not_supported.png"))

        # สร้าง label แสดงชื่อไฟล์
        name_label = QLabel(os.path.basename(file_path))
        name_label.setAlignment(Qt.AlignCenter)

        # สร้างปุ่มลบ
        delete_button = QPushButton("ลบ")
        delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px; font-size: 12px;")
        delete_button.setFixedSize(40, 40)
        delete_button.clicked.connect(lambda _, fp=file_path, fl=file_layout: self.remove_preview(fp, fl))


        # เพิ่ม widgets ลงใน layout
        file_layout.addWidget(icon_label)
        file_layout.addWidget(name_label)
        file_layout.addWidget(delete_button)

        # สร้าง container_widget และกำหนด layout
        container_widget = QWidget()
        container_widget.setLayout(file_layout)
        
        return container_widget


    def remove_preview(self, file_path, file_layout):
        reply = QMessageBox.question(
            self,
            "ยืนยันการลบ",
            "คุณต้องการลบรายการนี้ออกจากการแสดงผลหรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if file_path in self.files_to_append:
                self.files_to_append.remove(file_path)
            for i in reversed(range(file_layout.count())):
                widget = file_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)
            parent_widget = file_layout.parentWidget()
            if parent_widget is not None:
                self.preview_layout.removeWidget(parent_widget)
                parent_widget.setParent(None)
            if hasattr(self, 'file_content_display'):
                self.file_content_display.setPlainText("\n".join(self.files_to_append))









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





