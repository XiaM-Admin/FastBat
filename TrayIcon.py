from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QStyle
import subprocess
import os


class TrayIcon(QSystemTrayIcon):
   def __init__(self, parent=None):
       super().__init__(parent)
       
       # 确保图标文件存在
       # 设置图标
       icon_path = "icon.png"
       if os.path.exists(icon_path):
           self.setIcon(QIcon(icon_path))
       else:
           app = QApplication.instance()
           self.setIcon(app.style().standardIcon(QStyle.SP_ComputerIcon))
       
       # 创建右键菜单
       self.menu = QMenu()
       # 设置菜单样式，移除图标空间
       self.menu.setStyleSheet("""
           QMenu::item { 
               padding-left: 8px; 
               padding-right: 8px; 
           }
           QMenu::item:selected { 
               background-color: #0078d7;
               color: white;
           }
       """)


       # 创建脚本子菜单
       self.scripts_menu = QMenu("Bat脚本")
       # 对子菜单也应用相同的样式
       self.scripts_menu.setStyleSheet("""
           QMenu::item { 
               padding-left: 8px; 
               padding-right: 15px; 
           }
           QMenu::item:selected { 
               background-color: #0078d7;
               color: white;
           }
       """)
       self.menu.addMenu(self.scripts_menu)

       # 添加Python脚本子菜单
       self.python_scripts_menu = QMenu("Py脚本")
       self.python_scripts_menu.setStyleSheet("""
           QMenu::item { 
               padding-left: 8px; 
               padding-right: 15px; 
           }
           QMenu::item:selected { 
               background-color: #0078d7;
               color: white;
           }
       """)
       self.menu.addMenu(self.python_scripts_menu)

       # 添加打开根目录选项
       self.open_root_action = QAction("程序根目录", self)
       self.open_root_action.triggered.connect(self.open_root_directory)
       self.menu.addAction(self.open_root_action)
       
        # 添加重载脚本选项
       self.reload_action = QAction("重新加载脚本", self)
       self.reload_action.triggered.connect(self.reload_scripts)  # 连接到加载脚本方法
       self.menu.addAction(self.reload_action)
       
       # 添加退出选项
       self.exit_action = QAction("退出", self)
       self.exit_action.triggered.connect(QCoreApplication.quit)  # 修改这行
       self.menu.addAction(self.exit_action)
       
       # 设置菜单
       self.setContextMenu(self.menu)
       
       # 添加鼠标点击事件处理
       self.activated.connect(self.onTrayIconActivated)

       # 显示托盘图标
       self.show()
       
       # 添加提示信息
       self.setToolTip("X FastBat")

       # 初始化隐藏列表
       self.hidden_items = self._load_hidden_items()
       # 初始加载脚本
       self.load_scripts()
       self.load_python_scripts()
       

   def onTrayIconActivated(self, reason):
        """处理托盘图标的点击事件"""
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            # 获取鼠标当前位置
            cursor = QApplication.desktop().cursor()
            pos = cursor.pos()
            # 显示菜单
            self.menu.popup(pos)

   def _load_hidden_items(self):
        """读取hide.txt文件中的隐藏项目列表"""
        hidden_items = set()
        try:
            if os.path.exists('hide.txt'):
                with open('hide.txt', 'r', encoding='utf-8') as f:
                    # 修改这里：先读取所有内容，然后按行分割
                    for line in f.read().strip().splitlines():
                        if line:
                            hidden_items.add(line.strip())
        except Exception as e:
            self.showMessage("警告", f"读取hide.txt失败: {str(e)}", QSystemTrayIcon.Warning)
        return hidden_items

   def _should_hide_item(self, item_path):
        """检查项目是否应该被隐藏"""
        item_name = os.path.basename(item_path)
        relative_path = os.path.relpath(item_path, os.getcwd())
        return item_name in self.hidden_items or relative_path in self.hidden_items

   def reload_scripts(self):
        """重新加载所有脚本"""
        self.load_scripts()
        self.load_python_scripts()
        # 初始化隐藏列表
        self.hidden_items = self._load_hidden_items()

   def load_scripts(self):
        """递归加载at文件夹中的所有批处理脚本"""
        # 清空现有脚本菜单
        self.scripts_menu.clear()
        # 检查Bat文件夹是否存在
        bat_folder = "Bat"
        if not os.path.exists(bat_folder):
            return
        # 递归加载文件夹中的脚本
        self._load_scripts_from_folder(bat_folder, self.scripts_menu)    
   
   def load_python_scripts(self):
        """递归加载Py文件夹中的所有Python脚本"""
        # 清空现有Python脚本菜单
        self.python_scripts_menu.clear()
        # 检查Py文件夹是否存在
        py_folder = "Py"
        if not os.path.exists(py_folder):
            return
        # 递归加载文件夹中的脚本
        self._load_python_scripts_from_folder(py_folder, self.python_scripts_menu)

   def _load_python_scripts_from_folder(self, folder_path, parent_menu):
        """递归加载指定文件夹中的Python脚本
        Args:
            folder_path: 要加载的文件夹路径
            parent_menu: 父级菜单项
        """
        # 遍历文件夹中的所有项目
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # 检查是否应该隐藏
            if self._should_hide_item(item_path):
                continue

            if os.path.isdir(item_path):
                # 如果是文件夹，创建子菜单
                submenu = QMenu(item, parent_menu)
                submenu.setStyleSheet(self.menu.styleSheet())
                parent_menu.addMenu(submenu)
                # 递归加载子文件夹
                self._load_python_scripts_from_folder(item_path, submenu)
            elif item.endswith('.py'):
                # 如果是py文件，添加到当前菜单
                script_name = os.path.splitext(item)[0]
                action = QAction(script_name, self)
                action.triggered.connect(lambda checked, path=item_path: self.run_python_script(path))
                parent_menu.addAction(action)

   def _load_scripts_from_folder(self, folder_path, parent_menu):
        """递归加载指定文件夹中的脚本
        Args:
            folder_path: 要加载的文件夹路径
            parent_menu: 父级菜单项
        """
        # 遍历文件夹中的所有项目
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # 检查是否应该隐藏
            if self._should_hide_item(item_path):
                continue

            if os.path.isdir(item_path):
                # 如果是文件夹，创建子菜单
                submenu = QMenu(item, parent_menu)
                # 应用与主菜单相同的样式
                submenu.setStyleSheet(self.menu.styleSheet())
                parent_menu.addMenu(submenu)
                # 递归加载子文件夹
                self._load_scripts_from_folder(item_path, submenu)
            elif item.endswith('.bat'):
                # 如果是bat文件，添加到当前菜单
                script_name = os.path.splitext(item)[0]
                action = QAction(script_name, self)
                action.triggered.connect(lambda checked, path=item_path: self.run_script(path))
                parent_menu.addAction(action)

   def run_script(self, script_path):
       """执行指定的批处理脚本"""
       try:
           os.startfile(script_path)
       except Exception as e:
           self.showMessage("错误", f"执行脚本失败: {str(e)}", QSystemTrayIcon.Critical)

      # 在类的末尾添加新方法
   
   def run_python_script(self, script_path):
    """执行指定的Python脚本，支持conda环境"""
    try:
        cmd = f'start cmd /k python "{script_path}" ^& pause ^& exit'
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        self.showMessage("错误", f"执行Python脚本失败: {str(e)}", QSystemTrayIcon.Critical)

   def open_root_directory(self):
        """打开程序的根目录"""
        try:
            os.startfile(os.getcwd())
        except Exception as e:
            self.showMessage("错误", f"打开目录失败: {str(e)}", QSystemTrayIcon.Critical)