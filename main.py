"""
是一个快速启动Bat批处理脚本的后台托盘程序
件不需要界面，只需要托盘图标
"""
import sys
from PyQt5.QtWidgets import QApplication
from TrayIcon import TrayIcon

if __name__ == '__main__':
   # 防止程序直接退出
   app = QApplication(sys.argv)
   app.setQuitOnLastWindowClosed(False)
   
   try:
       tray = TrayIcon()
       sys.exit(app.exec_())
   except Exception as e:
       print(f"程序出错: {str(e)}")
       sys.exit(1)