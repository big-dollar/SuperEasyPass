from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QPushButton, 
                            QLabel, QLineEdit, QHeaderView, QMessageBox,
                            QComboBox, QDialog, QInputDialog, QListWidget, QTextEdit,
                            QFileDialog, QMenu, QAction)
from PyQt5.QtCore import Qt, QPoint
from database import PasswordDatabase
import random
import string
import json

class AutoSaveTextEdit(QTextEdit):
    def __init__(self, save_callback):
        super().__init__()
        self.save_callback = save_callback
        
    def focusOutEvent(self, event):
        self.save_callback()
        super().focusOutEvent(event)

class GroupManageDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("分组管理")
        self.setFixedSize(300, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加分组")
        add_btn.setStyleSheet("""
            QPushButton { background-color: #2ea44f; color: white; border-radius: 4px; padding: 6px; }
            QPushButton:hover { background-color: #2c974b; }
        """)
        add_btn.clicked.connect(self.add_group)
        
        del_btn = QPushButton("删除分组")
        del_btn.setStyleSheet("""
            QPushButton { background-color: #d73a49; color: white; border-radius: 4px; padding: 6px; }
            QPushButton:hover { background-color: #cb2431; }
        """)
        del_btn.clicked.connect(self.delete_group)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
        self.load_groups()
        
    def load_groups(self):
        self.list_widget.clear()
        groups = self.db.get_all_groups()
        self.list_widget.addItems(groups)
        
    def add_group(self):
        name, ok = QInputDialog.getText(self, "添加分组", "请输入新分组名称:")
        if ok and name:
            if self.db.add_group(name):
                self.load_groups()
            else:
                QMessageBox.warning(self, "错误", "该分组已存在！")
                
    def delete_group(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择要删除的分组")
            return
            
        name = item.text()
        if name == "未分组":
            QMessageBox.warning(self, "错误", "默认分组不能删除！")
            return
            
        success, msg = self.db.delete_group(name)
        if success:
            self.load_groups()
        else:
            QMessageBox.warning(self, "无法删除", msg)

class PasswordManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = PasswordDatabase()
        self.current_viewing_id = None
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        self.setWindowTitle('超容易密码管理器 (SuperEasyPass) - V1.0')
        self.setGeometry(300, 300, 800, 500)
        
        # 设置应用样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafbfc;
            }
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 16px; 
                color: #24292e;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                gridline-color: transparent;
                outline: none;
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #eaecef;
            }
            QTableWidget::item:selected {
                background-color: #f1f8ff;
                color: #0366d6;
            }
            QHeaderView::section {
                background-color: #f6f8fa;
                padding: 14px 12px;
                border: none;
                border-bottom: 2px solid #e1e4e8;
                font-weight: 600;
                font-size: 16px;
                color: #24292e;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 12px 14px;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: #ffffff;
                selection-background-color: #0366d6;
                font-size: 16px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #0366d6;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 12px 24px;
                border-radius: 6px;
                border: 1px solid rgba(27,31,35,0.15);
                background-color: #2ea44f;
                color: white;
                font-weight: 600;
                font-size: 15px; 
            }
            QPushButton:hover {
                background-color: #2c974b;
            }
            QPushButton:pressed {
                background-color: #2a8f47;
            }
            QPushButton[text="删除"] {
                background-color: #d73a49;
                border: 1px solid rgba(27,31,35,0.15);
            }
            QPushButton[text="删除"]:hover {
                background-color: #cb2431;
            }
            /* 细微调整"管理"按钮样式 */
            QPushButton#manageBtn {
                background-color: #f6f8fa;
                color: #24292e;
                border: 1px solid #e1e4e8;
                padding: 0px;
                font-size: 22px; 
            }
            QPushButton#manageBtn:hover {
                background-color: #f3f4f6;
            }
            /* 作者信息标签样式 */
            QLabel#authorLabel {
                color: #586069;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局改为垂直布局，以便底部输入框横跨整个界面
        main_layout = QVBoxLayout(central_widget)
        
        # 内容区域布局（水平分割：左侧列表 + 右侧预览）
        content_layout = QHBoxLayout()
        
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
        self.detail_table.setFixedHeight(140) # 稍微增加高度适应大字体
        
        # 增加行高
        self.detail_table.verticalHeader().setDefaultSectionSize(50)
        
        right_layout.addWidget(self.detail_table)
        
        # 备注区域
        right_layout.addWidget(QLabel("📝 备注 (点击外部自动保存):"))
        self.note_edit = AutoSaveTextEdit(self.save_current_note)
        self.note_edit.setPlaceholderText("在此输入备注信息...")
        right_layout.addWidget(self.note_edit)
        
        # 修改表格设置，添加双击编辑功能
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['分组', '名称'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.show_password_details)
        self.table.cellDoubleClicked.connect(self.edit_password)  # 添加双击事件
        
        # 搜索区域
        search_layout = QHBoxLayout()
        
        self.search_group_input = QLineEdit()
        self.search_group_input.setPlaceholderText('🔍 搜索分组...')
        self.search_group_input.textChanged.connect(self.search_passwords)
        
        self.search_name_input = QLineEdit()
        self.search_name_input.setPlaceholderText('🔍 搜索名称...')
        self.search_name_input.textChanged.connect(self.search_passwords)
        
        # 更多选项按钮（导出/导入）
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedWidth(40)
        self.menu_btn.setToolTip("更多选项 (导入/导出)")
        self.menu_btn.clicked.connect(self.show_more_menu)
        
        search_layout.addWidget(self.search_group_input)
        search_layout.addWidget(self.search_name_input)
        search_layout.addWidget(self.menu_btn)
        
        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.table)
        
        # 将左右布局添加到内容布局
        content_layout.addLayout(left_layout, 2)
        content_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(content_layout)
        
        # 底部输入区域 (横跨整个界面)
        input_layout = QHBoxLayout()
        
        # 替换为下拉框 + 管理按钮的组合
        group_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.setMinimumWidth(100)
        
        self.manage_group_btn = QPushButton("⚙")
        self.manage_group_btn.setObjectName("manageBtn")
        self.manage_group_btn.setToolTip("管理分组")
        self.manage_group_btn.setFixedWidth(50)
        self.manage_group_btn.clicked.connect(self.opened_group_manager)
        
        group_layout.addWidget(self.group_combo)
        group_layout.addWidget(self.manage_group_btn)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('名称')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('用户名')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('密码')
        # 改为明文显示
        # self.password_input.setEchoMode(QLineEdit.Password) 
        
        # 随机密码生成按钮
        self.gen_pwd_btn = QPushButton("🎲")
        self.gen_pwd_btn.setFixedWidth(50)
        self.gen_pwd_btn.setToolTip("生成8位随机复杂密码")
        self.gen_pwd_btn.clicked.connect(self.generate_random_password)
        self.gen_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                border: 1px solid rgba(27,31,35,0.15);
                font-size: 22px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        
        add_button = QPushButton('添加/更新') # 更新按钮文字以反映功能
        add_button.clicked.connect(self.add_password)
        delete_button = QPushButton('删除')
        delete_button.clicked.connect(self.delete_password)
        
        input_layout.addLayout(group_layout)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(self.password_input)
        input_layout.addWidget(self.gen_pwd_btn)
        input_layout.addWidget(add_button)
        input_layout.addWidget(delete_button)
        
        main_layout.addLayout(input_layout)
        
        # 底部作者信息
        author_label = QLabel("Designed by BigDollar | Email: lylovelj@gmail.com")
        author_label.setObjectName("authorLabel")
        author_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(author_label)
    
    def load_data(self):
        self.load_groups()
        self.load_passwords()

    def show_more_menu(self):
        menu = QMenu(self)
        
        export_action = QAction("📤 导出数据 (JSON)", self)
        export_action.triggered.connect(self.export_data)
        menu.addAction(export_action)
        
        import_action = QAction("📥 导入数据 (JSON)", self)
        import_action.triggered.connect(self.import_data)
        menu.addAction(import_action)
        
        # 在按钮位置显示菜单
        menu.exec_(self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height())))

    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出密码数据", "", "JSON Files (*.json)")
        if not file_path:
            return
            
        try:
            passwords = self.db.get_all_passwords()
            export_list = []
            for id, name, username, password, group_name, note in passwords:
                export_list.append({
                    "group": group_name,
                    "name": name,
                    "username": username,
                    "password": password,
                    "note": note
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_list, f, indent=4, ensure_ascii=False)
                
            QMessageBox.information(self, "导出成功", f"成功导出 {len(export_list)} 条记录！")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))

    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入密码数据", "", "JSON Files (*.json)")
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON格式错误：根元素必须是列表")
            
            added_count = 0
            updated_count = 0
            
            for item in data:
                # 简单验证必要字段
                if not all(k in item for k in ("group", "name", "username", "password")):
                    continue
                
                group = item.get("group", "未分组")
                name = item.get("name")
                username = item.get("username")
                password = item.get("password")
                note = item.get("note", "")
                
                # 确保分组存在
                self.db.add_group(group)
                
                # 检查是否存在，存在则更新，不存在则添加
                existing_id = self.db.get_password_id(group, name)
                
                if existing_id:
                    self.db.update_password(existing_id, name, username, password, group, note)
                    updated_count += 1
                else:
                    self.db.add_password(name, username, password, group, note)
                    added_count += 1
            
            self.load_data()
            QMessageBox.information(self, "导入成功", f"导入完成！\n新增: {added_count}\n更新: {updated_count}")
            
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"错误详情: {str(e)}")

    def generate_random_password(self):
        """生成8位复杂密码（字母+数字+符号）"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = ''.join(random.choice(chars) for _ in range(8))
        self.password_input.setText(pwd)


    def load_groups(self):
        current = self.group_combo.currentText()
        self.group_combo.clear()
        groups = self.db.get_all_groups()
        self.group_combo.addItems(groups)
        
        # 尝试恢复之前的选择
        index = self.group_combo.findText(current)
        if index >= 0:
            self.group_combo.setCurrentIndex(index)
        elif self.group_combo.count() > 0:
            self.group_combo.setCurrentIndex(0)
            
    def opened_group_manager(self):
        dialog = GroupManageDialog(self.db, self)
        dialog.exec_()
        # 关闭对话框后刷新分组列表
        self.load_groups()

    def load_passwords(self):
        passwords = self.db.get_all_passwords()
        self.table.setRowCount(len(passwords))
        
        for row, (id, name, username, password, group_name, note) in enumerate(passwords):
            group_item = QTableWidgetItem(group_name)
            group_item.setData(Qt.UserRole, id)
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, id)
            
            self.table.setItem(row, 0, group_item)
            self.table.setItem(row, 1, name_item)
            
        # 重新应用当前的搜索过滤
        self.search_passwords()
            
    def search_passwords(self):
        group_filter = self.search_group_input.text().lower()
        name_filter = self.search_name_input.text().lower()
        
        for row in range(self.table.rowCount()):
            group_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            
            if group_item and name_item:
                group_text = group_item.text().lower()
                name_text = name_item.text().lower()
                
                show_row = True
                if group_filter and group_filter not in group_text:
                    show_row = False
                if name_filter and name_filter not in name_text:
                    show_row = False
                    
                self.table.setRowHidden(row, not show_row)
    
    def show_password_details(self, row, column):
        item = self.table.item(row, 0)
        if item:
            password_id = item.data(Qt.UserRole)
            self.current_viewing_id = password_id # 记录当前查看的ID
            password_data = self.db.get_password_by_id(password_id)
            if password_data:
                # 只设置一列的值
                self.detail_table.setItem(0, 0, QTableWidgetItem(password_data[2]))
                self.detail_table.setItem(1, 0, QTableWidgetItem('*' * len(password_data[3])))
                # 加载备注
                self.note_edit.setPlainText(password_data[5])
    
    def save_current_note(self):
        if self.current_viewing_id:
            content = self.note_edit.toPlainText()
            self.db.update_note(self.current_viewing_id, content)
            
    def edit_password(self, row, column):
        item = self.table.item(row, 0)
        if item:
            password_id = item.data(Qt.UserRole)
            password_data = self.db.get_password_by_id(password_id)
            if password_data:
                # 设置下拉框选中项
                group_name = password_data[4]
                index = self.group_combo.findText(group_name)
                if index >= 0:
                    self.group_combo.setCurrentIndex(index)
                
                self.name_input.setText(password_data[1])
                self.username_input.setText(password_data[2])
                self.password_input.setText(password_data[3])
                self.editing_id = password_id
    
    def add_password(self):
        name = self.name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        group_name = self.group_combo.currentText()
        
        if not name or not username or not password:
            QMessageBox.warning(self, '警告', '所有字段都必须填写！')
            return
        
        # 检查同分组下是否存在相同名称
        if hasattr(self, 'editing_id'):
            if self.db.check_name_exists(name, group_name, self.editing_id):
                QMessageBox.warning(self, '警告', f'分组"{group_name}"下已存在名称为"{name}"的记录！')
                return
            
            # 为了防止覆盖备注，需要先获取原有的备注
            old_data = self.db.get_password_by_id(self.editing_id)
            existing_note = old_data[5] if old_data else ''
            
            self.db.update_password(self.editing_id, name, username, password, group_name, existing_note)
            delattr(self, 'editing_id')
        else:
            if self.db.check_name_exists(name, group_name):
                QMessageBox.warning(self, '警告', f'分组"{group_name}"下已存在名称为"{name}"的记录！')
                return
            self.db.add_password(name, username, password, group_name)
        
        self.load_passwords()
        
        # 清空输入框，但保留分组选择以便连续添加
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
            # 清空预览区
            self.detail_table.clearContents()
            self.note_edit.clear()
            self.current_viewing_id = None