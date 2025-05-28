import logging
import shutil
import struct
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QFileDialog, QTextEdit, QScrollArea, QGridLayout, QMessageBox, QHBoxLayout, QTabWidget
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
        main_layout = QVBoxLayout()  # layout หลัก
        horizontal_group_layout = QHBoxLayout()  # layout สำหรับกล่องสองกล่องแนวนอน

        # ============ กล่องกลางสำหรับแสดง Log ============
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("ผลลัพธ์ / Log ต่างๆ จะปรากฏที่นี่...")

        # ============ ส่วนที่ 1: ข้อความต่อท้าย ============
        group_text = QGroupBox("ต่อท้ายข้อความและถอดข้อความ")
        layout_text = QVBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("ป้อนข้อความที่ต้องการต่อท้าย...")
        self.button_append_text = QPushButton("ต่อท้ายข้อความ")
        self.button_append_text.setStyleSheet("background-color: green; color: white;")
        self.button_append_text.clicked.connect(self.append_text_to_image)
        self.button_extract_text = QPushButton("ถอดข้อความที่ต่อท้าย")
        self.button_extract_text.setStyleSheet("background-color: #007bff; color: white;")
        self.button_extract_text.clicked.connect(self.extract_text_content)
        layout_text.addWidget(self.text_input)
        layout_text.addWidget(self.button_append_text)
        layout_text.addWidget(self.button_extract_text)
        group_text.setLayout(layout_text)

        # ============ ส่วนที่ 2: ไฟล์ต่อท้าย ============
        group_file = QGroupBox("ต่อท้ายไฟล์และถอดไฟล์")
        layout_file = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.preview_container = QWidget()
        self.preview_layout = QGridLayout()
        self.preview_container.setLayout(self.preview_layout)
        self.scroll_area.setWidget(self.preview_container)
        self.info_label = QLabel("ไม่มีไฟล์ที่เลือก")
        self.button_select_files = QPushButton("เลือกไฟล์หลายไฟล์")
        self.button_clear_all = QPushButton("ลบทั้งหมด")
        self.button_clear_all.setStyleSheet("""
            background-color: #dc3545;
            color: white;
            border-radius: 5px;
            padding: 5px;
        """)
        self.button_clear_all.clicked.connect(self.clear_all_files)
        self.button_append_files = QPushButton("ต่อท้ายไฟล์ไปยังภาพ")
        self.button_append_files.setStyleSheet("background-color: purple; color: white;")
        self.button_append_files.clicked.connect(self.file_to)
        self.button_extract_files = QPushButton("ถอดไฟล์ที่ถูกต่อท้าย")
        self.button_extract_files.setStyleSheet("background-color: orange; color: white;")
        self.button_extract_files.clicked.connect(self.ex_file)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_select_files)
        button_layout.addWidget(self.button_clear_all)
        button_layout.addWidget(self.button_append_files)
        button_layout.addWidget(self.button_extract_files)
        self.button_select_files.clicked.connect(self.select_files)

        # ============ เพิ่มส่วนนี้เข้ามา ============
        self.file_content_display = QTextEdit()
        self.file_content_display.setReadOnly(True)
        self.file_content_display.setPlaceholderText("ผลลัพธ์ / Log จะแสดงที่นี่...")

        # ============ เพิ่ม widget เข้า layout ============
        layout_file.addWidget(self.scroll_area)
        layout_file.addWidget(self.info_label)
        layout_file.addLayout(button_layout)
        layout_file.addWidget(self.file_content_display)  # เพิ่มตรงนี้เข้าไป
        group_file.setLayout(layout_file)

        # วางกล่องสองกล่องในแนวนอน
        horizontal_group_layout = QHBoxLayout()
        horizontal_group_layout.addWidget(group_text)
        horizontal_group_layout.addWidget(group_file)

        # ตั้งความสูงขั้นต่ำ
        group_text.setMinimumHeight(400)
        group_file.setMinimumHeight(400)

        # ใส่เข้า Layout หลัก
        main_layout = QVBoxLayout()
        main_layout.addLayout(horizontal_group_layout, stretch=3)
        main_layout.addWidget(self.log_output, stretch=1)
        self.setLayout(main_layout)

    def append_files_to_image(self, image_path, file_paths):
        """
        เมธอดสำหรับต่อท้ายไฟล์หลายไฟล์ลงท้ายไฟล์ภาพ
        """
        if not file_paths:
            raise ValueError("ไม่มีไฟล์ที่เลือก")

        modified_image_path = os.path.splitext(image_path)[0] + "_modified" + os.path.splitext(image_path)[1]
        
        # คัดลอกไฟล์ภาพเดิม
        shutil.copy2(image_path, modified_image_path)

        with open(modified_image_path, 'ab') as image_file:
            original_size = os.path.getsize(image_path)
            image_file.write(struct.pack('<I', len(file_paths)))  # เขียนจำนวนไฟล์ที่ต่อท้าย

            for file_path in file_paths:
                _, ext = os.path.splitext(file_path)
                ext = ext[1:]  # ลบจุดออก เช่น .txt -> txt

                with open(file_path, 'rb') as f:
                    file_data = f.read()

                # เขียนนามสกุลไฟล์
                image_file.write(struct.pack('<I', len(ext)))
                image_file.write(ext.encode('ascii'))

                # เขียนขนาดไฟล์
                image_file.write(struct.pack('<Q', len(file_data)))

                # เขียนข้อมูลไฟล์
                image_file.write(file_data)

            # เขียนขนาดไฟล์ภาพต้นฉบับท้ายสุด
            image_file.write(struct.pack('<Q', original_size))

        return modified_image_path

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
        image_path, _ = QFileDialog.getOpenFileName(
            self, "เลือกไฟล์ภาพ", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        try:
            files_to_append = self.files_to_append
            modified_image = self.append_files_to_image(image_path, files_to_append)
            self.file_content_display.setPlainText(f"ภาพที่แก้ไขถูกบันทึกที่: {modified_image}")
            # Verify appended files
            appended_files = self.verify_appended_files(modified_image)
            # Display details
            if appended_files:
                details = "ไฟล์ที่ถูกต่อท้าย:\n"
                for i, file_info in enumerate(appended_files):
                    details += f"\n{i+1}. ประเภท: {file_info['type']}"
                    details += f"\n   ขนาด: {file_info['size']} ไบต์"
                    details += f"\n   ตำแหน่ง: {file_info['positions']}"
                self.file_content_display.setPlainText(details)
            else:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ต่อท้าย")
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")

    def append_text_to_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        text = self.text_input.toPlainText()
        if not text:
            self.file_content_display.setPlainText("ไม่มีข้อความสำหรับต่อท้าย")
            return
        modified_image_path = os.path.splitext(image_path)
        modified_image_path = f"{modified_image_path[0]}_modified{modified_image_path[1]}"
        shutil.copy2(image_path, modified_image_path)
        original_size = os.path.getsize(image_path)  # อ่านขนาดไฟล์ต้นฉบับ
        with open(modified_image_path, 'ab') as image_file:
            # บันทึกจำนวนไฟล์ที่ต่อท้าย (1 ไฟล์)
            image_file.write(struct.pack('<I', 1))
            # บันทึกนามสกุลไฟล์ (txt)
            file_ext = "txt"
            image_file.write(struct.pack('<I', len(file_ext)))
            image_file.write(file_ext.encode('ascii'))
            # บันทึกขนาดข้อความและข้อมูล
            file_data = text.encode('utf-8')
            image_file.write(struct.pack('<Q', len(file_data)))
            image_file.write(file_data)
            # บันทึกขนาดไฟล์ต้นฉบับท้ายไฟล์
            image_file.write(struct.pack('<Q', original_size))
        self.file_content_display.setPlainText(f"ข้อความถูกต่อท้ายในไฟล์: {modified_image_path}")

    def verify_appended_files(self, image_path):
        """Updated to better identify text files"""
        appended_files = []
        try:
            with open(image_path, 'rb') as f:
                original_image_size = os.path.getsize(image_path.replace('_modified', ''))
                f.seek(original_image_size)
                num_files = struct.unpack('<I', f.read(4))[0]
                current_position = original_image_size + 4
                for _ in range(num_files):
                    ext_len = struct.unpack('<I', f.read(4))[0]
                    file_ext = f.read(ext_len).decode('ascii', errors='ignore')
                    file_size = struct.unpack('<Q', f.read(8))[0]
                    # Determine file type
                    file_type = file_ext
                    if file_ext.lower() == 'txt':
                        file_type = 'Text File (.txt)'
                    appended_files.append({
                        'type': file_type, 
                        'positions': [current_position],
                        'size': file_size
                    })
                    current_position += 4 + ext_len + 8 + file_size
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
        return appended_files

    def extract_appended_files(self, image_path):
        """
        ฟังก์ชันสำหรับถอดไฟล์ที่ถูกต่อท้ายจากไฟล์ภาพ
        คืนค่าเป็น Dictionary ของไฟล์ทั้งหมดที่ถูกถอด
        """
        extracted_files = []
        try:
            with open(image_path, 'rb') as f:
                # อ่านขนาดไฟล์ต้นฉบับจาก 8 ไบต์สุดท้าย
                f.seek(-8, os.SEEK_END)
                original_size = struct.unpack('<Q', f.read(8))[0]
                # ไปที่ตำแหน่งเริ่มต้นของข้อมูลเมตา
                f.seek(original_size)
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
                    # แยกประเภทไฟล์
                    if file_ext == 'txt':
                        # ถ้าเป็น .txt ให้เก็บข้อมูลเป็นข้อความ
                        extracted_files.append({
                            'type': 'text',
                            'content': file_data.decode('utf-8', errors='replace')
                        })
                    else:
                        # ไฟล์อื่นให้เก็บข้อมูล Binary
                        extracted_files.append({
                            'type': 'binary',
                            'ext': file_ext,
                            'data': file_data
                        })
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
            extracted_files = self.extract_appended_files(image_path)
            # แยกการจัดการไฟล์
            text_content = ""
            binary_files = []
            for file_info in extracted_files:
                if file_info['type'] == 'text':
                    # แสดงข้อความใน UI
                    text_content += "ข้อความที่ถูกถอด:\n"
                    text_content += "-" * 40 + "\n"
                    text_content += file_info['content'] + "\n"
                    text_content += "-" * 40 + "\n"
                else:
                    # บันทึกไฟล์อื่น
                    file_ext = file_info['ext']
                    file_data = file_info['data']
                    file_path = os.path.join(output_folder, f"extracted_file_{len(binary_files) + 1}.{file_ext}")
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    binary_files.append(file_path)
            # อัปเดต UI
            if text_content:
                self.file_content_display.setPlainText(text_content)
            if binary_files:
                QMessageBox.information(self, "สำเร็จ", f"บันทึกไฟล์อื่นๆ ที่: {output_folder}")
            if not extracted_files:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ถูกถอด")
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")

    def extract_text_content(self):
        """Extract only text content from appended files"""
        image_path, _ = QFileDialog.getOpenFileName(
            self, "เลือกไฟล์ภาพที่ถูกแก้ไข", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        try:
            with open(image_path, 'rb') as f:
                # Find original image size
                original_image_size = os.path.getsize(image_path.replace('_modified', ''))
                f.seek(original_image_size)
                # Read number of files
                num_files = struct.unpack('<I', f.read(4))[0]
                current_position = original_image_size + 4
                text_content = ""
                for _ in range(num_files):
                    # Read file extension
                    ext_len = struct.unpack('<I', f.read(4))[0]
                    file_ext = f.read(ext_len).decode('ascii', errors='ignore')
                    current_position += 4 + ext_len
                    # Read file size
                    file_size = struct.unpack('<Q', f.read(8))[0]
                    current_position += 8
                    # Read file data
                    file_data = f.read(file_size)
                    # If it's a text file, decode and display it
                    if file_ext.lower() == 'txt':
                        try:
                            decoded_text = file_data.decode('utf-8')
                            text_content += "ข้อความที่ถูกถอด:\n"
                            text_content += "-" * 40 + "\n"
                            text_content += decoded_text + "\n"
                            text_content += "-" * 40 + "\n"
                        except UnicodeDecodeError:
                            text_content += "ข้อผิดพลาด: ไม่สามารถถอดรหัสข้อความได้\n"
                    current_position += file_size
            if text_content:
                self.file_content_display.setPlainText(text_content)
            else:
                self.file_content_display.setPlainText("ไม่พบข้อความที่ถูกต่อท้ายในไฟล์นี้")
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")