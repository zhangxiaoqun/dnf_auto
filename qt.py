import sys
import json
import subprocess
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
        self.setWindowTitle("JSON 修改器")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.tabs = QTabWidget(self)

        # 添加两个标签，一个用于 JSON 修改，另一个用于主功能
        self.json_tab = QWidget()
        self.setup_json_tab()
        self.tabs.addTab(self.json_tab, "JSON 修改")

        # 创建主功能标签页
        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "主功能")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def setup_json_tab(self):
        layout = QFormLayout()

        # 显示名称到实际键名的映射字典
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

        # 添加运行主文件的按钮
        run_main_button = QPushButton("运行主文件", self)
        run_main_button.clicked.connect(self.run_main_file)

        # 添加输出区域
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)

        layout.addWidget(run_main_button)
        layout.addWidget(self.output_text)

        self.main_tab.setLayout(layout)

    def get_current_value(self):
        json_file_path = 'data.json'  # 你的 JSON 文件路径
        key = self.keys[self.key_selector.currentIndex()]

        try:
            # 读取 JSON 文件
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # 根据键获取当前值
            current_value = self.get_nested_value(data, key)
            msg = f"当前 '{key}' 的值为: '{current_value}'"
            print(msg)  # 控制台输出
            self.textEdit.append(msg)  # 图形界面输出
            self.json_value_input.setText(str(current_value))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取 JSON 值时出错：\n{str(e)}")

    def get_nested_value(self, data, key):
        """ 获取嵌套 JSON 对象中的值 """
        keys = key.split('.')  # 按点分割键
        for k in keys:
            data = data[k]  # 逐层访问
        return data

    def modify_json_value(self):
        json_file_path = 'data.json'  # 你的 JSON 文件路径
        key = self.keys[self.key_selector.currentIndex()]
        new_value = self.json_value_input.text()

        try:
            # 尝试将新值转换为列表
            if new_value.startswith('[') and new_value.endswith(']'):
                new_value = json.loads(new_value)  # 将字符串转换为列表
            else:
                raise ValueError("输入格式错误，需为列表格式，例如 [2096, 968]")

            if not isinstance(new_value, list):
                raise ValueError("新值必须为一个列表。")

            # 读取 JSON 文件
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # 修改嵌套值
            keys = key.split('.')
            if len(keys) > 1:
                # 如果是嵌套结构，处理嵌套
                nested_key = keys[-1]
                parent_key = keys[:-1]

                parent_data = data
                for k in parent_key:
                    parent_data = parent_data[k]  # 找到父级

                parent_data[nested_key] = new_value

            else:
                # 处理非嵌套值
                data[key] = new_value

            # 写回 JSON 文件
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
            # 显示主文件的输出
            self.output_text.setPlainText(result.stdout + result.stderr)
        except subprocess.CalledProcessError as e:
            self.output_text.setPlainText(e.stdout + e.stderr)  # 显示错误信息


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
