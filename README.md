# 🚀 超容易密码管理器 (SuperEasyPass)

> **可能是 Windows 上最顺滑、最“无脑”好用的 Python 本地密码管理工具。拒绝繁琐，一键自动填充！**

![Version](https://img.shields.io/badge/version-V1.0-blue.svg) ![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg) ![Platform](https://img.shields.io/badge/Platform-Windows-00a2ed.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🌟 为什么选择它？(Why SuperEasyPass?)

你是否厌倦了那些臃肿、收费、还需要联网的密码管理器？
**SuperEasyPass** 就是为你打造的**终极效率神器**！它不仅是一个存储工具，更是你的**生产力加速器**。

*   ⚡ **神级一键填充**：独创 **`Ctrl + 鼠标右键`** 全局召唤悬浮菜单，0.05秒极速自动输入账号密码！彻底告别 `Ctrl+C` / `Ctrl+V` 的重复劳动！
*   🎨 **颜值即正义**：采用 **Notion / GitHub** 同款现代化设计语言，清爽、简约、高级。让管理密码也成为一种视觉享受。
*   🔐 **数据绝对掌控**：**100% 本地化存储 (SQLite)**，绝不上传云端，不需要注册账号。你的数据完全属于你，拔掉网线也能用！
*   🧠 **聪明且强大**：内置**随机密码生成器**、**实时搜索过滤**、**自动保存备注**... 每一个细节都经过精心打磨，只为让你用得更顺手。

---

## ✨ 核心功能亮点 (Features)

### 🖱️ 全局光速填充
在任何软件、网页、登录框，只需按住 `Ctrl` 并点击 `鼠标右键`，即可弹出你的密码库菜单。选择目标账号，**Duang！** 账号密码瞬间自动填入，快到看不清！

### 🔍 实时闪电搜索
无论是上百还是上千条密码，通过顶部的**双重搜索框**（分组+名称），输入即筛选，瞬间定位你需的信息。

### 🎲 强密码一键生成
还在用 "123456"？点击界面下方的 **🎲 按钮**，一键生成 8 位包含字母符号的强密码，并自动填入。安全，就这么简单。

### 📝 智能备注系统
忘记了这个账号是干嘛的？右侧贴心的**备注区域**支持多行文本，**失去焦点自动保存**，再也不用担心手滑没保存。

### 📂 灵活分组管理
强大的**分组管理系统**，支持自定义增删分组，让你的工作、生活、娱乐账号井井有条。

---

## 🛠️ 技术栈 (Tech Stack)

本项目完全开源，基于强大的 Python 生态构建：
*   **GUI 框架**: `PyQt5` (打造丝滑流畅的桌面级体验)
*   **系统底层**: `pywin32` / `ctypes` (实现底层的 Windows 钩子与自动化输入)
*   **数据库**: `SQLite3` (轻量、快速、无需配置)
*   **自动化**: `pyautogui` (模拟人类操作，兼容性满分)

---

## 🚀 快速开始 (Quick Start)

### 环境要求
*   Windows 10/11
*   Python 3.x

### 安装依赖
```bash
pip install PyQt5 pywin32 pyautogui keyboard
```

### 运行
```bash
python main.py
```
*(主要逻辑位于 `password_manager.py` 和 `hotkey_manager.py`)*

---

## 👨‍💻 作者 (Author)

**BigDollar**
*   📧 Email: [lylovelj@gmail.com](mailto:lylovelj@gmail.com)
*   💻 致力于开发“简单到令人发指”的高效工具。

---

## 🏷️ 热门标签
#PasswordManager #Python #PyQt5 #Automation #Windows工具 #效率神器 #开源 #自动化 #黑客工具 #PythonGUI #本地存储 #安全隐私

---

*如果觉得这个工具有点意思，请给个 Star ⭐️ 吧！你的支持是我更新的动力！*