import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QPushButton, 
                            QLabel, QLineEdit, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from database import PasswordDatabase

class PasswordManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = PasswordDatabase()
        self.init_ui()
        self.load_passwords()
        
    def init_ui(self):
        self.setWindowTitle('如席密码管理器（RuxiPass） - V0.5')
        self.setGeometry(300, 300, 800, 500)
        
        # 设置应用样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                gridline-color: #e1e4e8;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e1e4e8;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #2196f3;
            }
            QHeaderView::section {
                background-color: #ffffff;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e1e4e8;
                font-weight: bold;
                color: #24292e;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #2196f3;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                background-color: #2196f3;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
            QPushButton[text="删除"] {
                background-color: #f44336;
            }
            QPushButton[text="删除"]:hover {
                background-color: #d32f2f;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧布局
        left_layout = QVBoxLayout()
        
        # 修改右侧布局
        right_layout = QVBoxLayout()
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(1)  # 只显示一列
        self.detail_table.setRowCount(2)
        self.detail_table.setVerticalHeaderLabels(['用户名', '密码'])
        self.detail_table.horizontalHeader().hide()  # 隐藏水平表头
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        right_layout.addWidget(self.detail_table)
        
        # 修改表格设置，添加双击编辑功能
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['分组', '名称'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.show_password_details)
        self.table.cellDoubleClicked.connect(self.edit_password)  # 添加双击事件
        
        left_layout.addWidget(self.table)
        
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        
        # 底部输入区域
        input_layout = QHBoxLayout()
        
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText('分组')
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('名称')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('用户名')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        
        add_button = QPushButton('添加')
        add_button.clicked.connect(self.add_password)
        delete_button = QPushButton('删除')
        delete_button.clicked.connect(self.delete_password)
        
        input_layout.addWidget(self.group_input)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(self.password_input)
        input_layout.addWidget(add_button)
        input_layout.addWidget(delete_button)
        
        left_layout.addLayout(input_layout)
    
    def load_passwords(self):
        passwords = self.db.get_all_passwords()
        self.table.setRowCount(len(passwords))
        
        for row, (id, name, username, password, group_name) in enumerate(passwords):
            group_item = QTableWidgetItem(group_name)
            group_item.setData(Qt.UserRole, id)
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, id)
            
            self.table.setItem(row, 0, group_item)
            self.table.setItem(row, 1, name_item)
    
    def show_password_details(self, row, column):
        item = self.table.item(row, 0)
        if item:
            password_id = item.data(Qt.UserRole)
            password_data = self.db.get_password_by_id(password_id)
            if password_data:
                # 只设置一列的值
                self.detail_table.setItem(0, 0, QTableWidgetItem(password_data[2]))
                self.detail_table.setItem(1, 0, QTableWidgetItem('*' * len(password_data[3])))
    
    def edit_password(self, row, column):
        item = self.table.item(row, 0)
        if item:
            password_id = item.data(Qt.UserRole)
            password_data = self.db.get_password_by_id(password_id)
            if password_data:
                self.group_input.setText(password_data[4])
                self.name_input.setText(password_data[1])
                self.username_input.setText(password_data[2])
                self.password_input.setText(password_data[3])
                self.editing_id = password_id
    
    def add_password(self):
        name = self.name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        group_name = self.group_input.text() or '未分组'
        
        if not name or not username or not password:
            QMessageBox.warning(self, '警告', '所有字段都必须填写！')
            return
        
        # 检查同分组下是否存在相同名称
        if hasattr(self, 'editing_id'):
            if self.db.check_name_exists(name, group_name, self.editing_id):
                QMessageBox.warning(self, '警告', f'分组"{group_name}"下已存在名称为"{name}"的记录！')
                return
            self.db.update_password(self.editing_id, name, username, password, group_name)
            delattr(self, 'editing_id')
        else:
            if self.db.check_name_exists(name, group_name):
                QMessageBox.warning(self, '警告', f'分组"{group_name}"下已存在名称为"{name}"的记录！')
                return
            self.db.add_password(name, username, password, group_name)
        
        self.load_passwords()
        
        # 清空输入框
        self.group_input.clear()
        self.name_input.clear()
        self.username_input.clear()
        self.password_input.clear()
    
    def delete_password(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '警告', '请先选择要删除的项！')
            return
        
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        if item:
            password_id = item.data(Qt.UserRole)
            self.db.delete_password(password_id)
            self.load_passwords()