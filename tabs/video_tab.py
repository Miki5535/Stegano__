from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QLineEdit,
    QLabel, QHBoxLayout, QComboBox, QFileDialog, QTextEdit
)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
import os
import cv2
from utils.steganography import string_to_binary, binary_to_string
import time


class VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.max_bits = 0  # เก็บจำนวนบิตสูงสุดของวิดีโอ
        self.initUI()
        self.load_example_video()
        self.setAcceptDrops(True)

    def initUI(self):
        layout = QVBoxLayout()

        # Video file selection group
        video_group = QGroupBox("จัดการไฟล์วิดีโอ")
        video_layout = QVBoxLayout()

        # Row layout for buttons and dropdown
        video_row_layout = QHBoxLayout()
        self.select_video_button = QPushButton("เลือกไฟล์วิดีโอ")
        self.select_video_button.clicked.connect(self.select_video)
        self.load_example_button = QPushButton("โหลดวิดีโอตัวอย่าง")
        self.load_example_button.clicked.connect(self.load_example_video)
        self.load_example_button.setStyleSheet("background-color: blue; color: white;")
        self.example_video_dropdown = QComboBox()
        self.example_video_dropdown.setPlaceholderText("เลือกไฟล์วิดีโอตัวอย่าง")
        self.example_video_dropdown.currentIndexChanged.connect(self.select_example_video)
        self.open_output_folder_button = QPushButton("เปิดโฟลเดอร์ Output")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)
        self.open_output_folder_button.setStyleSheet("background-color: black; color: white;")

        video_row_layout.addWidget(self.example_video_dropdown)
        video_row_layout.addWidget(self.select_video_button)
        video_row_layout.addWidget(self.load_example_button)
        video_row_layout.addWidget(self.open_output_folder_button)
        video_layout.addLayout(video_row_layout)

        # File path preview
        self.video_path_label = QLabel("ไม่ได้เลือกไฟล์")
        self.video_path_label.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        self.video_path_label.setMinimumHeight(30)
        self.video_path_label.setMinimumWidth(400)
        video_layout.addWidget(self.video_path_label)

        # Video preview
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        video_layout.addWidget(self.video_widget)

        # Message input field
        self.video_message_input = QTextEdit()
        self.video_message_input.setPlaceholderText("ข้อความที่ต้องการซ่อนในไฟล์วิดีโอ")
        video_layout.addWidget(self.video_message_input)

        # Bit info label
        self.bit_info_label = QLabel("บิตสูงสุดที่รองรับ: - | บิตที่ใช้: - | บิตคงเหลือ: -")
        self.bit_info_label.setStyleSheet("padding: 5px; font-weight: bold;")
        video_layout.addWidget(self.bit_info_label)

        # Buttons for hiding, extracting, playing, stopping
        video_buttons_layout = QHBoxLayout()
        self.hide_video_button = QPushButton("ซ่อนข้อความในไฟล์วิดีโอ")
        self.hide_video_button.clicked.connect(self.hide_message_in_video)
        self.hide_video_button.setStyleSheet("background-color: purple; color: white;")
        self.extract_video_button = QPushButton("ถอดข้อความจากไฟล์วิดีโอ")
        self.extract_video_button.clicked.connect(self.extract_message_from_video)
        self.extract_video_button.setStyleSheet("background-color: orange; color: white;")
        self.play_video_button = QPushButton("เล่น")
        self.play_video_button.clicked.connect(self.play_video)
        self.play_video_button.setStyleSheet("background-color: green; color: white;")
        self.stop_video_button = QPushButton("หยุด")
        self.stop_video_button.clicked.connect(self.stop_video)
        self.stop_video_button.setStyleSheet("background-color: red; color: white;")

        video_buttons_layout.addWidget(self.hide_video_button)
        video_buttons_layout.addWidget(self.extract_video_button)
        video_buttons_layout.addWidget(self.play_video_button)
        video_buttons_layout.addWidget(self.stop_video_button)
        video_layout.addLayout(video_buttons_layout)

        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # Result output area
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        layout.addWidget(self.result_output)

        self.setLayout(layout)

        # Connect text changed event
        self.video_message_input.textChanged.connect(self.update_bit_display)

    def select_video(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(
            self,
            "เลือกไฟล์วิดีโอ",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if video_path:
            self.video_path = video_path
            self.video_path_label.setText(video_path)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.media_player.play()
            self.calculate_max_bit_capacity()  # คำนวณแคปซิตี้ครั้งเดียวตอนโหลดวิดีโอ
            self.update_bit_display()

    def select_example_video(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "vdio")
        selected_video = self.example_video_dropdown.currentText()
        if selected_video != "เลือกไฟล์วิดีโอตัวอย่าง":
            selected_audio_path = os.path.join(example_folder_path, selected_video)
            self.video_path_label.setText(selected_audio_path)
            self.result_output.append(f"เลือกเสียงตัวอย่าง: <font color='blue'>{selected_audio_path}</font>")
            self.video_path = selected_audio_path
            self.calculate_max_bit_capacity()
            self.update_bit_display()

    def load_example_video(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "vdio")
        if os.path.exists(example_folder_path):
            vdio_files = [f for f in os.listdir(example_folder_path) if f.endswith(('.avi', '.mp4', '.mkv'))]
            self.example_video_dropdown.clear()
            self.example_video_dropdown.addItem("เลือกไฟล์วิดีโอตัวอย่าง")
            self.example_video_dropdown.addItems(vdio_files)
            self.result_output.append("<font color='blue'>โหลดไฟล์วิดีโอตัวอย่างสำเร็จ</font>")
        else:
            self.result_output.append("<font color='red'>ไม่พบโฟลเดอร์วิดีโอตัวอย่าง</font>")

    def play_video(self):
        if self.video_path:
            self.media_player.play()

    def stop_video(self):
        self.media_player.stop()

    def open_output_folder(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        output_path = os.path.join(parent_directory, "vdio", "output")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                self.video_path = file_path
                self.video_path_label.setText(file_path)
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
                self.media_player.play()
                self.result_output.append(f"<font color='blue'>เลือกไฟล์วิดีโอผ่านการลากและวาง: {file_path}</font>")
                self.calculate_max_bit_capacity()
                self.update_bit_display()
            else:
                self.result_output.append("<font color='red'>ไฟล์ที่ลากเข้ามาไม่ใช่วิดีโอที่รองรับ!</font>")

    def calculate_max_bit_capacity(self):
        if not self.video_path:
            self.max_bits = 0
            return 0
        try:
            cap = cv2.VideoCapture(self.video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            self.max_bits = width * height * frame_count
            return self.max_bits
        except Exception as e:
            print("Error calculating max bit capacity:", e)
            return 0

    def update_bit_display(self):
        if not self.video_path:
            self.bit_info_label.setText("บิตสูงสุดที่รองรับ: - | บิตที่ใช้: - | บิตคงเหลือ: -")
            return

        message = self.video_message_input.toPlainText()
        total_bits_needed = len(string_to_binary(message)) + 16  # +16 for end marker

        try:
            remaining_bits = self.max_bits - total_bits_needed
            used_percent = min(100, total_bits_needed / self.max_bits * 100)

            color_used = "green" if total_bits_needed <= self.max_bits else "red"
            color_remaining = "green" if remaining_bits > 0 else "red"

            self.bit_info_label.setText(
                f"บิตสูงสุดที่รองรับ: {self.max_bits} | "
                f"<font color='{color_used}'>บิตที่ใช้: {total_bits_needed}</font> | "
                f"<font color='{color_remaining}'>บิตคงเหลือ: {remaining_bits}</font> | "
                f"({used_percent:.1f}%)"
            )
        except Exception as e:
            self.bit_info_label.setText("เกิดข้อผิดพลาดในการคำนวณบิต")

    def hide_message_in_video(self):
        if not self.video_path:
            self.result_output.append("กรุณาเลือกไฟล์วิดีโอก่อน!")
            return
        message = self.video_message_input.toPlainText()
        if not message:
            self.result_output.append("กรุณากรอกข้อความที่จะซ่อนในวิดีโอ!")
            return
        try:
            input_video = self.video_path
            if not os.path.exists(input_video):
                self.result_output.append("ไม่พบไฟล์วิดีโออินพุต!")
                return
            current_directory = os.path.dirname(os.path.realpath(__file__))
            parent_directory = os.path.dirname(current_directory)
            directory = os.path.join(parent_directory, "vdio", "output")
            if not os.path.exists(directory):
                os.makedirs(directory)
            if not os.access(directory, os.W_OK):
                self.result_output.append("ไม่สามารถเขียนไฟล์ในไดเรกทอรีเป้าหมายได้!")
                return
            filename = os.path.splitext(os.path.basename(input_video))[0]
            timestamp = time.strftime("%Y%m%d%H%M%S")
            output_video = os.path.join(directory, f"{filename}_hidden_{timestamp}.avi")
            self.encode_message_in_video(input_video, output_video, message)
        except Exception as e:
            self.result_output.append(f"เกิดข้อผิดพลาด: {e}")

    def extract_message_from_video(self):
        if not self.video_path:
            self.result_output.append("กรุณาเลือกไฟล์วิดีโอก่อน!")
            return
        try:
            hidden_message = self.decode_message_from_video(self.video_path)
            self.result_output.append("ข้อความที่ถอดจากวีดีโอ :<font color='green'>" + hidden_message)
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")

    def encode_message_in_video(self, input_video, output_video, message):
        binary_message = string_to_binary(message) + '0' * 8
        binary_message += '1111111111111110'  # End marker
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            self.result_output.append("Failed to open input video file.")
            return
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        message_idx = 0
        total_bits = len(binary_message)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if message_idx < total_bits:
                for i in range(frame.shape[0]):
                    for j in range(frame.shape[1]):
                        if message_idx < total_bits:
                            frame[i, j, 0] = (frame[i, j, 0] & 0xFE) | int(binary_message[message_idx])
                            message_idx += 1
            out.write(frame)
        cap.release()
        out.release()
        self.result_output.append(f"<font color='blue'>ซ่อนข้อความในวิดีโอสำเร็จ! จำนวนบิตที่ซ่อน: {message_idx} จากทั้งหมด {total_bits} บิต.")
        if message_idx < total_bits:
            self.result_output.append("<font color='red'>คำเตือน: มีบางบิตของข้อความที่ไม่ได้ถูกซ่อนในวิดีโอ.")

    def decode_message_from_video(self, encoded_video):
        cap = cv2.VideoCapture(encoded_video)
        if not cap.isOpened():
            self.result_output.append("Failed to open encoded video file.")
            return ""
        binary_message = ""
        bit_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    binary_message += str(frame[i, j, 0] & 1)
                    bit_count += 1
                    if binary_message[-16:] == '1111111111111110':
                        cap.release()
                        binary_message = binary_message[:-16]
                        return binary_to_string(binary_message)
        cap.release()
        return "No hidden message found."