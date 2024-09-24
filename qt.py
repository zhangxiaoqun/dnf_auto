import sys
import json
import subprocess
import ast
import time

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLineEdit,
    QTabWidget, QFormLayout, QComboBox, QMessageBox, QGridLayout
)
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout,
                             QPushButton, QLineEdit, QTextEdit, QMessageBox, QLabel)
import ctypes
from img.find_img import take_screenshot  # 导入帮助函数

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
        self.json_file_path = 'hero/hero_skill/common_skill.json'  # 设置要修改的 JSON 文件路径
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DNF参数修改")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.tabs = QTabWidget(self)

        # 添加 JSON 修改标签
        self.skill_coord_tab = QWidget()
        self.setup_skill_coord_tab()
        # layout.addWidget(self.skill_coord_tab, "技能坐标修改")
        self.tabs.addTab(self.skill_coord_tab, "技能坐标修改")

        # 创建主功能标签页
        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "运行功能")

        # 创建变量修改标签页
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

    def setup_skill_coord_tab(self):
        layout = QGridLayout()
        layout.setSpacing(10)

        self.key_name_mapping = {
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

        self.skill_coords = {}
        self.load_json_data()  # 加载 JSON 数据

        row = 0
        col = 0

        for skill_key, skill_name in self.key_name_mapping.items():
            x_input = QLineEdit(self)
            y_input = QLineEdit(self)
            x_input.setPlaceholderText("输入 X 坐标")
            y_input.setPlaceholderText("输入 Y 坐标")

            # 注释掉 QIntValidator，允许输入字母和数字
            # x_input.setValidator(QIntValidator())
            # y_input.setValidator(QIntValidator())

            if skill_key in self.skill_data:
                coords = self.skill_data[skill_key]
                if isinstance(coords, list) and len(coords) >= 2:
                    x_input.setText(str(coords[0]))
                    y_input.setText(str(coords[1]))

            self.skill_coords[skill_key] = (x_input, y_input)

            layout.addWidget(QLabel(skill_name), row, col)
            layout.addWidget(x_input, row, col + 1)
            layout.addWidget(y_input, row, col + 2)

            col += 3  # 每个技能占三列
            if col >= 6:  # 如果超过两列则换行
                col = 0
                row += 1

        self.modify_skills_button = QPushButton("修改技能坐标", self)
        self.modify_skills_button.clicked.connect(self.modify_skill_coords)

        layout.addWidget(self.modify_skills_button, row + 1, 0, 1, 3)  # 按钮放在底部
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text, row + 2, 0, 1, 3)  # 输出框放在按钮下

        self.skill_coord_tab.setLayout(layout)

    def load_json_data(self):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.skill_data = json.load(file)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载 JSON 数据时出错：\n{str(e)}")

    def modify_skill_coords(self):
        skill_coords = {}
        valid_input = True

        for skill_key, (x_input, y_input) in self.skill_coords.items():
            x = x_input.text().strip()  # 去掉前后空格
            y = y_input.text().strip()

            print(f"Debug: {skill_key} - X: '{x}', Y: '{y}'")  # 调试输出

            # 判断输入并分别处理
            if x.isdigit() and y.isdigit():
                skill_coords[skill_key] = [int(x), int(y)]
            elif x == '' or y == '':
                valid_input = False
                QMessageBox.critical(self, "错误", f"{self.key_name_mapping[skill_key]} 的坐标输入无效！X 和 Y 不能为空。")
                break
            else:
                skill_coords[skill_key] = [x, y]  # 如果是字母，直接存储字符串

        if valid_input:
            # 保存修改到 JSON 文件
            try:
                for key, coords in skill_coords.items():
                    self.skill_data[key] = coords

                with open(self.json_file_path, 'w', encoding='utf-8') as file:
                    json.dump(self.skill_data, file, ensure_ascii=False, indent=4)

                self.output_text.clear()
                for skill_key, coords in skill_coords.items():
                    self.output_text.append(f"{self.key_name_mapping[skill_key]} 坐标已修改为: X = {coords[0]}, Y = {coords[1]}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存 JSON 数据时出错：\n{str(e)}")





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

        # 角色字典输入
        self.role_dict_grid = QGridLayout()
        self.role_dict_inputs = []

        self.add_role_dict_button = QPushButton("添加角色字典输入框", self)
        self.add_role_dict_button.clicked.connect(self.add_role_dict_input)

        modify_role_dict_button = QPushButton("修改角色字典", self)
        modify_role_dict_button.clicked.connect(self.modify_role_dict)

        self.role_dict_output_text = QTextEdit(self)
        self.role_dict_output_text.setReadOnly(True)

        layout.addRow(self.add_role_dict_button)
        layout.addRow(modify_role_dict_button)  # 添加修改按钮
        layout.addRow(self.role_dict_output_text)

        layout.addRow(self.role_dict_grid)


        # 角色坐标顺序（固定的）
        self.role_seq_coord = {
            "role_index1": [202, 177],
            "role_index2": [201, 298],
            "role_index3": [205, 420],
            "role_index4": [196, 532]
        }

        self.role_seq_inputs = {}
        for role, coord in self.role_seq_coord.items():
            x_input = QLineEdit(self)
            y_input = QLineEdit(self)
            x_input.setText(str(coord[0]))  # 设置 X 坐标初始值
            y_input.setText(str(coord[1]))  # 设置 Y 坐标初始值
            self.role_seq_inputs[role] = (x_input, y_input)

            layout.addRow(f"{role} X 坐标:", x_input)
            layout.addRow(f"{role} Y 坐标:", y_input)

        modify_role_seq_button = QPushButton("修改角色顺序坐标", self)
        modify_role_seq_button.clicked.connect(self.modify_role_seq_coord)
        layout.addRow(modify_role_seq_button)

        self.role_seq_output_text = QTextEdit(self)
        self.role_seq_output_text.setReadOnly(True)
        layout.addRow(self.role_seq_output_text)

        self.variable_tab.setLayout(layout)


    def add_role_dict_input(self):
        row = len(self.role_dict_inputs)
        key_input = QLineEdit(self)
        key_input.setPlaceholderText("输入角色键")
        value_input = QLineEdit(self)
        value_input.setPlaceholderText("输入角色值")

        self.role_dict_inputs.append((key_input, value_input))
        self.role_dict_grid.addWidget(key_input, row // 3, 2 * (row % 3))  # 键
        self.role_dict_grid.addWidget(value_input, row // 3, 2 * (row % 3) + 1)  # 值

    def add_role_seq_input(self):
        row = len(self.role_seq_inputs)
        key_input = QLineEdit(self)
        key_input.setPlaceholderText("输入角色坐标键")
        x_input = QLineEdit(self)
        x_input.setPlaceholderText("输入 X 坐标")
        y_input = QLineEdit(self)
        y_input.setPlaceholderText("输入 Y 坐标")

        self.role_seq_inputs.append((key_input, x_input, y_input))
        self.role_seq_grid.addWidget(key_input, row // 3, 3 * (row % 3))  # 键
        self.role_seq_grid.addWidget(x_input, row // 3, 3 * (row % 3) + 1)  # X坐标
        self.role_seq_grid.addWidget(y_input, row // 3, 3 * (row % 3) + 2)  # Y坐标

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

    def modify_role_dict(self):
        shared_file_path = 'shared_variables.py'
        role_dict = {}

        for key_input, value_input in self.role_dict_inputs:
            key = key_input.text()
            value = value_input.text()
            if key.isdigit() and value:  # 确保键为数字，值不能为空
                role_dict[int(key)] = value  # 将键转换为 int

        # 保存角色字典到 shared_variables.py
        try:
            with open(shared_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith("role_dic = "):  # 这里需要确保变量名是 role_dic
                    lines[i] = f"role_dic = {repr(role_dict)}\n"
                    break
            else:
                raise ValueError("未找到角色字典变量。")

            with open(shared_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            msg = f"角色字典已修改为 '{role_dict}'"
            print(msg)
            self.role_dict_output_text.append(msg)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改角色字典时出错：\n{str(e)}")

    def modify_role_seq_coord(self):
        shared_file_path = 'shared_variables.py'  # 替换为实际文件路径
        role_seq_coord = {}

        for role, (x_input, y_input) in self.role_seq_inputs.items():
            x = x_input.text()
            y = y_input.text()
            if x.isdigit() and y.isdigit():
                role_seq_coord[role] = [int(x), int(y)]

        # 保存角色顺序坐标到 shared_variables.py
        try:
            with open(shared_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith("role_seq_coord = "):
                    lines[i] = f"role_seq_coord = {repr(role_seq_coord)}\n"
                    break
            else:
                raise ValueError("未找到角色顺序坐标变量。")

            with open(shared_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            msg = f"角色顺序坐标已修改为 '{role_seq_coord}'"
            print(msg)
            self.role_seq_output_text.append(msg)


        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改角色顺序坐标时出错：\n{str(e)}")

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

    def setup_game_tab(self):
        layout = QVBoxLayout()
        game_handle = self.get_game_window_handle()

        if game_handle:
            game_widget = QWidget(self)
            layout.addWidget(game_widget)

            game_widget.setGeometry(0, 0, 800, 600)  # 根据需要设置尺寸
            game_widget.setAttribute(Qt.WA_NativeWindow)

            game_widget_id = int(game_widget.winId())  # 获取窗口 ID

            print(f"游戏窗口ID: {game_widget_id}, 游戏句柄: {game_handle}")  # 调试信息

            handle = ctypes.c_void_p(game_handle)  # 游戏窗口句柄
            widget_id = ctypes.c_void_p(game_widget_id)  # Qt 窗口句柄

            result = ctypes.windll.user32.SetParent(handle, widget_id)
            if result == 0:
                print(f"SetParent 失败: {ctypes.GetLastError()}")

        else:
            layout.addWidget(QTextEdit("未能找到游戏窗口。"))

        self.game_tab.setLayout(layout)

    def get_game_window_handle(self):
        time.sleep(5)
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
