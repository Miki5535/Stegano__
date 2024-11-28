import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QLineEdit,
    QLabel, QHBoxLayout, QFileDialog, QProgressDialog
)


class VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Video handling group
        video_group = QGroupBox("จัดการไฟล์วิดีโอ")
        video_layout = QVBoxLayout()

        self.select_video_button = QPushButton("เลือกไฟล์วิดีโอ")
        self.select_video_button.clicked.connect(self.select_video)

        self.video_path_label = QLabel("ไม่ได้เลือกไฟล์")

        self.video_message_input = QLineEdit()
        self.video_message_input.setPlaceholderText("ข้อความที่ต้องการซ่อนในไฟล์วิดีโอ")

        video_buttons_layout = QHBoxLayout()
        self.hide_video_button = QPushButton("ซ่อนข้อความในไฟล์วิดีโอ")
        self.hide_video_button.clicked.connect(self.hide_message_in_video)
        self.hide_video_button.setStyleSheet("background-color: purple; color: white;")

        self.extract_video_button = QPushButton("ถอดข้อความจากไฟล์วิดีโอ")
        self.extract_video_button.clicked.connect(self.extract_message_from_video)
        self.extract_video_button.setStyleSheet("background-color: orange; color: white;")

        video_buttons_layout.addWidget(self.hide_video_button)
        video_buttons_layout.addWidget(self.extract_video_button)

        video_layout.addWidget(self.select_video_button)
        video_layout.addWidget(self.video_path_label)
        video_layout.addWidget(self.video_message_input)
        video_layout.addLayout(video_buttons_layout)

        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        self.setLayout(layout)

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

    def hide_message_in_video(self):
        if not self.video_path:
            print("กรุณาเลือกไฟล์วิดีโอก่อน!")
            return

        message = self.video_message_input.text()
        if not message:
            print("กรุณากรอกข้อความที่จะซ่อนในวิดีโอ!")
            return

        try:
            # Open the video file
            video = cv2.VideoCapture(self.video_path)
            if not video.isOpened():
                print("ไม่สามารถเปิดไฟล์วิดีโอได้!")
                return

            # Get video properties
            fps = video.get(cv2.CAP_PROP_FPS)
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            # Check if the message can fit
            total_pixels = width * height * total_frames
            message_bits = len(message) * 8 + 8  # Include delimiter
            if total_pixels < message_bits:
                print("วิดีโอมีขนาดเล็กเกินไปสำหรับซ่อนข้อความนี้!")
                video.release()
                return

            # Prepare output video file
            output_path = os.path.splitext(self.video_path)[0] + "_hidden.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # Convert the message to binary
            binary_message = ''.join(format(ord(c), '08b') for c in message) + '00000000'
            bit_idx = 0

            # Progress dialog
            progress = QProgressDialog("กำลังซ่อนข้อความในวิดีโอ...", "ยกเลิก", 0, total_frames, self)
            progress.setWindowTitle("กำลังประมวลผล")
            progress.setWindowModality(True)
            progress.show()

            # Process frames
            frame_idx = 0
            while True:
                ret, frame = video.read()
                if not ret:
                    break

                if bit_idx < len(binary_message):
                    for i in range(frame.shape[0]):
                        for j in range(frame.shape[1]):
                            if bit_idx < len(binary_message):
                                frame[i, j, 0] = (frame[i, j, 0] & 254) | int(binary_message[bit_idx])
                                bit_idx += 1
                            else:
                                break

                out.write(frame)
                frame_idx += 1
                progress.setValue(frame_idx)

                if progress.wasCanceled():
                    print("การซ่อนข้อความถูกยกเลิก!")
                    break

            # Clean up
            video.release()
            out.release()
            progress.close()

            if frame_idx == total_frames:
                print(f"ซ่อนข้อความสำเร็จ! ไฟล์ถูกบันทึกที่: {output_path}")

        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {str(e)}")

    def extract_message_from_video(self):
        if not self.video_path:
            print("กรุณาเลือกไฟล์วิดีโอก่อน!")
            return

        try:
            video = cv2.VideoCapture(self.video_path)
            if not video.isOpened():
                print("ไม่สามารถเปิดไฟล์วิดีโอได้!")
                return

            binary_message = ""
            delimiter = "00000000"
            frame_idx = 0

            # Progress dialog
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            progress = QProgressDialog("กำลังถอดข้อความจากวิดีโอ...", "ยกเลิก", 0, total_frames, self)
            progress.setWindowTitle("กำลังประมวลผล")
            progress.setWindowModality(True)
            progress.show()

            while True:
                ret, frame = video.read()
                if not ret:
                    break

                for i in range(frame.shape[0]):
                    for j in range(frame.shape[1]):
                        binary_message += str(frame[i, j, 0] & 1)
                        if len(binary_message) >= 8 and binary_message[-8:] == delimiter:
                            video.release()
                            progress.close()
                            extracted_message = ''.join(
                                chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message) - 8, 8)
                            )
                            print(f"ข้อความที่ซ่อนอยู่: {extracted_message}")
                            return

                frame_idx += 1
                progress.setValue(frame_idx)

                if progress.wasCanceled():
                    print("การถอดข้อความถูกยกเลิก!")
                    break

            video.release()
            progress.close()
            print("ไม่พบข้อความที่ซ่อนอยู่ในวิดีโอ หรือข้อมูลอาจเสียหาย")

        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {str(e)}")
