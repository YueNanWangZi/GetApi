import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.font import Font

class APIExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("API路径提取工具")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 主题风格
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 自定义字体
        self.title_font = Font(family="微软雅黑", size=14, weight="bold")
        self.button_font = Font(family="微软雅黑", size=10)
        self.status_font = Font(family="微软雅黑", size=9)
        
        # UI元素
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="API路径提取工具", 
            font=self.title_font,
            foreground="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # 说明文本
        desc_label = ttk.Label(
            main_frame, 
            text="选择文件或目录，提取所有以'/'开头的API路径",
            font=self.status_font,
            foreground="#7f8c8d"
        )
        desc_label.pack(pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        # 选择文件按钮
        file_button = ttk.Button(
            button_frame, 
            text="选择文件", 
            command=self.select_file,
            style="Accent.TButton"
        )
        file_button.pack(side=tk.LEFT, padx=10)
        
        # 选择目录按钮
        dir_button = ttk.Button(
            button_frame, 
            text="选择目录", 
            command=self.select_directory,
            style="Accent.TButton"
        )
        dir_button.pack(side=tk.LEFT, padx=10)
        
        # 提取按钮
        self.extract_button = ttk.Button(
            main_frame, 
            text="提取API路径", 
            command=self.extract_apis,
            state=tk.DISABLED,
            style="Accent.TButton"
        )
        self.extract_button.pack(pady=10)
        
        # 进度条框架
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        # 进度标签
        self.progress_label = ttk.Label(
            progress_frame,
            text="等待操作...",
            font=self.status_font,
            foreground="#3498db"
        )
        self.progress_label.pack(anchor=tk.W)
        
        # 进度条
        self.progress = ttk.Progressbar(
            progress_frame, 
            orient=tk.HORIZONTAL, 
            length=550, 
            mode='determinate'
        )
        self.progress.pack(fill=tk.X)
        
        # 进度百分比
        self.progress_percent = ttk.Label(
            progress_frame,
            text="0%",
            font=self.status_font,
            foreground="#e74c3c"
        )
        self.progress_percent.pack(anchor=tk.E)
        
        # 状态框架
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(
            status_frame,
            text="状态: 等待选择文件或目录",
            font=self.status_font,
            foreground="#2c3e50"
        )
        self.status_label.pack(anchor=tk.W)
        
        # 文件计数标签
        self.file_count_label = ttk.Label(
            status_frame,
            text="",
            font=self.status_font,
            foreground="#27ae60"
        )
        self.file_count_label.pack(anchor=tk.W)
        
        # API计数标签
        self.api_count_label = ttk.Label(
            status_frame,
            text="",
            font=self.status_font,
            foreground="#e67e22"
        )
        self.api_count_label.pack(anchor=tk.W)
        
        # 存储选择的文件或目录
        self.target_path = None
        self.is_file = False
        
        # 配置样式
        self.style.configure('Accent.TButton', foreground='white', background='#3498db')
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=(("所有文件", "*.*"), ("文本文件", "*.txt;*.json;*.js;*.java;*.py"),)
        )
        if file_path:
            self.target_path = file_path
            self.is_file = True
            self.update_status(f"已选择文件: {os.path.basename(file_path)}", "#27ae60")
            self.file_count_label.config(text="将处理: 1个文件")
            self.extract_button.config(state=tk.NORMAL)
        
    def select_directory(self):
        dir_path = filedialog.askdirectory(title="选择目录")
        if dir_path:
            self.target_path = dir_path
            self.is_file = False
            file_count = sum([len(files) for _, _, files in os.walk(dir_path)])
            self.update_status(f"已选择目录: {os.path.basename(dir_path)}", "#27ae60")
            self.file_count_label.config(text=f"将处理: {file_count}个文件")
            self.extract_button.config(state=tk.NORMAL)
    
    def extract_apis(self):
        if not self.target_path:
            messagebox.showerror("错误", "请先选择文件或目录")
            return
        
        # 定义正则表达式
        api_pattern = re.compile(r'["\'](/[a-zA-Z0-9\-_/.]+)["\']')
        apis = set()  # 使用集合避免重复
        
        try:
            if self.is_file:
                # 处理单个文件
                self.update_progress(0, "正在处理文件...")
                apis.update(self.extract_from_file(self.target_path, api_pattern))
                self.update_progress(100, "文件处理完成!")
            else:
                # 处理目录下所有文件
                file_count = 0
                for root_dir, _, files in os.walk(self.target_path):
                    file_count += len(files)
                
                processed = 0
                for root_dir, _, files in os.walk(self.target_path):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        apis.update(self.extract_from_file(file_path, api_pattern))
                        processed += 1
                        percent = int((processed / file_count) * 100)
                        self.update_progress(
                            percent, 
                            f"正在处理: {processed}/{file_count} 个文件"
                        )
            
            # 排序并保存结果
            sorted_apis = sorted(apis)
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(sorted_apis))
            
            # 显示结果统计
            self.api_count_label.config(text=f"共提取到: {len(sorted_apis)}个API路径")
            messagebox.showinfo(
                "完成", 
                f"成功提取 {len(sorted_apis)} 个API路径\n已保存到 result.txt"
            )
            
            # 重置进度
            self.update_progress(0, "准备就绪")
            
        except Exception as e:
            messagebox.showerror("错误", f"提取过程中出错: {str(e)}")
            self.update_progress(0, "发生错误")
    
    def extract_from_file(self, file_path, pattern):
        apis = set()
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = pattern.findall(content)
                apis.update(matches)
        except Exception as e:
            print(f"无法处理文件 {file_path}: {str(e)}")
        
        return apis
    
    def update_status(self, message, color="#2c3e50"):
        self.status_label.config(text=f"状态: {message}", foreground=color)
        self.root.update()
    
    def update_progress(self, value, message):
        self.progress["value"] = value
        self.progress_percent.config(text=f"{value}%")
        self.progress_label.config(text=message)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    
    try:
        root.iconbitmap("icon.ico")  
    except:
        pass
    
    app = APIExtractorApp(root)
    root.mainloop()
