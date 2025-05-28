# นำเข้าไลบรารีที่จำเป็น
import os
import mimetypes
import subprocess
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, 
    QGroupBox, QHBoxLayout, QTextEdit, QComboBox, QMessageBox, QFileDialog,
    QTabWidget, QListWidget, QSplitter
)
from PyQt5.QtCore import Qt
import ffmpeg
from utils.steganography import string_to_binary, binary_to_string2, binary_to_string

class FileInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setAcceptDrops(True)
        self.hidden_data = {}  # เก็บข้อมูลที่ถูกซ่อนไว้
        self.supported_formats = {
            '.mp3': ['-id3v2_version', '3', '-write_id3v1', '1'],
            '.m4a': ['-movflags', '+faststart'],
            '.mp4': ['-movflags', '+faststart'],
            '.ogg': [],  # OGG รองรับ Vorbis comment โดยไม่ต้องตั้งค่าเพิ่มเติม
            '.wav': []   # WAV รองรับ metadata แบบ RIFF
        }

    def initUI(self):
        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)

        # ส่วนด้านบน (ซ่อนข้อมูลและดึงข้อมูล)
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        tabs = QTabWidget()
        hide_tab = QWidget()
        extract_tab = QWidget()

        # Tab ซ่อนข้อมูล
        hide_layout = QVBoxLayout(hide_tab)
        hide_group = QGroupBox()
        hide_group.setTitle("ซ่อนข้อมูล")
        hide_box_layout = QVBoxLayout()

        # ปุ่มเลือกไฟล์และแสดงชื่อไฟล์
        file_selection_layout = QHBoxLayout()
        self.select_file_button = QPushButton("เลือกไฟล์")
        self.select_file_button.clicked.connect(self.select_file_for_info)
        file_selection_layout.addWidget(self.select_file_button)

        self.selected_file_label = QLabel("ยังไม่ได้เลือกไฟล์")
        self.selected_file_label.setWordWrap(True)
        file_selection_layout.addWidget(self.selected_file_label, 1)
        hide_box_layout.addLayout(file_selection_layout)

        # แถว เลือกฟิลด์มาตรฐาน และ ข้อความที่จะซ่อน (แนวนอนในแถวเดียวกัน)
        metadata_secret_layout = QHBoxLayout()
        # ฟิลด์มาตรฐาน
        self.metadata_field = QComboBox()
        standard_fields = ["comment", "title", "artist", "genre", "album", "composer", "copyright", "description"]
        self.metadata_field.addItems(standard_fields)

        metadata_layout = QVBoxLayout()
        metadata_layout.addWidget(QLabel("เลือกฟิลด์มาตรฐาน:"))
        metadata_layout.addWidget(self.metadata_field)
        metadata_secret_layout.addLayout(metadata_layout)

        # ช่องข้อความที่จะซ่อน
        secret_layout = QVBoxLayout()
        secret_layout.addWidget(QLabel("ข้อความที่จะซ่อน:"))
        self.secret_text = QLineEdit()
        secret_layout.addWidget(self.secret_text)
        metadata_secret_layout.addLayout(secret_layout)

        hide_box_layout.addLayout(metadata_secret_layout)

        # ปุ่ม ซ่อนข้อมูล และ เปิดโฟลเดอร์ Output
        hide_row_layout = QHBoxLayout()
        self.hide_button = QPushButton("ซ่อนข้อมูล")
        self.hide_button.clicked.connect(self.hide_metadata)
        self.hide_button.setStyleSheet("background-color: purple; color: white;")
        hide_row_layout.addWidget(self.hide_button)

        self.open_output_folder_button = QPushButton("เปิดโฟลเดอร์ Output")
        self.open_output_folder_button.setStyleSheet("background-color: black; color: white;")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)
        hide_row_layout.addWidget(self.open_output_folder_button)

        hide_box_layout.addLayout(hide_row_layout)

        hide_group.setLayout(hide_box_layout)
        hide_layout.addWidget(hide_group)
        tabs.addTab(hide_tab, "ซ่อนข้อมูล")

        # Tab ดึงข้อมูล
        extract_layout = QVBoxLayout(extract_tab)
        extract_group = QGroupBox("ดึงข้อมูลที่ซ่อนไว้")
        extract_box_layout = QVBoxLayout()

        self.extract_button = QPushButton("ดึงข้อมูลที่ซ่อนไว้ทั้งหมด")
        self.extract_button.clicked.connect(self.extract_hidden_data)
        self.extract_button.setStyleSheet("background-color: green; color: white;")
        extract_box_layout.addWidget(self.extract_button)

        self.hidden_data_list = QListWidget()
        extract_box_layout.addWidget(QLabel("ข้อมูลที่ซ่อนไว้:"))
        extract_box_layout.addWidget(self.hidden_data_list)

        extract_group.setLayout(extract_box_layout)
        extract_layout.addWidget(extract_group)
        tabs.addTab(extract_tab, "ดึงข้อมูลที่ซ่อนไว้")

        top_layout.addWidget(tabs)
        
        
        

        # ส่วนด้านล่าง (รายละเอียดไฟล์ ไม่มีขอบ)
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        self.file_info_text.setMinimumHeight(300)
        bottom_layout.addWidget(self.file_info_text)

        bottom_widget.setLayout(bottom_layout)

        
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 600])  
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)



    def open_output_folder(self):
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
        filters_string = ";;".join(file_filters)
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select a File", "", filters_string)
        if file_path:
            self.selected_file = file_path
            self.selected_file_label.setText(os.path.basename(file_path))
            self.show_file_details(file_path)
            self.hidden_data = {}
            self.hidden_data_list.clear()

    def hide_metadata(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกไฟล์ก่อน")
            return
        secret = self.secret_text.text()
        if not secret:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกข้อความที่ต้องการซ่อน")
            return

        selected_field = self.metadata_field.currentText()
        if not selected_field:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกฟิลด์มาตรฐาน")
            return

        try:
            file_name = os.path.basename(self.selected_file)
            base_name, ext = os.path.splitext(file_name)
            dir_name = os.path.dirname(self.selected_file)

            # สร้างไฟล์ชั่วคราว
            temp_file = os.path.join(dir_name, f"{base_name}_temp{ext}")
            output_file = os.path.join(dir_name, f"{base_name}{ext}")

            encoded_secret = string_to_binary(secret)

            ffmpeg_cmd = ffmpeg.input(self.selected_file)
            args = []
            if ext.lower() in self.supported_formats:
                args = self.supported_formats[ext.lower()]
            ffmpeg_cmd = ffmpeg_cmd.output(
                temp_file,
                metadata=f"{selected_field}={encoded_secret}",
                codec="copy"
            ).global_args(*args).overwrite_output()

            ffmpeg_cmd.run(capture_stdout=True, capture_stderr=True)

            if os.path.exists(output_file):
                os.remove(output_file)
            os.rename(temp_file, output_file)

            self.selected_file = output_file
            self.selected_file_label.setText(os.path.basename(output_file))
            self.show_file_details(output_file)

            QMessageBox.information(
                self,
                "สำเร็จ",
                f"ซ่อนข้อมูลสำเร็จในฟิลด์: {selected_field}\n"
                f"ไฟล์ถูกบันทึกที่: {output_file}\n"
                f"ไฟล์ใหม่ถูกเลือกโดยอัตโนมัติแล้ว"
            )

            self.secret_text.clear()

        except ffmpeg.Error as e:
            stderr = e.stderr.decode('utf-8', errors='ignore')
            QMessageBox.critical(self, "ข้อผิดพลาด", f"FFmpeg error: {stderr}")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
        
        
        
    def extract_hidden_data(self):
        if not hasattr(self, 'selected_file') or not self.selected_file:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกไฟล์ก่อน")
            return
        try:
            self.hidden_data = {}
            self.hidden_data_list.clear()
            media_info = self.get_media_info(self.selected_file)
            if 'tags' in media_info:
                tags = media_info['tags']
                found_hidden = False
                for field, value in tags.items():
                    if isinstance(value, str) and all(c in '01 ' for c in value.strip()):
                        decoded = binary_to_string2(value.strip())
                        if decoded:
                            self.hidden_data[field] = decoded
                            self.hidden_data_list.addItem(f"{field}: {decoded}")
                            found_hidden = True
                if not found_hidden:
                    QMessageBox.information(self, "ผลการค้นหา", "ไม่พบข้อมูลที่ซ่อนไว้ในไฟล์นี้")
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถดึงข้อมูล metadata จากไฟล์นี้ได้")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}")

    def show_file_details(self, file_path):
        try:
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
            if mime_type.startswith(('video/', 'audio/')):
                media_info = self.get_media_info(file_path)
                if 'general' in media_info:
                    general = media_info['general']
                    detailed_info.extend([
                        f"\n📌 General Information",
                        f"━━━━━━━━━━━━━━",
                    ])
                    general_fields = {
                        '⏱️ Duration': f"{float(general.get('duration', 0)):.2f} seconds",
                        '📊 Total Bit Rate': f"{int(general.get('bit_rate', 0)) // 1000} kbps",
                    }
                    for label, value in general_fields.items():
                        detailed_info.append(f"{label}: {value}")
                if 'tags' in media_info:
                    detailed_info.extend([
                        f"\n🔖 Metadata Fields",
                        f"━━━━━━━━━━━━━━",
                    ])
                    tags = media_info['tags']
                    for field, value in tags.items():
                        if value != 'N/A':
                            hidden_text = ""
                            if isinstance(value, str) and all(c in '01 ' for c in value.strip()):
                                decoded = binary_to_string2(value.strip())
                                if decoded:
                                    hidden_text = f" (ข้อมูลซ่อน: {decoded})"
                                else:
                                    hidden_text = f" N/A"
                            detailed_info.append(f"{field}: {hidden_text}")


                if 'video' in media_info and media_info['video']:
                    video = media_info['video']
                    detailed_info.extend([
                        f"\n🎥 Video Information",
                        f"━━━━━━━━━━━━",
                        f"🖼️ Resolution: {video.get('width', 'N/A')}x{video.get('height', 'N/A')}",
                    ])
                    
                    # จัดการ Frame Rate
                    frame_rate = video.get('frame_rate', 'N/A')
                    if frame_rate != 'N/A':
                        try:
                            frame_rate = f"{eval(frame_rate):.2f} fps"
                        except:
                            frame_rate = 'N/A'
                    detailed_info.append(f"🎞️ Frame Rate: {frame_rate}")
                    
                    # จัดการ Video Bit Rate
                    video_bit_rate = video.get('bit_rate', 'N/A')
                    if video_bit_rate != 'N/A' and video_bit_rate.isdigit():
                        video_bit_rate = f"{int(video_bit_rate) // 1000} kbps"
                    else:
                        video_bit_rate = 'N/A'
                    detailed_info.append(f"📊 Video Bit Rate: {video_bit_rate}")
                    
                    detailed_info.extend([
                        f"🎯 Codec: {video.get('codec', 'N/A')}",
                        f"🎨 Pixel Format: {video.get('pixel_format', 'N/A')}",
                    ])

                if 'audio' in media_info and media_info['audio']:
                    audio = media_info['audio']
                    detailed_info.extend([
                        f"\n🔊 Audio Information",
                        f"━━━━━━━━━━",
                    ])
                    
                    # จัดการ Sample Rate
                    sample_rate = audio.get('sample_rate', 'N/A')
                    if sample_rate != 'N/A' and sample_rate.isdigit():
                        sample_rate = f"{int(sample_rate) // 1000} kHz"
                    else:
                        sample_rate = 'N/A'
                    detailed_info.append(f"🎵 Sample Rate: {sample_rate}")
                    
                    detailed_info.extend([
                        f"📢 Channels: {audio.get('channels', 'N/A')} ({audio.get('channel_layout', 'N/A')})",
                    ])
                    
                    # จัดการ Audio Bit Rate
                    audio_bit_rate = audio.get('bit_rate', 'N/A')
                    if audio_bit_rate != 'N/A' and audio_bit_rate.isdigit():
                        audio_bit_rate = f"{int(audio_bit_rate) // 1000} kbps"
                    else:
                        audio_bit_rate = 'N/A'
                    detailed_info.append(f"📊 Audio Bit Rate: {audio_bit_rate}")
                    
                    detailed_info.append(f"🎯 Codec: {audio.get('codec', 'N/A')}")
                    detailed_info.append(f"\n\n")
                    
                    
                    
                    
            self.file_info_text.setText("\n".join(detailed_info))
        except Exception as e:
            self.file_info_text.setText(f"Error occurred: {str(e)}")

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    def get_media_info(self, file_path):
        try:
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
                'audio': {},
                'tags': {}
            }
            if 'format' in data:
                format_data = data['format']
                media_info['general'] = {
                    'duration': format_data.get('duration', 'N/A'),
                    'size': format_data.get('size', 'N/A'),
                    'bit_rate': format_data.get('bit_rate', 'N/A'),
                    'format_name': format_data.get('format_name', 'N/A'),
                }
                if 'tags' in format_data:
                    media_info['tags'] = format_data['tags']
                    media_info['general'].update({
                        'title': format_data['tags'].get('title', 'N/A'),
                        'artist': format_data['tags'].get('artist', 'N/A'),
                        'date': format_data['tags'].get('date', 'N/A'),
                        'comment': format_data['tags'].get('comment', 'N/A'),
                        'genre': format_data['tags'].get('genre', 'N/A'),
                    })
            if 'streams' in data:
                for stream in data['streams']:
                    if 'tags' in stream:
                        media_info['tags'].update(stream['tags'])
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
            return {'general': {}, 'error': f"ไม่สามารถดึงข้อมูลมัลติมีเดียได้: {str(e)}"}

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith((
                '.mp3', '.mp4', '.m4a', '.wav', '.avi', '.mkv', 
                '.flv', '.mov', '.ogg', '.wma', '.aac')):
                self.selected_file = file_path
                self.show_file_details(file_path)
                QMessageBox.information(self, "ไฟล์ที่เลือก", f"เลือกไฟล์ผ่านการลากและวาง: {file_path}")
            else:
                QMessageBox.warning(self, "ข้อผิดพลาด", "ไฟล์ที่ลากเข้ามาไม่ใช่ประเภทที่รองรับ")