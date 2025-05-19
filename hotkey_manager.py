import keyboard
import win32con
import win32api
import win32gui
import ctypes
from PyQt5.QtCore import QObject, QPoint, QTimer, pyqtSignal
from menu import PasswordMenu
from database import PasswordDatabase
import mouse

# 定义回调函数类型
CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))

class HotkeyManager(QObject):
    show_menu_signal = pyqtSignal(QPoint)
    
    def __init__(self, password_manager):
        super().__init__()
        self.password_manager = password_manager
        self.db = PasswordDatabase()
        self.menu = None
        self.ctrl_pressed = False
        self.show_timer = QTimer(self)
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self.delayed_show_menu)
        
        # 改用键盘事件监听
        keyboard.on_press_key('ctrl', self.on_ctrl_press)
        keyboard.on_release_key('ctrl', self.on_ctrl_release)
        
        # 创建回调函数
        self._hook_proc = CMPFUNC(self._mouse_hook_proc)
        
        # 添加鼠标钩子
        self.hook = ctypes.windll.user32.SetWindowsHookExW(
            win32con.WH_MOUSE_LL,
            self._hook_proc,
            None,
            0
        )
        
        if not self.hook:
            raise Exception('Failed to set mouse hook')
        
        self.show_menu_signal.connect(self.show_password_menu_in_main_thread)
    
    def _mouse_hook_proc(self, nCode, wParam, lParam):
        try:
            if nCode >= 0 and self.ctrl_pressed:
                if wParam == win32con.WM_RBUTTONDOWN:
                    # 获取鼠标位置并显示菜单
                    cursor_pos = win32gui.GetCursorPos()
                    point = QPoint(cursor_pos[0], cursor_pos[1])
                    self.show_menu_signal.emit(point)
                    # 阻止事件传递
                    return 1
        except:
            pass
        # 继续传递事件
        return ctypes.windll.user32.CallNextHookEx(self.hook, nCode, wParam, lParam)
    
    def __del__(self):
        if hasattr(self, 'hook') and self.hook:
            ctypes.windll.user32.UnhookWindowsHookEx(self.hook)

    def on_ctrl_press(self, e):
        self.ctrl_pressed = True
    
    def on_ctrl_release(self, e):
        self.ctrl_pressed = False
    
    def on_right_click(self):
        if self.ctrl_pressed:
            try:
                # 获取当前鼠标位置
                cursor_pos = win32gui.GetCursorPos()
                point = QPoint(cursor_pos[0], cursor_pos[1])
                self.show_menu_signal.emit(point)
            except Exception as e:
                print(f"鼠标事件处理错误: {e}")
    
    def show_password_menu_in_main_thread(self, point):
        try:
            passwords = self.db.get_all_passwords()
            
            if self.menu:
                try:
                    self.menu.hide()
                    self.menu.deleteLater()
                except:
                    pass
            
            # 创建新菜单
            self.menu = PasswordMenu(point, passwords)
            self.menu.setParent(None)  # 设置为顶级窗口
            
            # 使用定时器延迟显示菜单
            self.show_timer.start(50)
            
        except Exception as e:
            print(f"显示密码菜单时出错: {e}")
    
    def delayed_show_menu(self):
        try:
            if self.menu:
                # 重新设置位置并显示
                cursor_pos = win32gui.GetCursorPos()
                self.menu.move(cursor_pos[0], cursor_pos[1])
                self.menu.show()
                self.menu.activateWindow()
        except Exception as e:
            print(f"延迟显示菜单时出错: {e}")