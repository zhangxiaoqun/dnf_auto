import sys
import json
import subprocess
import ast
import time

from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLineEdit,
    QTabWidget, QFormLayout, QComboBox, QMessageBox, QSizePolicy
)

import ctypes
from img.find_img import take_screenshot  # 导入 helper.py 文件

class Worker(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.process = None


    def run(self):
        try:
            self.process = subprocess.Popen(['python', 'main.py'],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True,
                                            encoding='utf-8')
            for stdout_line in iter(self.process.stdout.readline, ""):
                self.output_signal.emit(stdout_line)

            for stderr_line in iter(self.process.stderr.readline, ""):
                self.output_signal.emit(stderr_line)

            self.process.stdout.close()
            self.process.stderr.close()
            self.process.wait()
        except Exception as e:
            self.output_signal.emit(str(e))

    def terminate_process(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = None

    def initUI(self):
        self.setWindowTitle("dnf参数修改")
        self.setGeometry(100, 100, 2400, 1400)

        layout = QVBoxLayout()
        self.tabs = QTabWidget(self)

        # 添加 JSON 修改标签
        self.json_tab = QWidget()
        self.setup_json_tab()
        self.tabs.addTab(self.json_tab, "技能坐标修改")

        # 创建主功能标签页
        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "运行功能")

        # 创建其他变量修改标签页
        self.variable_tab = QWidget()
        self.setup_variable_tab()
        self.tabs.addTab(self.variable_tab, "修改变量")

        # 创建调用方法的标签页
        self.call_method_tab = QWidget()
        self.setup_call_method_tab()
        self.tabs.addTab(self.call_method_tab, "截图")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # 游戏窗口标签页
        self.game_tab = QWidget()
        self.setup_game_tab()
        self.tabs.addTab(self.game_tab, "游戏窗口")

    def setup_json_tab(self):
        layout = QFormLayout()

        self.key_name_mapping = {
            "joystick.center": "操纵杆中心",
            "joystick.radius": "操纵杆半径",
            "attack": "攻击",
            "Jump_Back": "后跳",
            "Jump": "跳跃",
            "Roulette": "轮盘",
            "skill1": "技能1",
            "skill2": "技能2",
            "skill3": "技能3",
            "skill4": "技能4",
            "skill5": "技能5",
            "skill6": "技能6",
            "skill7": "技能7",
            "skill8": "技能8",
            "skill9": "技能9",
            "skill10": "技能10",
            "skill11": "技能11",
            "skill12": "技能12",
            "skill13": "技能13",
            "skill14": "技能14",
            "skill15": "技能15",
            "skill16": "技能16"
        }

        self.keys = list(self.key_name_mapping.keys())
        self.key_selector = QComboBox(self)
        self.key_selector.addItems(self.key_name_mapping.values())

        self.json_value_input = QLineEdit(self)
        self.json_value_input.setPlaceholderText("输入新值（格式: [值1, 值2]）")

        get_value_button = QPushButton("获取当前值", self)
        get_value_button.clicked.connect(self.get_current_value)

        modify_button = QPushButton("修改 JSON 值", self)
        modify_button.clicked.connect(self.modify_json_value)

        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)

        layout.addRow("选择键:", self.key_selector)
        layout.addRow("输入新值:", self.json_value_input)
        layout.addRow(get_value_button)
        layout.addRow(modify_button)
        layout.addRow(self.textEdit)

        self.json_tab.setLayout(layout)

    def setup_call_method_tab(self):
        layout = QVBoxLayout()

        call_method_button = QPushButton("点击截图", self)
        call_method_button.clicked.connect(self.screenshot)

        self.method_output_text = QTextEdit(self)
        self.method_output_text.setReadOnly(True)

        layout.addWidget(call_method_button)
        layout.addWidget(self.method_output_text)

        self.call_method_tab.setLayout(layout)

    def screenshot(self):
        try:
            result = take_screenshot()
            self.method_output_text.append(result)
        except Exception as e:
            self.method_output_text.append(f"调用方法时出错: {str(e)}")

    def setup_main_tab(self):
        layout = QVBoxLayout()

        run_main_button = QPushButton("运行主文件", self)
        run_main_button.clicked.connect(self.run_main_file)

        terminate_button = QPushButton("终止线程", self)
        terminate_button.clicked.connect(self.terminate_worker)

        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)

        layout.addWidget(run_main_button)
        layout.addWidget(terminate_button)
        layout.addWidget(self.output_text)

        self.main_tab.setLayout(layout)

    def setup_variable_tab(self):
        layout = QFormLayout()

        self.variable_name_mapping = {
            "hero_num": "英雄数量",
            "pl_300_message_num": "300 消息数量",
            "combat_start": "战斗开始"
        }

        self.variable_name_selector = QComboBox(self)
        self.variable_name_selector.addItems(self.variable_name_mapping.values())

        self.variable_value_input = QLineEdit(self)
        self.variable_value_input.setPlaceholderText("输入新变量值（例如: 10）")

        modify_variable_button = QPushButton("修改变量", self)
        modify_variable_button.clicked.connect(self.modify_variable)

        self.variable_output_text = QTextEdit(self)
        self.variable_output_text.setReadOnly(True)

        layout.addRow("选择变量:", self.variable_name_selector)
        layout.addRow("新变量值:", self.variable_value_input)
        layout.addRow(modify_variable_button)
        layout.addRow(self.variable_output_text)

        # 添加角色字典
        self.role_dic_value_input = QLineEdit(self)
        self.role_dic_value_input.setPlaceholderText("输入新角色字典（例如: {1:'新角色'}）")

        modify_role_dic_button = QPushButton("修改角色字典", self)
        modify_role_dic_button.clicked.connect(self.modify_role_dic)

        self.role_dic_output_text = QTextEdit(self)
        self.role_dic_output_text.setReadOnly(True)

        layout.addRow("输入新角色字典:", self.role_dic_value_input)
        layout.addRow(modify_role_dic_button)
        layout.addRow(self.role_dic_output_text)

        # 添加角色顺序坐标
        self.role_seq_coord_value_input = QLineEdit(self)
        self.role_seq_coord_value_input.setPlaceholderText("输入新角色顺序坐标（例如: {'role_index1': [100, 200]}）")

        modify_role_seq_coord_button = QPushButton("修改角色顺序坐标", self)
        modify_role_seq_coord_button.clicked.connect(self.modify_role_seq_coord)

        self.role_seq_coord_output_text = QTextEdit(self)
        self.role_seq_coord_output_text.setReadOnly(True)

        layout.addRow("输入新角色顺序坐标:", self.role_seq_coord_value_input)
        layout.addRow(modify_role_seq_coord_button)
        layout.addRow(self.role_seq_coord_output_text)

        self.variable_tab.setLayout(layout)

    def get_current_value(self):
        json_file_path = 'data.json'
        key = self.keys[self.key_selector.currentIndex()]

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            current_value = self.get_nested_value(data, key)
            msg = f"当前 '{key}' 的值为: '{current_value}'"
            print(msg)
            self.textEdit.append(msg)
            self.json_value_input.setText(str(current_value))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取 JSON 值时出错：\n{str(e)}")

    def get_nested_value(self, data, key):
        keys = key.split('.')
        for k in keys:
            data = data[k]
        return data

    def modify_json_value(self):
        json_file_path = 'data.json'
        key = self.keys[self.key_selector.currentIndex()]
        new_value = self.json_value_input.text()

        try:
            if new_value.startswith('[') and new_value.endswith(']'):
                new_value = json.loads(new_value)
            else:
                raise ValueError("输入格式错误，需为列表格式，例如 [2096, 968]")

            if not isinstance(new_value, list):
                raise ValueError("新值必须为一个列表。")

            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            keys = key.split('.')
            if len(keys) > 1:
                nested_key = keys[-1]
                parent_key = keys[:-1]

                parent_data = data
                for k in parent_key:
                    parent_data = parent_data[k]

                parent_data[nested_key] = new_value
            else:
                data[key] = new_value

            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            msg = f"已将 '{key}' 修改为 '{new_value}'"
            print(msg)
            self.textEdit.append(msg)

        except ValueError as ve:
            QMessageBox.critical(self, "错误", f"输入格式错误：\n{str(ve)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改 JSON 时出错：\n{str(e)}")

    def run_main_file(self):
        self.worker = Worker()
        self.worker.output_signal.connect(self.output_text.append)
        self.worker.start()

    def terminate_worker(self):
        if self.worker:
            self.worker.terminate_process()
            self.worker.quit()
            self.worker.wait()
            self.worker = None

            self.output_text.append("工作线程已终止。")
        else:
            self.output_text.append("没有运行中的线程。")

    def closeEvent(self, event):
        if self.worker:
            self.worker.terminate_process()
            self.worker.quit()
            self.worker.wait()

        event.accept()

    def modify_variable(self):
        shared_file_path = 'shared_variables.py'
        variable_name = list(self.variable_name_mapping.keys())[self.variable_name_selector.currentIndex()]
        new_value = self.variable_value_input.text()

        try:
            with open(shared_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith(variable_name + " = "):
                    try:
                        parsed_value = ast.literal_eval(new_value)
                        lines[i] = f"{variable_name} = {repr(parsed_value)}\n"
                    except Exception as e:
                        raise ValueError(f"无效的新值：{new_value}") from e
                    break
            else:
                raise ValueError("未找到指定变量。")

            with open(shared_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            msg = f"变量 '{variable_name}' 已修改为 '{new_value}'"
            print(msg)
            self.variable_output_text.append(msg)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改变量时出错：\n{str(e)}")

    def modify_role_dic(self):
        shared_file_path = 'shared_variables.py'
        new_value = self.role_dic_value_input.text()

        try:
            with open(shared_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith("role_dic = "):
                    try:
                        parsed_value = ast.literal_eval(new_value)
                        if not isinstance(parsed_value, dict):
                            raise ValueError("角色字典必须是字典格式。")
                        lines[i] = f"role_dic = {repr(parsed_value)}\n"
                    except Exception as e:
                        raise ValueError(f"无效的新角色字典：{new_value}") from e
                    break
            else:
                raise ValueError("未找到角色字典变量。")

            with open(shared_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            msg = f"角色字典已修改为 '{new_value}'"
            print(msg)
            self.role_dic_output_text.append(msg)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改角色字典时出错：\n{str(e)}")

    def modify_role_seq_coord(self):
        shared_file_path = 'shared_variables.py'
        new_value = self.role_seq_coord_value_input.text()

        try:
            with open(shared_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith("role_seq_coord = "):
                    try:
                        parsed_value = ast.literal_eval(new_value)
                        if not isinstance(parsed_value, dict):
                            raise ValueError("角色顺序坐标必须是字典格式。")
                        lines[i] = f"role_seq_coord = {repr(parsed_value)}\n"
                    except Exception as e:
                        raise ValueError(f"无效的新角色顺序坐标：{new_value}") from e
                    break
            else:
                raise ValueError("未找到角色顺序坐标变量。")

            with open(shared_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            msg = f"角色顺序坐标已修改为 '{new_value}'"
            print(msg)
            self.role_seq_coord_output_text.append(msg)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改角色顺序坐标时出错：\n{str(e)}")

    def setup_game_tab(self):
        layout = QVBoxLayout()

        game_handle = self.get_game_window_handle()

        if game_handle:
            # 创建 QWidget 作为容器
            game_widget = QWidget(self)
            layout.addWidget(game_widget)

            # 设置 QWidget 的几何和样式
            game_widget.setGeometry(0, 0, 800, 600)  # 根据需要设置尺寸
            game_widget.setAttribute(Qt.WA_NativeWindow)

            # 获取窗口ID
            game_widget_id = int(game_widget.winId())  # 将 Qt 窗口 ID 转换为整数

            # 打印调试信息
            print(f"游戏窗口ID: {game_widget_id}, 游戏句柄: {game_handle}")  # 调试信息

            # 将窗口句柄转换为 CTYPES 的句柄类型
            handle = ctypes.c_void_p(game_handle)  # 游戏窗口句柄
            widget_id = ctypes.c_void_p(game_widget_id)  # Qt 窗口句柄

            # 设置游戏窗口为父窗口
            result = ctypes.windll.user32.SetParent(handle, widget_id)
            if result == 0:  # 返回值为0表示设置失败
                print(f"SetParent 失败: {ctypes.GetLastError()}")

        else:
            layout.addWidget(QTextEdit("未能找到游戏窗口。"))

        self.game_tab.setLayout(layout)

    def get_game_window_handle(self):
        time.sleep(5)
        # 获取游戏窗口句柄，假设窗口标题为 "游戏窗口标题"
        # hwnd = ctypes.windll.user32.FindWindowW(None, "image")  # 替换为实际窗口标题
        hwnd = ctypes.windll.user32.FindWindowW(None, "Oopz")  # 替换为实际窗口标题
        if hwnd:
            print(f"找到游戏窗口，句柄: {hwnd}")  # 调试信息
        else:
            print("未找到游戏窗口")  # 调试信息
        return hwnd if hwnd else None
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
