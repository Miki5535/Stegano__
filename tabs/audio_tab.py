import os
import wave
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QHBoxLayout,  
                             QGroupBox, QComboBox, QTextEdit,QLineEdit)
import soundfile as sf
import sounddevice as sd
from pydub import AudioSegment
import utils.steganography as steganography
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices


class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_example_audio()
        self.setAcceptDrops(True)



    def initUI(self):
        layout = QVBoxLayout()

        # Audio file selection group
        audio_group = QGroupBox("จัดการไฟล์เสียง")
        audio_layout = QVBoxLayout()

        # Row layout for file selection and folder opening
        audio_row_layout = QHBoxLayout()

        self.select_audio_button = QPushButton("เลือกไฟล์เสียง")
        self.select_audio_button.clicked.connect(self.select_audio)

        self.load_example_button = QPushButton("โหลดเสียงตัวอย่าง")
        self.load_example_button.clicked.connect(self.load_example_audio)
        self.load_example_button.setStyleSheet("background-color: blue; color: white;")

        self.example_audio_dropdown = QComboBox()
        self.example_audio_dropdown.setPlaceholderText("เลือกไฟล์เสียงตัวอย่าง")
        self.example_audio_dropdown.currentIndexChanged.connect(self.select_example_audio)

        self.open_output_folder_button = QPushButton("เปิดโฟลเดอร์ Output")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)
        self.open_output_folder_button.setStyleSheet("background-color: back; color: white;")

        # Add buttons and dropdown to the row layout
        audio_row_layout.addWidget(self.example_audio_dropdown)
        audio_row_layout.addWidget(self.select_audio_button)
        audio_row_layout.addWidget(self.load_example_button)
        audio_row_layout.addWidget(self.open_output_folder_button)

        # Add row layout to the audio layout
        audio_layout.addLayout(audio_row_layout)
        
        

        # Preview selected file with increased width
        self.audio_path_label = QLabel("ไม่ได้เลือกไฟล์")
        self.audio_path_label.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        self.audio_path_label.setMinimumHeight(30)
        self.audio_path_label.setMinimumWidth(400)  
        audio_layout.addWidget(self.audio_path_label)
        
        self.audio_message_input = QTextEdit()  # ใช้ QTextEdit แทน QLineEdit
        self.audio_message_input.setPlaceholderText("ข้อความที่ต้องการซ่อนในไฟล์เสียง")
        self.audio_message_input.setMinimumHeight(100)  # กำหนดความสูงเพิ่มขึ้น
        self.audio_message_input.setMinimumWidth(400)  # กำหนดความกว้าง
        self.audio_message_input.setStyleSheet("font-size: 14px; padding: 5px;")  # ปรับขนาดตัวอักษรและเพิ่ม padding


        
        audio_layout.addWidget(self.audio_message_input)

        # Add buttons for hiding, extracting, playing, and stopping audio
        audio_buttons_layout = QHBoxLayout()

        self.hide_audio_button = QPushButton("ซ่อนข้อความในไฟล์เสียง")
        self.hide_audio_button.clicked.connect(self.hide_message_in_audio)
        self.hide_audio_button.setStyleSheet("background-color: purple; color: white;")

        self.extract_audio_button = QPushButton("ถอดข้อความจากไฟล์เสียง")
        self.extract_audio_button.clicked.connect(self.extract_message_from_audio)
        self.extract_audio_button.setStyleSheet("background-color: orange; color: white;")

        self.play_audio_button = QPushButton("เล่น")
        self.play_audio_button.clicked.connect(self.reset_audio)
        self.play_audio_button.setStyleSheet("background-color: green; color: white;")

        self.stop_audio_button = QPushButton("หยุด")
        self.stop_audio_button.clicked.connect(self.stop_audio)
        self.stop_audio_button.setStyleSheet("background-color: red; color: white;")

        # Add buttons to the layout
        audio_buttons_layout.addWidget(self.hide_audio_button)
        audio_buttons_layout.addWidget(self.extract_audio_button)
        audio_buttons_layout.addWidget(self.play_audio_button)
        audio_buttons_layout.addWidget(self.stop_audio_button)

        # Add button layout to the audio layout
        audio_layout.addLayout(audio_buttons_layout)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        


        # Result output area
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        layout.addWidget(self.result_output)

        self.setLayout(layout)


    def load_example_audio(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "audioexample")

        if os.path.exists(example_folder_path):
            audio_files = [f for f in os.listdir(example_folder_path) if f.endswith(('.wav', '.mp3', '.flac'))]
            self.example_audio_dropdown.clear()
            self.example_audio_dropdown.addItem("เลือกไฟล์เสียงตัวอย่าง")
            self.example_audio_dropdown.addItems(audio_files)
            self.result_output.append("<font color='blue'>โหลดไฟล์เสียงตัวอย่างสำเร็จ</font>")
        else:
            self.result_output.append("<font color='red'>ไม่พบโฟลเดอร์เสียงตัวอย่าง</font>")

    def select_example_audio(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "audioexample")

        selected_audio = self.example_audio_dropdown.currentText()
        if selected_audio != "เลือกไฟล์เสียงตัวอย่าง":
            selected_audio_path = os.path.join(example_folder_path, selected_audio)
            self.audio_path_label.setText(selected_audio_path)
            self.result_output.append(f"เลือกเสียงตัวอย่าง: <font color='blue'>{selected_audio_path}</font>")

    def stop_audio(self):
        try:
            sd.stop()
            self.result_output.append("หยุดการเล่นไฟล์เสียง.")
        except Exception as e:
            self.result_output.append(f"เกิดข้อผิดพลาดในการหยุดเสียง: {e}")

    def reset_audio(self):
        try:
            audio_file = self.audio_path_label.text()
            if audio_file != "ไม่ได้เลือกไฟล์":
                data, samplerate = sf.read(audio_file)
                sd.stop()
                sd.play(data, samplerate)
                self.result_output.append("เล่นไฟล์เสียงใหม่.")
            else:
                self.result_output.append("กรุณาเลือกไฟล์เสียงก่อนที่จะเล่น.")
        except Exception as e:
            self.result_output.append(f"เกิดข้อผิดพลาด: {e}")

    def select_audio(self):
        options = QFileDialog.Options()
        audio_file, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์เสียง", "", "Audio Files (*.wav *.mp3 *.flac);;All Files (*)", options=options)
        if audio_file:
            self.audio_path_label.setText(audio_file)
            self.result_output.append(f"เลือกไฟล์เสียง: {audio_file}")
        else:
            self.audio_path_label.setText("ไม่ได้เลือกไฟล์")

    def hide_message_in_audio(self):
        message = self.audio_message_input.toPlainText()
        audio_path = self.audio_path_label.text()
        if audio_path == "ไม่ได้เลือกไฟล์":
            self.result_output.append("กรุณาเลือกไฟล์เสียงก่อน!")
            return
        try:
            file_extension = os.path.splitext(audio_path)[1].lower()
            temp_wav_path = None
            if file_extension != ".wav":
                audio = AudioSegment.from_file(audio_path)
                temp_wav_path = os.path.splitext(audio_path)[0] + ".wav"
                audio.export(temp_wav_path, format="wav")
                audio_path = temp_wav_path

            with wave.open(audio_path, 'rb') as audio_file:
                n_channels = audio_file.getnchannels()
                sampwidth = audio_file.getsampwidth()
                framerate = audio_file.getframerate()
                n_frames = audio_file.getnframes()
                frames = audio_file.readframes(n_frames)
                audio_data = np.frombuffer(frames, dtype=np.uint8)

            # แปลงข้อความเป็นไบนารีและเพิ่มตัวจบข้อความ
            binary_message = steganography.string_to_binary(message) + '00000000'

            # คำนวณขนาดข้อความสูงสุดที่สามารถซ่อนในไฟล์เสียง
            max_message_length = len(audio_data) // 8  # 1 ตัวอักษรใช้ 8 บิต
            self.result_output.append(f"ขนาดข้อความสูงสุดที่สามารถใส่ได้: {max_message_length} ตัวอักษร")

            # ตรวจสอบว่าข้อความยาวเกินไปหรือไม่
            if len(binary_message) > len(audio_data):
                raise ValueError(f"ข้อความยาวเกินไป! (สูงสุด: {max_message_length} ตัวอักษร)")

            # ฝังข้อมูลลงในไฟล์เสียง
            modified_data = audio_data.copy()
            for i in range(len(binary_message)):
                modified_data[i] = (modified_data[i] & 254) | int(binary_message[i])

            # สร้างโฟลเดอร์ output ถ้ายังไม่มี
            current_directory = os.path.dirname(os.path.realpath(__file__))
            parent_directory = os.path.dirname(current_directory)  
            directory = os.path.join(parent_directory, "audioexample", "output")
            if not os.path.exists(directory):
                os.makedirs(directory)

            # ตั้งชื่อไฟล์เอาต์พุต
            filename = os.path.splitext(os.path.basename(audio_path))[0]
            output_path = os.path.join(directory, f"{filename}_hidden.wav")

            # บันทึกไฟล์เสียงที่ถูกแก้ไข
            with wave.open(output_path, 'wb') as output_file:
                output_file.setnchannels(n_channels)
                output_file.setsampwidth(sampwidth)
                output_file.setframerate(framerate)
                output_file.writeframes(modified_data.tobytes())

            # ลบไฟล์ชั่วคราวถ้ามี
            if temp_wav_path:
                os.remove(temp_wav_path)

            self.result_output.append(f"ข้อความถูกซ่อนใน : <font color='blue'>{output_path}</font>")

        except Exception as e:
            self.result_output.append(f"เกิดข้อผิดพลาดในการซ่อนข้อความ: {e}")

    def extract_message_from_audio(self):
        audio_path = self.audio_path_label.text()
        if audio_path == "ไม่ได้เลือกไฟล์":
            self.result_output.append("กรุณาเลือกไฟล์เสียงก่อน!")
            return
        try:
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.uint8)

            binary_message = ''
            for byte in audio_data:
                binary_message += str(byte & 1)
                if len(binary_message) >= 8 and binary_message[-8:] == '00000000':
                    break

            message = steganography.binary_to_string(binary_message)
            self.result_output.append(f"ข้อความที่ถูกถอดออกมา : <font color='green'>{message}</font>")

        except Exception as e:
            self.result_output.append(f"เกิดข้อผิดพลาดในการถอดข้อความ: {e}")

    def open_output_folder(self):


        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        output_path = os.path.join(parent_directory, "audioexample", "output")

        # สร้างโฟลเดอร์หากยังไม่มี
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # เปิดโฟลเดอร์
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    def dragEnterEvent(self, event):
            # ตรวจสอบว่าไฟล์ที่ลากเข้ามาเป็นประเภทที่รองรับ
            if event.mimeData().hasUrls():
                event.accept()
            else:
                event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(('.wav', '.mp3', '.flac')):
                self.audio_path_label.setText(file_path)
                self.result_output.append(f"<font color='blue'>เลือกไฟล์เสียงผ่านการลากและวาง: {file_path}</font>")
            else:
                self.result_output.append("<font color='red'>ไฟล์ที่ลากเข้ามาไม่ใช่ไฟล์เสียงที่รองรับ!</font>")



