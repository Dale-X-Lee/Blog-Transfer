# main.py
import sys
from PyQt5.QtWidgets import QApplication
from pathlib import Path

from file_processor import FileProcessor
from gui import MainWindow
# 假设 gui.py 已经提供了 MainWindow

class MainApplication:
    """PyQt5 应用程序的主控制器
    
    负责初始化 GUI 应用程序，管理主窗口，并处理核心业务逻辑：
    
    主要功能：
      1. 创建 QApplication 实例和 MainWindow 主窗口
      2. 连接 GUI 事件与业务逻辑处理函数：
          - 文件选择事件: 自动提取标题并预填充到 GUI
          - 表单提交事件: 处理文件转换并显示结果
      3. 启动应用程序事件循环
    
    工作流程：
      - 用户选择文件 → 触发 _on_file_select() → 预填充标题
      - 用户填写元数据并提交 → 触发 _on_submit()
        → 调用 FileProcessor 处理文件 → 显示成功/错误信息
    
    回调方法说明：
      _on_file_select(): 根据文件类型预填充标题
        - .md 文件: 提取一级标题
        - .pdf 文件: 使用文件名（不含扩展名）作为标题
      
      _on_submit(): 处理文件转换的核心逻辑
        1. 获取输出目录
        2. 调用 FileProcessor.process_file()
        3. 显示处理结果（成功路径或错误信息）
    
    使用示例：
      if __name__ == '__main__':
          MainApplication().run()
    """
    def __init__(self):
        """
        初始化主应用程序
        
        执行以下操作：
        1. 创建 QApplication 实例（PyQt5 应用核心）
        2. 创建主窗口实例（MainWindow）
           - 绑定文件选择回调函数：_on_file_select
           - 绑定表单提交回调函数：_on_submit
        3. 显示主窗口
        
        注意：必须先创建 QApplication 实例，然后才能创建任何 GUI 组件
        """
        # 先创建 QApplication
        self.app = QApplication(sys.argv)
        # 再创建窗口
        self.window = MainWindow(
            on_file_select=self._on_file_select,
            on_submit=self._on_submit,
        )
        self.window.show()

    def _on_file_select(self, file_path):
        """
        文件选择回调函数（由 GUI 触发）
        
        根据选择的文件类型自动预填充标题：
          - Markdown 文件: 提取一级标题
          - PDF 文件: 使用文件名（不含扩展名）作为标题
        
        :param file_path: 用户选择的文件路径
        """
        # 示例：把 md 标题回显到 GUI
        if file_path.lower().endswith('.md'):
            title = FileProcessor.extract_title_from_md(file_path)
            self.window.prefill_title(title or "")
        elif file_path.lower().endswith('.pdf'):
            self.window.prefill_title(Path(file_path).stem)

    def _on_submit(self, input_path, metadata):
        """
        表单提交回调函数（由 GUI 触发）
        
        核心文件处理流程：
        1. 从 GUI 获取输出目录
        2. 调用 FileProcessor 处理文件
        3. 在 GUI 中显示处理结果（成功信息或错误提示）
        
        :param input_path: 输入文件路径
        :param metadata: 包含标题、描述等元数据的字典
        """
        try:
            out_dir = self.window.output_dir()
            new_file = FileProcessor.process_file(input_path, out_dir, metadata)
            self.window.show_success(f"已生成：{new_file}")
        except Exception as e:
            self.window.show_error(str(e))

    def run(self):
        """
        启动应用程序主事件循环
        
        执行以下操作：
        1. 调用 QApplication.exec_() 启动事件循环
        2. 使用 sys.exit() 确保应用正确退出
        3. 阻塞直到应用程序关闭
        
        注意：这是应用程序的入口点，应在创建 MainApplication 实例后调用
        """
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    MainApplication().run()