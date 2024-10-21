import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QColorDialog)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFontMetrics
from PyQt5.Qsci import QsciLexerPython
from eqsci import EQscintilla
from eqsci_panel_manager import Panel, EQsciPanelManager, PanelPosition, PanelSettings

class LineNumberPanel(Panel):
    def __init__(self, editor):
        super().__init__(editor)
        self._margin = 5
        self.setFixedWidth(40)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.lightGray)
        
        first_visible_line = self.editor.firstVisibleLine()
        visible_lines = self.editor.SendScintilla(EQscintilla.SCI_LINESONSCREEN)
        
        font_metrics = QFontMetrics(self.editor.font())
        
        for i in range(visible_lines):
            line_number = first_visible_line + i + 1
            
            position = self.editor.positionFromLineIndex(i, 0)
            y = self.editor.lineIndexFromPosition(position)[0]
            y = y * font_metrics.height()
            
            painter.setPen(Qt.black)
            painter.drawText(
                self._margin,
                y + font_metrics.ascent(),
                str(line_number)
            )
        

class ColorPreviewPanel(Panel):
    def __init__(self, editor):
        super().__init__(editor)
        self.setFixedWidth(20)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.white)
        
        text = self.editor.text()
        lines = text.split('\n')
        font_metrics = QFontMetrics(self.editor.font())
        line_height = font_metrics.height()
        
        for i, line in enumerate(lines):
            if 'QColor' in line or '#' in line:
                try:
                    if 'QColor' in line:
                        color_str = line.split('QColor')[1].split(')')[0]
                        if 'Qt.' in color_str:
                            if 'red' in color_str.lower():
                                color = QColor(Qt.red)
                            elif 'blue' in color_str.lower():
                                color = QColor(Qt.blue)
                        else:
                            rgb = [int(x) for x in color_str.strip('()').split(',')]
                            color = QColor(*rgb[:3])
                    else:
                        hex_color = line.split('#')[1][:6]
                        color = QColor(f'#{hex_color}')
                    
                    painter.fillRect(
                        2,
                        i * line_height,
                        self.width() - 4,
                        line_height - 2,
                        color
                    )
                except:
                    continue

class ToolPanel(Panel):
    def __init__(self, editor):
        super().__init__(editor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setStyleSheet("background:#222")
        
        self.add_button("Clear", self.editor.clear)
        self.add_button("Select All", self.editor.selectAll)
        self.add_button("Copy", self.editor.copy)
        self.add_button("Paste", self.editor.paste)
        
        layout.addStretch()
        self.setMinimumWidth(180)
        
    def add_button(self, text, callback):
        btn = QPushButton(text, self)
        btn.clicked.connect(callback)
        self.layout().addWidget(btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.editor = EQscintilla()
        self.setCentralWidget(self.editor)
        
        self.setup_editor()
        
        self.panel_manager = EQsciPanelManager(self.editor)
        
        self.add_panels()
        
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('QScintilla Panel Manager Example')
        
        self.load_example_code()
        
    def setup_editor(self):
        font = self.editor.font()
        font.setFamily('Consolas')
        font.setPointSize(10)
        self.editor.setFont(font)
        
        lexer = QsciLexerPython(self.editor)
        self.editor.setLexer(lexer)
        
        self.editor.setMarginType(0, EQscintilla.NumberMargin)
        self.editor.setMarginWidth(0, 0)
        self.editor.setBraceMatching(EQscintilla.SloppyBraceMatch)
        
        self.editor.setAutoIndent(True)
        
    def add_panels(self):
        line_panel = LineNumberPanel(self.editor)
        self.panel_manager.append(line_panel, PanelPosition.LEFT)
        
        color_panel = ColorPreviewPanel(self.editor)
        self.panel_manager.append(color_panel, PanelPosition.LEFT)
        
        tools = ToolPanel(self.editor)
        self.panel_manager.append(tools, PanelPosition.RIGHT)
        
    def load_example_code(self):
        example_code = '''import sys
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

background_color = QColor(240, 240, 240)
text_color = QColor(Qt.black)
selection_color = QColor(Qt.blue)
error_color = QColor(255, 0, 0)

primary_color = #007ACC
secondary_color = #5C2D91
success_color = #008000
warning_color = #FFA500

def example_function():
    x = 10
    y = 20
    return x + y

class ExampleClass:
    def __init__(self):
        self.value = 100
        
    def calculate(self):
        return self.value * 2

for i in range(20):
    print(f"Line {i}")
    if i % 2 == 0:
        print("Even number")
    else:
        print("Odd number")
'''
        self.editor.setText(example_code)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
