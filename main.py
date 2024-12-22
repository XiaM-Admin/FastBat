"""
是一个快速启动Bat批处理脚本的后台托盘程序
件不需要界面，只需要托盘图标
"""
import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication  # 添加这行
import os
class TrayIcon(QSystemTrayIcon):
   def __init__(self, parent=None):
       super().__init__(parent)
       
       # 确保图标文件存在
       icon_path = "egg-icon.png"
       if not os.path.exists(icon_path):
           raise FileNotFoundError(f"图标文件 {icon_path} 不存在")
           
       # 设置图标
       self.setIcon(QIcon(icon_path))
       
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
       self.scripts_menu = QMenu("脚本列表")
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

        # 添加重载脚本选项
       self.reload_action = QAction("重新加载脚本", self)
       self.reload_action.triggered.connect(self.load_scripts)  # 连接到加载脚本方法
       self.menu.addAction(self.reload_action)
       
       # 添加退出选项
       self.exit_action = QAction("退出", self)
       self.exit_action.triggered.connect(QCoreApplication.quit)  # 修改这行
       self.menu.addAction(self.exit_action)
       
       # 设置菜单
       self.setContextMenu(self.menu)
       
       # 显示托盘图标
       self.show()
       
       # 添加提示信息
       self.setToolTip("批处理脚本启动器")

       # 初始加载脚本
       self.load_scripts()

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
   
   def _load_scripts_from_folder(self, folder_path, parent_menu):
        """递归加载指定文件夹中的脚本
        Args:
            folder_path: 要加载的文件夹路径
            parent_menu: 父级菜单项
        """
        # 遍历文件夹中的所有项目
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
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


if __name__ == '__main__':
   # 防止程序直接退出
   app = QApplication(sys.argv)
   app.setQuitOnLastWindowClosed(False)  # 添加这行
   
   try:
       tray = TrayIcon()
       sys.exit(app.exec_())
   except Exception as e:
       print(f"程序出错: {str(e)}")
       sys.exit(1)