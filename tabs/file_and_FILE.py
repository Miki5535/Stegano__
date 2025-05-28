import logging
import shutil
import struct
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QFileDialog, QTextEdit, QScrollArea, QGridLayout, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QUrl
import os


class FileAndFileTab(QWidget):
    def __init__(self):
        super().__init__()
        self.files_to_append = []
        self.initUI()
        self.setAcceptDrops(True)

    def initUI(self):
        main_layout = QVBoxLayout()

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

        self.file_content_display = QTextEdit()
        self.file_content_display.setReadOnly(True)
        self.file_content_display.setPlaceholderText("ผลลัพธ์ / Log จะแสดงที่นี่...")

        layout_file.addWidget(self.scroll_area)
        layout_file.addWidget(self.info_label)
        layout_file.addLayout(button_layout)
        layout_file.addWidget(self.file_content_display)
        group_file.setLayout(layout_file)

        horizontal_group_layout = QHBoxLayout()
        horizontal_group_layout.addWidget(group_text)
        horizontal_group_layout.addWidget(group_file)

        group_text.setMinimumHeight(400)
        group_file.setMinimumHeight(400)

        main_layout.addLayout(horizontal_group_layout, stretch=3)
        main_layout.addWidget(self.file_content_display, stretch=1)
        self.setLayout(main_layout)

    def append_files_to_image(self, image_path, file_paths):
        if not file_paths:
            raise ValueError("ไม่มีไฟล์ที่เลือก")
        modified_image_path = os.path.splitext(image_path)[0] + "_modified" + os.path.splitext(image_path)[1]
        shutil.copy2(image_path, modified_image_path)
        with open(modified_image_path, 'ab') as image_file:
            original_size = os.path.getsize(image_path)
            image_file.write(struct.pack('<I', len(file_paths)))
            for file_path in file_paths:
                _, ext = os.path.splitext(file_path)
                ext = ext[1:]
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                image_file.write(struct.pack('<I', len(ext)))
                image_file.write(ext.encode('ascii'))
                image_file.write(struct.pack('<Q', len(file_data)))
                image_file.write(file_data)
            image_file.write(struct.pack('<Q', original_size))
        return modified_image_path

    def append_text_to_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        text = self.text_input.toPlainText()
        if not text:
            self.file_content_display.setPlainText("ไม่มีข้อความสำหรับต่อท้าย")
            return
        modified_image_path = os.path.splitext(image_path)[0] + "_modified" + os.path.splitext(image_path)[1]
        shutil.copy2(image_path, modified_image_path)
        with open(modified_image_path, 'ab') as image_file:
            image_file.write(struct.pack('<I', 1))
            image_file.write(struct.pack('<I', len('txt')))
            image_file.write(b'txt')
            file_data = text.encode('utf-8')
            image_file.write(struct.pack('<Q', len(file_data)))
            image_file.write(file_data)
            image_file.write(struct.pack('<Q', os.path.getsize(image_path)))
        self.file_content_display.setPlainText(f"ข้อความถูกต่อท้ายในไฟล์: {modified_image_path}")

    def file_to(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        try:
            files_to_append = self.files_to_append
            modified_image = self.append_files_to_image(image_path, files_to_append)
            self.file_content_display.setPlainText(f"ภาพที่แก้ไขถูกบันทึกที่: {modified_image}")
            appended_files = self.verify_appended_files(modified_image)
            if appended_files:
                details = "ไฟล์ที่ถูกต่อท้าย:\n"
                for i, file_info in enumerate(appended_files):
                    details += f"\n{i+1}. ประเภท: {file_info['type']}"
                    details += f"\n   ขนาด: {file_info['size']} ไบต์"
                self.file_content_display.setPlainText(details)
            else:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ต่อท้าย")
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")

    def verify_appended_files(self, image_path):
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
                    file_type = file_ext
                    if file_ext.lower() == 'txt':
                        file_type = 'Text File (.txt)'
                    appended_files.append({
                        'type': file_type,
                        'size': file_size
                    })
                    current_position += 4 + ext_len + 8 + file_size
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
        return appended_files

    def extract_appended_files(self, image_path):
        extracted_files = []
        try:
            with open(image_path, 'rb') as f:
                f.seek(-8, os.SEEK_END)
                original_size = struct.unpack('<Q', f.read(8))[0]
                f.seek(original_size)
                num_files = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_files):
                    ext_len = struct.unpack('<I', f.read(4))[0]
                    file_ext = f.read(ext_len).decode('ascii', errors='ignore')
                    file_size = struct.unpack('<Q', f.read(8))[0]
                    file_data = f.read(file_size)
                    if file_ext == 'txt':
                        extracted_files.append({
                            'type': 'text',
                            'content': file_data.decode('utf-8', errors='replace')
                        })
                    else:
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
            text_content = ""
            binary_files = []
            for file_info in extracted_files:
                if file_info['type'] == 'text':
                    text_content += "ข้อความที่ถูกถอด:\n"
                    text_content += "-" * 40 + "\n"
                    text_content += file_info['content'] + "\n"
                    text_content += "-" * 40 + "\n"
                else:
                    file_path = os.path.join(output_folder, f"extracted_file_{len(binary_files) + 1}.{file_info['ext']}")
                    with open(file_path, 'wb') as f:
                        f.write(file_info['data'])
                    binary_files.append(file_path)
            if text_content:
                self.file_content_display.setPlainText(text_content)
            if binary_files:
                QMessageBox.information(self, "สำเร็จ", f"บันทึกไฟล์อื่นๆ ที่: {output_folder}")
            if not extracted_files:
                self.file_content_display.setPlainText("ไม่พบไฟล์ที่ถูกถอด")
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")

    def extract_text_content(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพที่ถูกแก้ไข", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.setPlainText("กรุณาเลือกไฟล์ภาพก่อน")
            return
        try:
            with open(image_path, 'rb') as f:
                original_image_size = os.path.getsize(image_path.replace('_modified', ''))
                f.seek(original_image_size)
                num_files = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_files):
                    ext_len = struct.unpack('<I', f.read(4))[0]
                    file_ext = f.read(ext_len).decode('ascii', errors='ignore')
                    file_size = struct.unpack('<Q', f.read(8))[0]
                    file_data = f.read(file_size)
                    if file_ext.lower() == 'txt':
                        decoded_text = file_data.decode('utf-8')
                        self.file_content_display.setPlainText(f"ข้อความที่ถูกถอด:\n{decoded_text}")
                        return
                self.file_content_display.setPlainText("ไม่พบข้อความที่ถูกต่อท้าย")
        except Exception as e:
            self.file_content_display.setPlainText(f"เกิดข้อผิดพลาด: {e}")

    def select_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์", "", "All Files (*.*)")
        if file_paths:
            self.files_to_append.extend(file_paths)
            self.info_label.setText(f"เลือกไฟล์ {len(self.files_to_append)} ไฟล์")
            self.file_content_display.setPlainText("\n".join(self.files_to_append))
            self.update_preview(self.files_to_append)

    def clear_all_files(self):
        if not self.files_to_append:
            return
        reply = QMessageBox.question(self, "ยืนยันการลบ", "คุณต้องการลบไฟล์ทั้งหมดใช่หรือไม่?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.files_to_append.clear()
            for i in reversed(range(self.preview_layout.count())):
                widget = self.preview_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            self.info_label.setText("ไม่มีไฟล์ที่เลือก")
            self.file_content_display.clear()

    def update_preview(self, file_paths):
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        row, col = 0, 0
        for file_path in file_paths:
            icon_label = QLabel()
            pixmap = QPixmap("icons/file.png").scaled(64, 64)
            icon_label.setPixmap(pixmap)
            name_label = QLabel(os.path.basename(file_path))
            delete_button = QPushButton("ลบ")
            delete_button.clicked.connect(lambda _, fp=file_path: self.remove_preview(fp))
            container = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(icon_label)
            layout.addWidget(name_label)
            layout.addWidget(delete_button)
            container.setLayout(layout)
            self.preview_layout.addWidget(container, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def remove_preview(self, file_path):
        if file_path in self.files_to_append:
            self.files_to_append.remove(file_path)
            self.update_preview(self.files_to_append)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if file_paths:
            self.files_to_append.extend(file_paths)
            self.update_preview(self.files_to_append)