from PyQt5.QtWidgets import QFileDialog, QComboBox, QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton, QLineEdit, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os
import random
from utils.steganography import hide_message, retrieve_message
import utils.encryption as encryption
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_example_image()

    def initUI(self):
        layout = QVBoxLayout()

        # Image handling group
        image_group = QGroupBox("จัดการรูปภาพ")
        image_layout = QVBoxLayout()

        # Buttons layout
        button_layout = QHBoxLayout()

        self.select_image_button = QPushButton("เลือกไฟล์ภาพ")
        self.select_image_button.clicked.connect(self.select_image)

        self.number_selector = QComboBox()
        self.number_selector.addItems([str(i) for i in range(1, 11)])

        self.load_example_button = QPushButton("โหลดภาพตัวอย่าง")
        self.load_example_button.clicked.connect(self.load_example_image)
        self.load_example_button.setStyleSheet("background-color: green; color: white;")

        button_layout.addWidget(self.number_selector)
        button_layout.addWidget(self.load_example_button)
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

        # Message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("ข้อความที่ต้องการซ่อน")

        # Hide/Extract buttons
        action_layout = QHBoxLayout()
        self.hide_button = QPushButton("ซ่อนข้อความ")
        self.hide_button.clicked.connect(self.hide_message)
        self.hide_button.setStyleSheet("background-color: purple; color: white;")

        self.extract_button = QPushButton("ถอดข้อความ")
        self.extract_button.clicked.connect(self.retrieve_message)
        self.extract_button.setStyleSheet("background-color: orange; color: white;")

        action_layout.addWidget(self.hide_button)
        action_layout.addWidget(self.extract_button)

        # Output Folder button
        self.output_folder_button = QPushButton("เปิดโฟลเดอร์ Output")
        self.output_folder_button.clicked.connect(self.open_output_folder)
        self.output_folder_button.setStyleSheet("background-color: back; color: white;")
        action_layout.addWidget(self.output_folder_button)

        # Add components to layout
        image_layout.addLayout(button_layout)
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.message_input)
        image_layout.addLayout(action_layout)

        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

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
        layout.addWidget(self.result_output)

        self.setLayout(layout)

    def open_output_folder(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        # เข้าถึงโฟลเดอร์ photoexample/output
        parent_directory = os.path.dirname(current_directory)  
        output_path = os.path.join(parent_directory, "photoexample", "output")
        
        # ตรวจสอบว่ามีโฟลเดอร์อยู่หรือไม่ ถ้าไม่มีก็สร้างขึ้น
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # เปิดโฟลเดอร์ด้วย QDesktopServices
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Image Files (*.png; *.jpg; *.jpeg; *.bmp;)")
        if file_path:
            self.selected_image = file_path
            self.result_output.append(f"เลือกไฟล์ภาพ: {file_path}")
            pixmap = QPixmap(self.selected_image)
            self.image_label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio))

    def load_example_image(self):
        num = self.number_selector.currentText()
        
        # เลื่อนขึ้น 1 ระดับจากโฟลเดอร์ปัจจุบัน
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)  
        example_image_path = os.path.join(parent_directory, 'photoexample', f'example{num}.png')

        if os.path.exists(example_image_path):
            self.selected_image = example_image_path
            pixmap = QPixmap(example_image_path)
            self.image_label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio))
            self.result_output.append(f"โหลดภาพตัวอย่าง: {example_image_path}")
        else:
            self.result_output.append("<font color='red'>ไม่พบไฟล์ภาพตัวอย่าง</font>")

    def hide_message(self):
        message = self.message_input.text()
        if not hasattr(self, "selected_image"):
            self.result_output.append("<font color='red'>กรุณาเลือกไฟล์ภาพ</font>")
            return

        output_folder = os.path.join(os.path.dirname(self.selected_image), 'output')
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        random_number = random.randint(1, 1000000)
        output_path = os.path.join(output_folder, f"{random_number}.png")
        hide_message(self.selected_image, message, output_path)
        self.result_output.append(f"ข้อความถูกซ่อนใน: {output_path}")

    def retrieve_message(self):
        if not hasattr(self, "selected_image"):
            self.result_output.append("<font color='red'>กรุณาเลือกไฟล์ภาพ</font>")
            return

        retrieved_message = retrieve_message(self.selected_image)
        if retrieved_message:
            self.result_output.append(f"ข้อความที่ถูกถอดออกมา: {retrieved_message}")
        else:
            self.result_output.append("<font color='red'>ไม่พบข้อความที่ถูกซ่อนอยู่ในภาพนี้</font>")