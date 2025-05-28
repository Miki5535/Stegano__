
from PyQt5.QtWidgets import QFileDialog,QProgressBar, QComboBox, QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt,QCoreApplication
import os
from utils.steganography import (hide_message_lsb_from_steganography ,    retrieve_message_lsb_from_steganography,
                                 hide_message_transform_domain_from_steganography ,      retrieve_message_transform_domain_from_steganography,
                                 hide_message_masking_filtering_from_steganography ,    retrieve_message_masking_filtering_from_steganography,
                                 hide_message_palette_based_from_steganography ,    retrieve_message_palette_based_from_steganography,
                                 hide_message_spread_spectrum_from_steganography , retrieve_message_spread_spectrum_from_steganography,
                                 hide_message_edge_detection , retrieve_message_edge_detection,
                                 hide_message_alpha_channel , retrieve_message_alpha_channel
                                 )
from utils.check_bit import(check_bit_palette,check_bit_message,check_bit_lsb,check_bit_edge_detection,check_bit_alpha_channel,check_bit_masking_filtering)
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
import uuid
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal



class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_example_image()
        self.setAcceptDrops(True) 
        
        self.message_input.textChanged.connect(self.check_message_length)
        self.mode_selector.currentIndexChanged.connect(self.update_num_from_mode)

    def initUI(self):
        layout = QVBoxLayout()
        self.num = 0
        self.previous_text_length = 0

        # Image handling group
        image_group = QGroupBox("จัดการรูปภาพ")
        image_layout = QVBoxLayout()

        # Buttons layout
        button_layout = QHBoxLayout()

        self.select_image_button = QPushButton("เลือกไฟล์ภาพ")
        self.select_image_button.setToolTip("เลือกไฟล์ภาพที่คุณต้องการใช้")
        self.select_image_button.clicked.connect(self.select_image)
        

        self.number_selector = QComboBox()
        self.number_selector.addItems([str(i) for i in range(1, 11)])
        self.number_selector.setToolTip("เลือกตัวอย่างภาพที่ระบบเตรียมไว้ให้")
        self.number_selector.currentIndexChanged.connect(self.load_example_image)

        # Dropdown for selecting hiding mode (Moved here)
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "LSB",
            # "Transform Domain Techniques",
            "Masking and Filtering",
            "Palette-based Techniques",
            # "Spread Spectrum",
            "Edge Detection",
            "Alpha Channel"
        ])
        self.mode_selector.setToolTip("เลือกโหมดการซ่อนข้อความ")

        # Label for mode selection
        mode_label = QLabel("เลือกโหมดการซ่อนข้อความ:")
        mode_label.setStyleSheet("background: transparent;")
        mode_label.setFixedWidth(140)  # กำหนดความกว้างเป็น 200px

        pic_label = QLabel("เลือกตัวอย่างภาพจากระบบ:")
        pic_label.setStyleSheet("background: transparent;")
        pic_label.setFixedWidth(140)  # กำหนดความกว้างเป็น 250px


        # Add widgets into button_layout
        button_layout.addWidget(pic_label)
        button_layout.addWidget(self.number_selector)
        
        button_layout.addWidget(mode_label)
        button_layout.addWidget(self.mode_selector)
        button_layout.addWidget(self.select_image_button)

        # Image preview
        self.image_label = QLabel()
        self.image_label.setFixedSize(400, 200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px dashed #BBDEFB;
                border-radius: 8px;
            }
        """)

        # Message next to the image preview
        self.numtext_message_label = QLabel()
        self.numtext_message_label.setText(f"ตัวอักษรที่ใส่ได้ {self.num} ตัว")
        self.numtext_message_label.setStyleSheet("color: green; font-weight: bold; font-size: 16px;")
        self.numtext_message_label.setAlignment(Qt.AlignCenter)

        # Create a layout to hold both the image and error message
        image_and_error_layout = QHBoxLayout()
        image_and_error_layout.addWidget(self.image_label)
        image_and_error_layout.addWidget(self.numtext_message_label)

        # Message input and output layout
        message_output_layout = QHBoxLayout()

        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("ข้อความที่ต้องการซ่อนในภาพ")
        self.message_input.setMinimumHeight(100)
        self.message_input.setStyleSheet("font-size: 14px; padding: 5px;")

        # Output Text Area
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Consolas', monospace;
            }
        """)

        message_output_layout.addWidget(self.message_input)
        message_output_layout.addWidget(self.result_output)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)  # Initially hidden

        # Hide/Extract buttons
        action_layout = QHBoxLayout()
        self.hide_button = QPushButton("ซ่อนข้อความ")
        self.hide_button.setToolTip("เริ่มซ่อนข้อความลงในภาพ")
        self.hide_button.clicked.connect(self.hide_message)
        self.hide_button.setStyleSheet("background-color: purple; color: white;")

        self.extract_button = QPushButton("ถอดข้อความ")
        self.extract_button.setToolTip("เริ่มถอดข้อความจากภาพ")
        self.extract_button.clicked.connect(self.retrieve_message)
        self.extract_button.setStyleSheet("background-color: orange; color: white;")

        action_layout.addWidget(self.hide_button)
        action_layout.addWidget(self.extract_button)

        # Output Folder button
        self.output_folder_button = QPushButton("เปิดโฟลเดอร์ Output")
        self.output_folder_button.setToolTip("เปิดโฟลเดอร์เพื่อดูผลลัพธ์")
        self.output_folder_button.clicked.connect(self.open_output_folder)
        self.output_folder_button.setStyleSheet("background-color: black; color: white;")
        action_layout.addWidget(self.output_folder_button)

        # Add components to layout
        image_layout.addLayout(button_layout)
        image_layout.addLayout(image_and_error_layout)
        image_layout.addLayout(message_output_layout)
        image_layout.addWidget(self.progress_bar)
        image_layout.addLayout(action_layout)

        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        self.setLayout(layout)



    def open_output_folder(self): 
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "photoexample", "output")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Image Files (*.png; *.jpg; *.jpeg; *.bmp;)")
        if file_path:
            self.selected_image = file_path
            self.result_output.append(f"เลือกไฟล์ภาพ: {file_path}")
            pixmap = QPixmap(self.selected_image)
            self.image_label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio))
            
            self.update_num_from_mode()

    def load_example_image(self):
        num = self.number_selector.currentText() 
        example_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'photoexample', f'example{num}.png')

        if os.path.exists(example_image_path):
            self.selected_image = example_image_path
            pixmap = QPixmap(example_image_path)
            self.image_label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio))
            self.result_output.append(f"โหลดภาพตัวอย่าง: {example_image_path}")
            
            self.update_num_from_mode()
            
        else:
            self.result_output.append("<font color='red'>ไม่พบไฟล์ภาพตัวอย่าง</font>")


    def hide_message(self):
        if not hasattr(self, "selected_image"):
            self.result_output.append("<font color='red'>กรุณาเลือกไฟล์ภาพ</font>")
            return

        mode = self.mode_selector.currentText()
        message = self.message_input.toPlainText()
        image = self.selected_image
        max_length = self.check_bit_pic()

        if len(message) > max_length:
            self.result_output.append(f"<font color='red'>ข้อความยาวเกินไป (สูงสุด {max_length} ตัวอักษร)</font>")
            return

        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        output_folder = os.path.join(parent_directory, "photoexample", "output")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        output_filename = f"{timestamp}_{unique_id}.png"
        output_path = os.path.join(output_folder, output_filename)

        self.progress_bar.setValue(0)

        # เรียกใช้งาน Thread
        self.worker = SteganographyWorker(mode, image, message, output_path)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(lambda msg: self.result_output.append(msg))

        self.worker.start()


    def retrieve_message(self):
        if not hasattr(self, "selected_image"):
            self.result_output.append("<font color='red'>กรุณาเลือกไฟล์ภาพ</font>")
            return

        mode = self.mode_selector.currentText()
        image_path = self.selected_image

        self.progress_bar.setValue(0)

        # ใช้ RetrieveWorker เพื่อทำให้ไม่ถ่วง UI
        self.retrieve_worker = RetrieveWorker(mode, image_path)
        self.retrieve_worker.progress.connect(self.progress_bar.setValue)
        self.retrieve_worker.finished.connect(lambda msg: self.result_output.append(msg))

        self.retrieve_worker.start()



    def dragEnterEvent(self, event):
            """ตรวจสอบว่าไฟล์ที่ลากเข้ามาถูกต้องหรือไม่"""
            if event.mimeData().hasUrls():  # ตรวจสอบว่ามี URL หรือไฟล์ที่ลากเข้ามาหรือไม่
                event.accept()
            else:
                event.ignore()

    def dropEvent(self, event):
        """จัดการไฟล์เมื่อปล่อยลงบน QLabel"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_path = urls[0].toLocalFile()  # ใช้เฉพาะไฟล์แรก
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.selected_image = file_path
                pixmap = QPixmap(file_path)
                self.image_label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio))
                self.result_output.append(f"เลือกไฟล์ผ่านการลากและวาง: {file_path}")
                
                self.update_num_from_mode()
            else:
                self.result_output.append("<font color='red'>ไฟล์ที่ลากมาไม่ใช่รูปภาพ</font>")

    def check_bit_pic(self):
        # ตรวจสอบว่า image_path เป็นสตริงหรือไม่
        image_path = self.selected_image
        # print(f"Using image path: {image_path}")
        mode = self.mode_selector.currentText()

        # Calculate maximum message length based on different techniques
        if mode == "LSB":
            pic_bit = check_bit_lsb(image_path)
        
        elif mode == "Transform Domain Techniques":
            # More conservative estimate due to transform coefficients
            pic_bit = 9999
        
        elif mode == "Masking and Filtering":
            # More limited capacity due to visibility concerns
            pic_bit = check_bit_masking_filtering(image_path)
        
        elif mode == "Palette-based Techniques":
            pic_bit = check_bit_palette(image_path)
            
        elif mode == "Spread Spectrum":
            # Conservative estimate due to spreading factor
            pic_bit = 9999
        
        elif mode == "Edge Detection":
            pic_bit = check_bit_edge_detection(image_path)
        elif mode == "Alpha Channel":
            pic_bit = check_bit_alpha_channel(image_path)
            if pic_bit ==0:
                 self.result_output.append("<font color='red'>ภาพต้องเป็น PNG ที่มี Alpha Channel</font>")
        
        return pic_bit


    def check_message_length(self):
        num,setText,setStyleSheet,current_length = check_bit_message(self.message_input.toPlainText(),self.previous_text_length,self.num)
        self.num =num
        self.numtext_message_label.setText(setText)
        self.numtext_message_label.setStyleSheet(setStyleSheet)
        self.previous_text_length = current_length


    def update_num_from_mode(self):
        """อัปเดตค่า self.num เมื่อโหมดถูกเปลี่ยน"""
        self.num = self.check_bit_pic()  # คำนวณค่าใหม่ตามโหมด
        self.previous_text_length = 0  # รีเซ็ตค่าความยาวข้อความ
        self.check_message_length()  # อัปเดตการคำนวณข้อความ
        self.numtext_message_label.setText(f"bit เหลือ {self.num}")
        self.progress_bar.setValue(0)



    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.setValue(value)




class SteganographyWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, mode, image, message, output_path):
        super().__init__()
        self.mode = mode
        self.image = image
        self.message = message
        self.output_path = output_path

    def run(self):
        try:
            for i in range(101):  # จำลองการอัปเดต Progress Bar
                self.progress.emit(i)
                QThread.msleep(50)  # ทำให้ดูเหมือนมีการประมวลผล
           
            if self.mode == "LSB":
                hide_message_lsb_from_steganography(self.image, self.message, self.output_path)
            elif self.mode == "Transform Domain Techniques":
                hide_message_transform_domain_from_steganography(self.image, self.message, self.output_path)
            elif self.mode == "Masking and Filtering":
                hide_message_masking_filtering_from_steganography(self.image, self.message, self.output_path)
            elif self.mode == "Palette-based Techniques":
                hide_message_palette_based_from_steganography(self.image, self.message, self.output_path)
            elif self.mode == "Spread Spectrum":
                hide_message_spread_spectrum_from_steganography(self.image, self.message, self.output_path)
            elif self.mode == "Edge Detection":
                hide_message_edge_detection(self.image, self.message, self.output_path)
            elif self.mode == "Alpha Channel":
                hide_message_alpha_channel(self.image, self.message, self.output_path)

            self.finished.emit(f"ข้อความถูกซ่อนใน: {self.output_path}")
        except Exception as e:
            self.finished.emit(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")




class RetrieveWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, mode, image_path):
        super().__init__()
        self.mode = mode
        self.image_path = image_path

    def run(self):
        try:
            for i in range(101):  # จำลองการอัปเดต Progress Bar
                self.progress.emit(i)
                QThread.msleep(50)  # ทำให้ดูเหมือนมีการประมวลผล

            if self.mode == "LSB":
                retrieved_message = retrieve_message_lsb_from_steganography(self.image_path)
            elif self.mode == "Transform Domain Techniques":
                retrieved_message = retrieve_message_transform_domain_from_steganography(self.image_path)
            elif self.mode == "Masking and Filtering":
                retrieved_message = retrieve_message_masking_filtering_from_steganography(self.image_path)
            elif self.mode == "Palette-based Techniques":
                retrieved_message = retrieve_message_palette_based_from_steganography(self.image_path)
            elif self.mode == "Spread Spectrum":
                retrieved_message = retrieve_message_spread_spectrum_from_steganography(self.image_path)
            elif self.mode == "Edge Detection":
                retrieved_message = retrieve_message_edge_detection(self.image_path)
            elif self.mode == "Alpha Channel":
                retrieved_message = retrieve_message_alpha_channel(self.image_path)
            else:
                self.finished.emit("<font color='red'>โหมดที่เลือกไม่รองรับ</font>")
                return

            if retrieved_message:
                self.finished.emit(f"ข้อความที่ถูกถอดออกมา: {retrieved_message}")
            else:
                self.finished.emit("<font color='red'>ไม่พบข้อความที่ถูกซ่อนอยู่ในภาพนี้</font>")

        except Exception as e:
            self.finished.emit(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")