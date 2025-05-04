from PyQt5.QtWidgets import (
    QGroupBox, QComboBox, QWidget, QPushButton, QTextEdit, QVBoxLayout,
    QMessageBox, QFileDialog, QHBoxLayout, QFrame, QListWidget, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QRadioButton
)
from PyQt5.QtCore import Qt
import os

class SteganoWorkflowItem:
    def __init__(self, mode, file_type, encryption_method=None, hide_text_files=None):
        self.mode = mode
        self.file_type = file_type
        self.encryption_method = encryption_method
        self.hide_text_files = hide_text_files  # This will store a list of text files
        self.source_files = []
        self.data_to_hide = None
        self.output_path = ""

class IntegrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.workflow_items = []
        self.output_path = ""
        self.initUI()




    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Horizontal Layout for Split View
        split_layout = QHBoxLayout()

        # Input Files Section (Left Side)
        input_group = QGroupBox("ไฟล์ที่ต้องใส่")
        input_layout = QVBoxLayout()

        file_controls = QHBoxLayout()
        self.file_btn = QPushButton("เลือกไฟล์")
        self.file_btn.clicked.connect(self.select_files)
        self.clear_files_btn = QPushButton("ล้างรายการไฟล์")
        self.clear_files_btn.clicked.connect(self.clear_files)

        file_controls.addWidget(self.file_btn)
        file_controls.addWidget(self.clear_files_btn)

        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["ชื่อไฟล์", "ประเภท", "ขนาด"])
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)

        input_layout.addLayout(file_controls)
        input_layout.addWidget(self.files_table)
        input_group.setLayout(input_layout)

        # Workflow Configuration Section (Right Side)
        workflow_group = QGroupBox("ลำดับการทำงาน")
        workflow_layout = QVBoxLayout()

        step_controls = QHBoxLayout()

        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["ซ่อนข้อมูล", "ถอดข้อมูล"])

        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["ภาพ", "เสียง", "วิดีโอ", "Metatag", "ข้อความ"])

        # Encryption Options
        self.encryption_checkbox = QRadioButton("ใช้การเข้ารหัสก่อนซ่อนข้อมูล")

        add_step_btn = QPushButton("เพิ่มขั้นตอน")
        add_step_btn.clicked.connect(self.add_workflow_step)

        step_controls.addWidget(QLabel("โหมด:"))
        step_controls.addWidget(self.mode_dropdown)
        step_controls.addWidget(QLabel("ประเภท:"))
        step_controls.addWidget(self.type_dropdown)
        step_controls.addWidget(self.encryption_checkbox)
        step_controls.addWidget(add_step_btn)

        # Workflow list
        self.workflow_list = QListWidget()
        self.workflow_list.setDragDropMode(QListWidget.DragDrop)
        self.workflow_list.setDefaultDropAction(Qt.MoveAction)

        workflow_buttons = QHBoxLayout()
        remove_step_btn = QPushButton("ลบขั้นตอนที่เลือก")
        remove_step_btn.clicked.connect(self.remove_workflow_step)
        clear_workflow_btn = QPushButton("ล้างทั้งหมด")
        clear_workflow_btn.clicked.connect(self.clear_workflow)

        workflow_buttons.addWidget(remove_step_btn)
        workflow_buttons.addWidget(clear_workflow_btn)

        workflow_layout.addLayout(step_controls)
        workflow_layout.addWidget(self.workflow_list)
        workflow_layout.addLayout(workflow_buttons)
        workflow_group.setLayout(workflow_layout)

        # Add to Split Layout
        split_layout.addWidget(input_group)
        split_layout.addWidget(workflow_group)

        # Results Section
        result_group = QGroupBox("ผลลัพธ์")
        result_layout = QVBoxLayout()

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("ผลลัพธ์จะแสดงที่นี่")

        # Execute button with progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        execute_layout = QHBoxLayout()
        self.execute_btn = QPushButton("เริ่มทำงาน")
        self.execute_btn.clicked.connect(self.execute_workflow)

        self.clear_results_btn = QPushButton("ล้างผลลัพธ์")
        self.clear_results_btn.clicked.connect(lambda: self.result_display.clear())

        execute_layout.addWidget(self.execute_btn)
        execute_layout.addWidget(self.clear_results_btn)

        result_layout.addWidget(self.result_display)
        result_layout.addWidget(self.progress_bar)
        result_layout.addLayout(execute_layout)
        result_group.setLayout(result_layout)

        # Add Split Layout and Result Section to Main Layout
        main_layout.addLayout(split_layout)
        main_layout.addWidget(result_group)






















    def select_files(self):
        file_types = "All Supported Files (*.png *.jpg *.wav *.mp3 *.mp4 *.avi);;Images (*.png *.jpg);;Audio (*.wav *.mp3);;Video (*.mp4 *.avi);;All Files (*.*)"
        files, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์", "", file_types)
        if files:
            self.selected_files.extend(files)
            self.update_files_table()

    def update_files_table(self):
        self.files_table.setRowCount(len(self.selected_files))
        for row, file_path in enumerate(self.selected_files):
            file_name = os.path.basename(file_path)
            self.files_table.setItem(row, 0, QTableWidgetItem(file_name))
            
            file_ext = os.path.splitext(file_path)[1].lower()
            file_type = "ไม่ระบุ"
            if file_ext in ['.png', '.jpg', '.jpeg']:
                file_type = "ภาพ"
            elif file_ext in ['.wav', '.mp3']:
                file_type = "เสียง"
            elif file_ext in ['.mp4', '.avi']:
                file_type = "วิดีโอ"
            self.files_table.setItem(row, 1, QTableWidgetItem(file_type))
            
            size = os.path.getsize(file_path)
            size_str = self.format_size(size)
            self.files_table.setItem(row, 2, QTableWidgetItem(size_str))

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def clear_files(self):
        self.selected_files.clear()
        self.files_table.setRowCount(0)

    def select_output_path(self):
        folder = QFileDialog.getExistingDirectory(self, "เลือกตำแหน่งบันทึกไฟล์ผลลัพธ์")
        if folder:
            self.output_path = folder
            self.output_path_display.setText(folder)

    def add_workflow_step(self):
        mode = self.mode_dropdown.currentText()
        file_type = self.type_dropdown.currentText()
        encryption_method = self.encryption_checkbox.isChecked()
        hide_text_files = []

        if mode == "ซ่อนข้อมูล" and file_type == "ข้อความ":
            text_files, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์ข้อความ", "", "Text Files (*.txt)")
            if text_files:
                hide_text_files.extend(text_files)
        
        step_text = f"{mode} - {file_type}"
        self.workflow_list.addItem(step_text)
        self.workflow_items.append(SteganoWorkflowItem(mode, file_type, encryption_method, hide_text_files))

    def remove_workflow_step(self):
        current_row = self.workflow_list.currentRow()
        if current_row >= 0:
            self.workflow_list.takeItem(current_row)
            self.workflow_items.pop(current_row)

    def clear_workflow(self):
        self.workflow_list.clear()
        self.workflow_items.clear()

    def execute_workflow(self):
        if not self.workflow_items:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเพิ่มขั้นตอนการทำงานก่อน")
            return
        if not self.selected_files:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์ที่ต้องการใช้")
            return
        if not self.output_path:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกตำแหน่งบันทึกผลลัพธ์")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Simulate processing
        for i in range(1, 101):
            self.progress_bar.setValue(i)

        self.result_display.append("ขั้นตอนเสร็จสมบูรณ์!")
        self.progress_bar.setVisible(False)
