from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QWidget
from opencc import OpenCC
import requests
import json
import re

# 定义转换数字为中文的函数
def num2zh(number):
    num_dict = {'0':'零','1':'一','2':'二','3':'三','4':'四','5':'五','6':'六','7':'七','8':'八','9':'九'}
    zh_number = ''.join([num_dict[i] for i in number])
    return zh_number

# 定义转换字母为位置的函数
def abc2loc(abc):
    abc_dict = {'a':'上','b':'中','c':'下'}
    return abc_dict.get(abc, '')

# 创建一个空字典来存储代码和略稱的映射
mapping_dict = {
    "A": "趙城金藏",
    "AC": "趙城金藏",
    "B": "大藏經補編",
    "C": "中華藏",
    "CC": "CBETA 選集",
    "D": "國圖善本佛典",
    "F": "房山石經",
    "G": "佛教大藏經",
    "GA": "佛寺志彙刊",
    "GB": "佛寺志叢刊",
    "GJ": "福州藏",
    "I": "北朝佛拓百品",
    "J": "嘉興藏",
    "JC": "嘉興藏",
    "JT": "嘉興藏",
    "K": "高麗藏",
    "L": "乾隆藏、清藏、龍藏",
    "LC": "呂澂著作集",
    "M": "卍正藏",
    "N": "南傳大藏經",
    "P": "永樂北藏",
    "PN": "普寧藏",
    "Q": "磧砂藏",
    "QC": "磧砂藏",
    "R": "卍續藏",
    "S": "宋藏遺珍",
    "SS": "縮刷藏、縮刻藏、縮藏、弘教本、弘教藏",
    "SX": "思溪藏",
    "SZ": "思溪藏",
    "T": "大正藏",
    "TX": "太虛大師集",
    "TW": "大正藏",
    "U": "洪武南藏",
    "X": "新纂卍續藏",
    "Y": "印順法師集",
    "Z": "卍續藏",
    "ZS": "正史佛教資料",
    "ZW": "藏外佛教文獻"
}


# 定义获取脚注的函数
def get_footnote(zh_text_traditional):
    url = "https://cbdata.dila.edu.tw/stable/sphinx/all_in_one"
    params = {
        'q': zh_text_traditional,  # 搜索词
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return ""
    
    data = response.json()
    print(data)
    if not data['results']:
        print("没有找到相关结果。")
        return ""

    footnotes = []  # 创建一个列表来存储所有脚注
    id = 0
    for result in data['results']:
        # 解析卷和页码信息
        id += 1
        
        
        vol_match = re.search(r"(\d+)", result['file'])
        vol = int(vol_match.group(0))
        
        page_match = re.search(r'(.*?)([a-zA-Z])(.*)', result['kwics']['results'][0]['lb'])
        page = page_match.group(1) if page_match else ""
        page = int(page)
        locate = abc2loc(page_match.group(2)) if page_match else ""
        
        footnote = f"{result['byline']}:《{result['title']}》卷{num2zh(str(result['juan']))},《{mapping_dict[result['canon']]}》第{str(vol)}册，第{str(page)}页{locate}。"
        #print(footnote)
        footnotes.append(footnote)
    return footnotes



class FootnoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('清言')
        self.setGeometry(100, 100, 600, 600)

        # 创建布局
        layout = QVBoxLayout()

        # 创建文本输入框
        self.input_box = QLineEdit(self)
        layout.addWidget(self.input_box)

        # 创建按钮，并连接到槽函数
        self.button = QPushButton('生成脚注', self)
        self.button.clicked.connect(self.generate_footnote)
        layout.addWidget(self.button)

        # 创建文本输出框
        self.output_box = QTextEdit(self)
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box)

        # 设置中心窗口的布局
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def generate_footnote(self):
        # 获取用户输入的文本
        zh_text = self.input_box.text()

        # 转换文本并获取脚注
        cc = OpenCC('s2t')
        zh_text_traditional = cc.convert(zh_text)
        footnotes = get_footnote(zh_text_traditional)
        # 如果有脚注，则显示
        if footnotes:
            cc = OpenCC('t2s')
            self.output_box.setPlainText("")  # 清空现有的文本输出
            for i, footnote in enumerate(footnotes, start=1):
                formatted_footnote = f"{i}. {footnote}\n\n"
                formatted_footnote = cc.convert(formatted_footnote)
                self.output_box.setPlainText(self.output_box.toPlainText() + formatted_footnote)
        else:
            self.output_box.setPlainText("没有找到相关结果。")



if __name__ == '__main__':
    app = QApplication([])
    window = FootnoteApp()
    window.show()
    app.exec_()
