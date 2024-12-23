import os
import mimetypes
import subprocess
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, 
    QGroupBox, QHBoxLayout, QTextEdit, QComboBox, QMessageBox, QFileDialog
)
# from PyQt5.QtCore import Qt
import ffmpeg
from utils.steganography import string_to_binary, binary_to_string2,binary_to_string


class FileInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        layout = QVBoxLayout()
        
        # Group for hiding metadata
        hide_group = QGroupBox("ซ่อนข้อมูล")
        hide_layout = QVBoxLayout()
        
        # Row layout for hide button and open folder button
        hide_row_layout = QHBoxLayout()

        # Dropdown to select metadata field
        self.metadata_field = QComboBox()
        self.metadata_field.addItems(["comment", "title", "artist", "genre"])
        hide_layout.addWidget(QLabel("เลือกฟิลด์:"))
        hide_layout.addWidget(self.metadata_field)
        
        # Input for secret message
        self.secret_text = QLineEdit()
        hide_layout.addWidget(QLabel("ข้อความที่จะซ่อน:"))
        hide_layout.addWidget(self.secret_text)

        # Button to hide metadata
        self.hide_button = QPushButton("ซ่อนข้อมูล")
        self.hide_button.clicked.connect(self.hide_metadata)
        self.hide_button.setStyleSheet("background-color: purple; color: white;")
        hide_row_layout.addWidget(self.hide_button)

        # Button to open output folder
        self.open_output_folder_button = QPushButton("เปิดโฟลเดอร์ Output")
        self.open_output_folder_button.setStyleSheet("background-color: black; color: white;")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)
        hide_row_layout.addWidget(self.open_output_folder_button)

        # Add row layout to hide group
        hide_layout.addLayout(hide_row_layout)
        hide_group.setLayout(hide_layout)
        layout.addWidget(hide_group)
        
        # Group for file information
        info_group = QGroupBox("รายละเอียดไฟล์")
        info_layout = QVBoxLayout()
        
        self.select_file_button = QPushButton("เลือกไฟล์")
        self.select_file_button.clicked.connect(self.select_file_for_info)
        
        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        self.file_info_text.setMinimumHeight(300)
        
        info_layout.addWidget(self.select_file_button)
        info_layout.addWidget(self.file_info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        self.setLayout(layout)

    def open_output_folder(self):
        """เปิดโฟลเดอร์ที่ไฟล์ที่เลือกมาอยู่"""
        if hasattr(self, 'selected_file') and self.selected_file:
            file_directory = os.path.dirname(self.selected_file)
            if os.path.exists(file_directory):
                os.startfile(file_directory)  # สำหรับ Windows
            else:
                QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบโฟลเดอร์ของไฟล์ที่เลือก")
        else:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกไฟล์ก่อน")


    def select_file_for_info(self):
        file_filters = [
            "Media Files (*.mp3 *.mp4 *.m4a *.wav *.avi *.mkv *.flv *.mov *.ogg *.wma *.aac)",
            "Audio Files (*.mp3 *.wav *.m4a *.ogg *.wma *.aac)",
            "Video Files (*.mp4 *.avi *.mkv *.flv *.mov)",
            "All Files (*.*)"
        ]
        
        # รวมตัวกรองเป็นสตริงเดียวโดยใช้ ';;' เป็นตัวคั่น
        filters_string = ";;".join(file_filters)
        
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select a File", "", filters_string)
        if file_path:
            self.selected_file = file_path
            self.show_file_details(file_path)
    
    def hide_metadata(self):
        """ซ่อนข้อมูลในฟิลด์ที่เลือก"""
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกไฟล์ก่อน")
            return

        secret = self.secret_text.text()
        if not secret:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกข้อความที่ต้องการซ่อน")
            return

        try:
            file_name = os.path.basename(self.selected_file)
            base_name, ext = os.path.splitext(file_name)
            output_file = os.path.join(os.path.dirname(self.selected_file), f"{base_name}{ext}")

            # แปลงข้อความเป็น Base64
            encoded_secret = string_to_binary(secret)

            # เพิ่ม metadata ด้วย ffmpeg
            selected_field = self.metadata_field.currentText()
            ffmpeg.input(self.selected_file).output(
                output_file,
                metadata=f"{selected_field}={encoded_secret}",
                codec="copy"
            ).overwrite_output().run(capture_stdout=True, capture_stderr=True)

            QMessageBox.information(self, "สำเร็จ", f"ซ่อนข้อมูลสำเร็จ\nไฟล์ถูกบันทึกที่: {output_file}")

            # อัพเดทการแสดงผลข้อมูลไฟล์
            self.show_file_details(output_file)

        except ffmpeg.Error as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"FFmpeg error: {e.stderr.decode('utf-8', errors='ignore')}")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def show_file_details(self, file_path):
        try:
            # ข้อมูลพื้นฐานของไฟล์
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            size_text = self.format_size(file_size)
            mime_type = mimetypes.guess_type(file_path)[0] or "unknown"
            
            detailed_info = [
                f"📝 File Details",
                f"━━━━━━━━━━━━━━━━━━━━━━━",
                f"📋 File Name: {file_name}",
                f"📊 Size: {size_text}",
                f"🏷️ Type: {mime_type}",
            ]

            # ถ้าเป็นไฟล์มัลติมีเดีย
            if mime_type.startswith(('video/', 'audio/')):
                media_info = self.get_media_info(file_path)
                
                # ข้อมูลทั่วไป
                general = media_info['general']
                metadata_fields = {
                    'title': general.get('title', 'N/A'),
                    'artist': general.get('artist', 'N/A'),
                    'date': general.get('date', 'N/A'),
                    'comment': general.get('comment', 'N/A'),
                    'genre': general.get('genre', 'N/A')
                }
                
                detailed_info.extend([
                    f"\n📌 General Information",
                    f"━━━━━━━━━━━━━━",
                ])
                
                # ตรวจสอบและแปลง binary data ในแต่ละฟิลด์
                for field, value in metadata_fields.items():
                    if value != 'N/A':
                        # ตรวจสอบว่าเป็น binary string หรือไม่
                        if all(c in '01 ' for c in value):
                            decoded = binary_to_string2(value)
                            if decoded:
                                value = f"{decoded} (Hidden data)"
                    detailed_info.append(f"{field.capitalize()}: {value}")
                
                detailed_info.extend([
                    f"⏱️ Duration: {float(general.get('duration', 0)):.2f} seconds",
                    f"📊 Total Bit Rate: {int(general.get('bit_rate', 0)) // 1000} kbps",
                ])
                
                # ข้อมูลวิดีโอ (ถ้ามี)
                if media_info['video']:
                    video = media_info['video']
                    detailed_info.extend([
                        f"\n🎥 Video Information",
                        f"━━━━━━━━━━━━",
                        f"🖼️ Resolution: {video.get('width')}x{video.get('height')}",
                        f"🎞️ Frame Rate: {eval(video.get('frame_rate', '0/1')):.2f} fps",
                        f"📊 Video Bit Rate: {int(video.get('bit_rate', 0)) // 1000} kbps",
                        f"🎯 Codec: {video.get('codec')}",
                        f"🎨 Pixel Format: {video.get('pixel_format')}",
                    ])
                
                # ข้อมูลเสียง
                if media_info['audio']:
                    audio = media_info['audio']
                    detailed_info.extend([
                        f"\n🔊 Audio Information",
                        f"━━━━━━━━━━",
                        f"🎵 Sample Rate: {int(audio.get('sample_rate', 0)) // 1000} kHz",
                        f"📢 Channels: {audio.get('channels')} ({audio.get('channel_layout')})",
                        f"📊 Audio Bit Rate: {int(audio.get('bit_rate', 0)) // 1000} kbps",
                        f"🎯 Codec: {audio.get('codec')}",
                    ])
            
            # แสดงข้อมูลใน QTextEdit
            self.file_info_text.setText("\n".join(detailed_info))
            
        except Exception as e:
            self.file_info_text.setText(f"Error occurred: {str(e)}")

    def format_size(self, size):
        # แปลงขนาดไฟล์เป็นหน่วยที่เหมาะสม
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
             
    def get_media_info(self, file_path):
        """ดึงข้อมูลละเอียดของไฟล์มัลติมีเดีย"""
        try:
            # ใช้ ffprobe เพื่อดึงข้อมูลละเอียด
            command = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            media_info = {
                'general': {},
                'video': {},
                'audio': {}
            }
            
            # ข้อมูลทั่วไป
            if 'format' in data:
                format_data = data['format']
                media_info['general'] = {
                    'duration': format_data.get('duration', 'N/A'),
                    'size': format_data.get('size', 'N/A'),
                    'bit_rate': format_data.get('bit_rate', 'N/A'),
                    'format_name': format_data.get('format_name', 'N/A'),
                }
                
                # ดึงข้อมูล metadata ถ้ามี
                if 'tags' in format_data:
                    tags = format_data['tags']
                    media_info['general'].update({
                        'title': tags.get('title', 'N/A'),
                        'artist': tags.get('artist', 'N/A'),
                        'date': tags.get('date', 'N/A'),
                        'comment': tags.get('comment', 'N/A'),
                        'genre': tags.get('genre', 'N/A'),
                    })
            
            # ข้อมูล streams
            if 'streams' in data:
                for stream in data['streams']:
                    if stream['codec_type'] == 'video':
                        media_info['video'] = {
                            'codec': stream.get('codec_name', 'N/A'),
                            'width': stream.get('width', 'N/A'),
                            'height': stream.get('height', 'N/A'),
                            'frame_rate': stream.get('r_frame_rate', 'N/A'),
                            'bit_rate': stream.get('bit_rate', 'N/A'),
                            'total_frames': stream.get('nb_frames', 'N/A'),
                            'pixel_format': stream.get('pix_fmt', 'N/A'),
                        }
                    elif stream['codec_type'] == 'audio':
                        media_info['audio'] = {
                            'codec': stream.get('codec_name', 'N/A'),
                            'sample_rate': stream.get('sample_rate', 'N/A'),
                            'channels': stream.get('channels', 'N/A'),
                            'bit_rate': stream.get('bit_rate', 'N/A'),
                            'channel_layout': stream.get('channel_layout', 'N/A'),
                        }
            
            return media_info
        except Exception as e:
            return f"ไม่สามารถดึงข้อมูลมัลติมีเดียได้: {str(e)}"




