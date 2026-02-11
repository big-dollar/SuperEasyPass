from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QPushButton, 
                            QLabel, QLineEdit, QHeaderView, QMessageBox,
                            QComboBox, QDialog, QInputDialog, QListWidget, QTextEdit,
                            QFileDialog, QMenu, QAction, QSystemTrayIcon, QApplication,
                            QWhatsThis, QToolTip)
from PyQt5.QtCore import Qt, QPoint, QUrl, QEvent, QTimer
from PyQt5.QtGui import QIcon, QDesktopServices, QCursor
from database import PasswordDatabase
import random
import string
import json
import sys
import os
import winreg


class DatabaseSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据库设置")
        self.setFixedSize(450, 250)
        self.db_path = None
        self.startup_password = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 提示信息
        layout.addWidget(QLabel("找不到数据库文件，请选择操作："))
        
        # 操作选择
        self.radio_layout = QHBoxLayout()
        # Create a container widget for radios to manage exclusion
        radio_group = QWidget()
        radio_group_layout = QHBoxLayout(radio_group)
        self.create_radio = QPushButton("创建新数据库")
        self.create_radio.setCheckable(True)
        self.create_radio.setChecked(True)
        self.create_radio.clicked.connect(lambda: self.toggle_mode(True))
        
        self.open_radio = QPushButton("打开现有数据库") 
        self.open_radio.setCheckable(True)
        self.open_radio.clicked.connect(lambda: self.toggle_mode(False))
        
        # Make them act like radio buttons visually
        self.update_radio_styles()
        
        self.radio_layout.addWidget(self.create_radio)
        self.radio_layout.addWidget(self.open_radio)
        layout.addLayout(self.radio_layout)
        
        # 路径选择
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
        # 启动密码设置 (仅新建模式显示, 或者总是显示作为更新?)
        # 需求: "首次启动在以上的窗口增加用户的启动密码... 如果留空则无密码"
        # 解释: 这里我们允许用户设置启动密码。
        self.pwd_label = QLabel("设置启动密码 (留空则无密码):")
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setPlaceholderText("在此输入启动密码(明文显示)")
        layout.addWidget(self.pwd_label)
        layout.addWidget(self.pwd_edit)
        
        # 确认按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("退出")
        cancel_btn.clicked.connect(self.reject)
        
        # 样式
        ok_btn.setStyleSheet("background-color: #2ea44f; color: white;")
        cancel_btn.setStyleSheet("background-color: #d73a49; color: white;")
        
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.is_create_mode = True

    def update_radio_styles(self):
        active = "background-color: #0366d6; color: white;"
        inactive = "background-color: #f6f8fa; color: black;"
        self.create_radio.setStyleSheet(active if self.create_radio.isChecked() else inactive)
        self.open_radio.setStyleSheet(active if self.open_radio.isChecked() else inactive)

    def toggle_mode(self, is_create):
        self.is_create_mode = is_create
        self.create_radio.setChecked(is_create)
        self.open_radio.setChecked(not is_create)
        self.update_radio_styles()
        
        if is_create:
            self.create_radio.setText("✓ 创建新数据库")
            self.open_radio.setText("打开现有数据库")
            self.pwd_label.setText("设置启动密码 (留空则无密码):")
            self.pwd_edit.setEnabled(True)
        else:
            self.create_radio.setText("创建新数据库")
            self.open_radio.setText("✓ 打开现有数据库")
            self.pwd_label.setText("启动密码 (如果现有库有密码，此处不用填):")
            self.pwd_edit.setEnabled(False) # 打开现有库时不在此处修改密码? 或者允许修改?
            # 简化逻辑：打开库时，我们只链接路径。如果用户想改密码，应该在软件内改(虽然暂无功能)。
            # 但也许用户忘记密码想重置？不行，这是"找回"功能。
            # 暂且禁用，避免混淆。
            self.pwd_edit.clear()

    def browse_path(self):
        if self.is_create_mode:
            path, _ = QFileDialog.getSaveFileName(self, "创建数据库", "", "SQLite Database (*.db)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "打开数据库", "", "SQLite Database (*.db)")
            
        if path:
            self.path_edit.setText(path)

    def accept(self):
        path = self.path_edit.text()
        if not path:
            QMessageBox.warning(self, "提示", "请选择数据库路径")
            return
            
        self.db_path = path
        # 仅在创建模式下读取密码输入，或者虽然是Open模式但如果以后支持重置也可以
        if self.is_create_mode:
            self.startup_password = self.pwd_edit.text()
        else:
            self.startup_password = None # Open模式保持原样
            
        super().accept()

class StartupLoginDialog(QDialog):
    def __init__(self, saved_password, parent=None):
        super().__init__(parent)
        self.saved_password = saved_password
        self.setWindowTitle("安全验证")
        self.setFixedSize(300, 150)
        # 去掉问号
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请输入启动密码:"))
        
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.pwd_edit.returnPressed.connect(self.check_password)
        layout.addWidget(self.pwd_edit)
        
        btn = QPushButton("登录")
        btn.clicked.connect(self.check_password)
        btn.setStyleSheet("background-color: #2ea44f; color: white; padding: 8px;")
        layout.addWidget(btn)
        
    def check_password(self):
        if self.pwd_edit.text() == self.saved_password:
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "密码错误！")
            self.pwd_edit.clear()
            self.pwd_edit.setFocus()

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
        # 移除标题栏的帮助按钮（问号）
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
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
    def __init__(self, db_path):
        super().__init__()
        if not db_path:
            raise ValueError("Database path must be provided")
            
        self.db = PasswordDatabase(db_path)
        self.current_viewing_id = None
        self.current_password = None  # 保存当前查看的真实密码
        self.init_ui()
        self.init_tray_icon()  # 初始化系统托盘
        self.load_data()
        
    def init_ui(self):
        self.setWindowTitle('超容易密码管理器 (SuperEasyPass) - V1.1')
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
            /* 气泡提示样式优化 */
            QToolTip {
                background-color: #24292e;
                color: #ffffff;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
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
        self.detail_table.cellClicked.connect(self.copy_password_to_clipboard)  # 添加点击事件
        
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
        
        # 实现悬停1秒显示气泡功能
        self.table.setMouseTracking(True)
        self.table.entered.connect(self.handle_table_hover)
        self.table.viewport().installEventFilter(self)
        
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self.show_edit_tip)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        
        self.search_group_input = QLineEdit()
        self.search_group_input.setPlaceholderText('🔍 搜索分组...')
        self.search_group_input.textChanged.connect(self.search_passwords)
        
        self.search_name_input = QLineEdit()
        self.search_name_input.setPlaceholderText('🔍 搜索名称...')
        self.search_name_input.textChanged.connect(self.search_passwords)
        
        # 新增帮助按钮（问号）
        self.help_btn = QPushButton("?")
        self.help_btn.setFixedWidth(40)
        self.help_btn.setToolTip("查看帮助 / 源码 (GitHub)")
        self.help_btn.setStyleSheet("""
            QPushButton { 
                background-color: #f6f8fa; 
                color: #586069; 
                border: 1px solid #e1e4e8; 
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover { 
                background-color: #0366d6; 
                color: white; 
                border: 1px solid #0366d6;
            }
        """)
        self.help_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/big-dollar/SuperEasyPass")))

        # 更多选项按钮（导出/导入）
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedWidth(40)
        self.menu_btn.setToolTip("更多选项 (导入/导出)")
        self.menu_btn.clicked.connect(self.show_more_menu)
        
        search_layout.addWidget(self.search_group_input)
        search_layout.addWidget(self.search_name_input)
        search_layout.addWidget(self.help_btn)
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
        
        menu.addSeparator()
        
        # 开机自启动选项
        startup_action = QAction("🚀 开机自启动", self)
        startup_action.setCheckable(True)
        startup_action.setChecked(self.is_startup_enabled())
        startup_action.triggered.connect(self.toggle_startup)
        menu.addAction(startup_action)
        
        # 在按钮位置显示菜单
        menu.exec_(self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height())))
    
    def is_startup_enabled(self):
        """检查是否已设置开机自启动"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "SuperEasyPass")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def toggle_startup(self):
        """切换开机自启动状态"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            if self.is_startup_enabled():
                # 删除自启动
                winreg.DeleteValue(key, "SuperEasyPass")
                QMessageBox.information(self, "开机自启动", "已取消开机自启动")
            else:
                # 添加自启动
                app_path = os.path.abspath(sys.argv[0])
                # 如果是python脚本，需要用pythonw执行
                if app_path.endswith('.py'):
                    python_path = sys.executable.replace('python.exe', 'pythonw.exe')
                    startup_cmd = f'"{python_path}" "{app_path}"'
                else:
                    startup_cmd = f'"{app_path}"'
                    
                winreg.SetValueEx(key, "SuperEasyPass", 0, winreg.REG_SZ, startup_cmd)
                QMessageBox.information(self, "开机自启动", "已设置开机自启动")
                
            winreg.CloseKey(key)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置失败: {str(e)}")

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
                # 保存真实密码和用户名以便复制
                self.current_username = password_data[2]
                self.current_password = password_data[3]
                # 只设置一列的值
                self.detail_table.setItem(0, 0, QTableWidgetItem(password_data[2]))
                self.detail_table.setItem(1, 0, QTableWidgetItem('*' * len(password_data[3])))
                # 加载备注
                self.note_edit.setPlainText(password_data[5])
    
    def copy_password_to_clipboard(self, row, column):
        """点击用户名或密码字段时复制到剪贴板"""
        clipboard = QApplication.clipboard()
        
        if row == 0 and hasattr(self, 'current_username'):  # 第0行是用户名
            clipboard.setText(self.current_username)
            self.tray_icon.showMessage(
                "复制成功",
                "用户名已复制到剪贴板！",
                QSystemTrayIcon.Information,
                1500
            )
        elif row == 1 and self.current_password:  # 第1行是密码行
            clipboard.setText(self.current_password)
            # 使用托盘气泡提示，不打断用户操作
            self.tray_icon.showMessage(
                "复制成功",
                "密码已复制到剪贴板！",
                QSystemTrayIcon.Information,
                1500
            )
    
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
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def init_tray_icon(self):
        """初始化系统托盘图标"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置图标
        # 使用新的 resource_path 方法获取图标路径
        icon_path = self.resource_path("RuxiPass.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 如果图标文件不存在，尝试尝试原始路径（开发环境备用）
            dev_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RuxiPass.ico")
            if os.path.exists(dev_path):
                self.tray_icon.setIcon(QIcon(dev_path))
            else:
                # 使用默认图标
                self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # 设置提示文本
        self.tray_icon.setToolTip("超容易密码管理器 (SuperEasyPass)")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出程序", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """托盘图标被激活时的处理"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """显示主窗口"""
        self.show()
        self.activateWindow()  # 激活窗口，使其获得焦点
        self.raise_()  # 将窗口提到最前面
    
    def closeEvent(self, event):
        """重写关闭事件，最小化到托盘而不是退出"""
        event.ignore()  # 忽略关闭事件
        self.hide()  # 隐藏窗口
        # 首次最小化到托盘时显示提示
        if not hasattr(self, '_tray_tip_shown'):
            self.tray_icon.showMessage(
                "超容易密码管理器",
                "程序已最小化到系统托盘，双击托盘图标可重新打开",
                QSystemTrayIcon.Information,
                2000
            )
            self._tray_tip_shown = True
    
    def quit_application(self):
        """真正退出应用程序"""
        self.tray_icon.hide()  # 隐藏托盘图标
        QApplication.instance().quit()  # 退出应用

    def handle_table_hover(self, index):
        """当鼠标进入表格单元格时，启动1秒计时器"""
        self.tooltip_timer.stop()
        if index.isValid():
            self.tooltip_timer.start(1000) # 1000ms = 1s

    def show_edit_tip(self):
        """显示气泡提示"""
        QToolTip.showText(QCursor.pos(), "💡 双击可编辑/更新此记录", self.table)

    def eventFilter(self, source, event):
        """事件过滤器：处理鼠标离开表格时隐藏气泡"""
        if source == self.table.viewport() and event.type() == QEvent.Leave:
            self.tooltip_timer.stop()
            QToolTip.hideText()
        return super().eventFilter(source, event)