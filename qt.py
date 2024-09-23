import sys
import json
import subprocess
import ast
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLineEdit,
    QTabWidget, QFormLayout, QComboBox, QMessageBox
)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("数据修改器")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.tabs = QTabWidget(self)

        # 添加 JSON 修改标签
        self.json_tab = QWidget()
        self.setup_json_tab()
        self.tabs.addTab(self.json_tab, "JSON 修改")

        # 创建主功能标签页
        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "主功能")

        # 创建变量修改标签页
        self.variable_tab = QWidget()
        self.setup_variable_tab()
        self.tabs.addTab(self.variable_tab, "修改共享变量")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

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

    def setup_main_tab(self):
        layout = QVBoxLayout()

        run_main_button = QPushButton("运行主文件", self)
        run_main_button.clicked.connect(self.run_main_file)

        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)

        layout.addWidget(run_main_button)
        layout.addWidget(self.output_text)

        self.main_tab.setLayout(layout)

    def setup_variable_tab(self):
        layout = QFormLayout()

        # 显示名称和实际变量名的映射
        self.variable_name_mapping = {
            "hero_num": "英雄数量",
            "pl_300_message_num": "300 消息数量",
            "combat_start": "战斗开始",
            "role_dic": "角色字典",
            "role_seq_coord": "角色顺序坐标"
        }

        self.variable_name_selector = QComboBox(self)
        self.variable_name_selector.addItems(self.variable_name_mapping.values())

        self.variable_value_input = QLineEdit(self)
        self.variable_value_input.setPlaceholderText("输入新变量值（如: hero_num输入：1,pl_300_message_num:输入0")

        modify_variable_button = QPushButton("修改变量", self)
        modify_variable_button.clicked.connect(self.modify_variable)

        self.variable_output_text = QTextEdit(self)
        self.variable_output_text.setReadOnly(True)

        layout.addRow("选择变量:", self.variable_name_selector)
        layout.addRow("新变量值:", self.variable_value_input)
        layout.addRow(modify_variable_button)
        layout.addRow(self.variable_output_text)

        # 添加分隔线
        layout.addRow(QPushButton("----------------------------------------------------"))

        # 添加角色字典和顺序坐标的独立修改
        self.role_dic_input = QLineEdit(self)
        self.role_dic_input.setPlaceholderText("输入角色字典新值（格式: {1: '新值'}）")

        modify_role_dic_button = QPushButton("修改角色字典", self)
        modify_role_dic_button.clicked.connect(self.modify_role_dic)

        self.role_seq_coord_input = QLineEdit(self)
        self.role_seq_coord_input.setPlaceholderText("输入角色顺序坐标新值（格式: {'role_index1': [x, y]}）")

        modify_role_seq_coord_button = QPushButton("修改角色顺序坐标", self)
        modify_role_seq_coord_button.clicked.connect(self.modify_role_seq_coord)

        layout.addRow("角色字典新值:", self.role_dic_input)
        layout.addRow(modify_role_dic_button)
        layout.addRow("角色顺序坐标新值:", self.role_seq_coord_input)
        layout.addRow(modify_role_seq_coord_button)

        self.variable_tab.setLayout(layout)

    def get_current_value(self):
        json_file_path = 'data.json'  # 你的 JSON 文件路径
        key = self.keys[self.key_selector.currentIndex()]

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            current_value = self.get_nested_value(data, key)
            msg = f"当前 '{key}' 的值为: '{current_value}'"
            print(msg)  # 控制台输出
            self.textEdit.append(msg)  # 图形界面输出
            self.json_value_input.setText(str(current_value))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取 JSON 值时出错：\n{str(e)}")

    def get_nested_value(self, data, key):
        keys = key.split('.')  # 按点分割键
        for k in keys:
            data = data[k]  # 逐层访问
        return data

    def modify_json_value(self):
        json_file_path = 'data.json'  # 你的 JSON 文件路径
        key = self.keys[self.key_selector.currentIndex()]
        new_value = self.json_value_input.text()

        try:
            if new_value.startswith('[') and new_value.endswith(']'):
                new_value = json.loads(new_value)  # 将字符串转换为列表
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
                    parent_data = parent_data[k]  # 找到父级

                parent_data[nested_key] = new_value

            else:
                data[key] = new_value

            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            msg = f"已将 '{key}' 修改为 '{new_value}'"
            print(msg)  # 控制台输出
            self.textEdit.append(msg)  # 图形界面输出

        except ValueError as ve:
            QMessageBox.critical(self, "错误", f"输入格式错误：\n{str(ve)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改 JSON 时出错：\n{str(e)}")

    def run_main_file(self):
        """ 执行主文件，并获取输出 """
        try:
            result = subprocess.run(['python', 'main.py'], capture_output=True, text=True, check=True)
            self.output_text.setPlainText(result.stdout + result.stderr)
        except subprocess.CalledProcessError as e:
            self.output_text.setPlainText(e.stdout + e.stderr)  # 显示错误信息

    def modify_variable(self):
        """ 修改 shared_variables.py 中的指定变量值 """
        shared_file_path = 'shared_variables.py'  # 指定要修改的共享变量文件
        # 获取选择的变量的真实名称
        variable_name = list(self.variable_name_mapping.keys())[self.variable_name_selector.currentIndex()]
        new_value = self.variable_value_input.text()

        try:
            # 读取当前的变量
            with open(shared_file_path, 'r') as file:
                lines = file.readlines()

            # 查找变量并修改
            for i, line in enumerate(lines):
                if line.startswith(variable_name + " = "):
                    # 尝试将新值解析为 Python 变量
                    try:
                        # 安全地评估新值
                        parsed_value = ast.literal_eval(new_value)
                        lines[i] = f"{variable_name} = {repr(parsed_value)}\n"
                    except Exception as e:
                        raise ValueError(f"无效的新值：{new_value}") from e
                    break
            else:
                raise ValueError("未找到指定变量。")

            # 将修改后的内容写回文件
            with open(shared_file_path, 'w') as file:
                file.writelines(lines)

            msg = f"变量 '{variable_name}' 已修改为 '{new_value}'"
            print(msg)  # 控制台输出
            self.variable_output_text.append(msg)  # 图形界面输出

        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改变量时出错：\n{str(e)}")

    def modify_role_dic(self):
        """ 修改角色字典 """
        shared_file_path = 'shared_variables.py'
        new_value = self.role_dic_input.text()

        try:
            with open(shared_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # 查找 role_dic 变量并修改
            for i, line in enumerate(lines):
                if line.startswith("role_dic = "):
                    parsed_value = ast.literal_eval(new_value)  # 安全解析新值
                    lines[i] = f"role_dic = {repr(parsed_value)}\n"
                    break
            else:
                raise ValueError("未找到 role_dic 变量。")

            with open(shared_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            msg = f"角色字典已修改为 '{new_value}'"
            print(msg)  # 控制台输出
            self.variable_output_text.append(msg)  # 图形界面输出

        except Exception as e:
            QMessageBox.critical(self, "错误", "请按照格式修改 例如：{1:'夏末', 2:'别拽了俺脱'}")

    def modify_role_seq_coord(self):
        """ 修改角色顺序坐标 """
        shared_file_path = 'shared_variables.py'
        new_value = self.role_seq_coord_input.text()

        try:
            with open(shared_file_path, 'r') as file:
                lines = file.readlines()

            # 查找 role_seq_coord 变量并修改
            for i, line in enumerate(lines):
                if line.startswith("role_seq_coord = "):
                    parsed_value = ast.literal_eval(new_value)  # 安全解析新值
                    lines[i] = f"role_seq_coord = {repr(parsed_value)}\n"
                    break
            else:
                raise ValueError("未找到 role_seq_coord 变量。")

            with open(shared_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            msg = f"角色顺序坐标已修改为 '{new_value}'"
            print(msg)  # 控制台输出
            self.variable_output_text.append(msg)  # 图形界面输出

        except Exception as e:
            QMessageBox.critical(self, "错误", "请按照格式修改 例如：'{role_index1': [202, 177],'role_index2': [201, 298],'role_index3': [205, 420],'role_index4': [196, 532]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
