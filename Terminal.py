import sys
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QPixmap, QPalette, QTextCursor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog, QMessageBox, QHBoxLayout, QTextEdit, QLineEdit


#Main class
class Terminal(QMainWindow):

#Init
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_terminal()


#UI
    def setup_ui(self):

#Buttons
        self.clear_button = QPushButton("🗑️")
        self.clear_button.setFixedSize(20, 20)
        self.clear_button.setToolTip("Clear Terminal")
        self.background_button = QPushButton("🎨")
        self.background_button.setFixedSize(20, 20) 
        self.background_button.setToolTip("Switch Background")

#Terminal output
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)

#Terminal input
        self.terminal_input = QLineEdit()
        self.terminal_input.setPlaceholderText("Hack here...")

#Terminal font        
        font = QFont("Consolas", 12)
        self.terminal_output.setFont(font)
        self.terminal_input.setFont(font)

#Layouts
        top_layout = QHBoxLayout()
        top_layout.addStretch()  
        top_layout.addWidget(self.background_button)
        top_layout.addWidget(self.clear_button)
        terminal_layout = QVBoxLayout()
        terminal_layout.addWidget(self.terminal_output)
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel(">_"))
        input_layout.addWidget(self.terminal_input)
        terminal_layout.addLayout(input_layout)
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)  
        main_layout.addLayout(terminal_layout)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  
        main_layout.setSpacing(7) 

#Window
        self.container = QWidget()
        self.container.setLayout(main_layout)
        self.setWindowTitle("Terminal")
        self.setGeometry(100, 100, 700, 350)
        self.setCentralWidget(self.container)
        
#Connect signals        
        self.terminal_input.returnPressed.connect(self.execute_command)
        self.clear_button.clicked.connect(self.clear_terminal)
        self.background_button.clicked.connect(self.switch_background)
        

#Process
    def setup_terminal(self):
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        if sys.platform == "win32":
            self.process.start("powershell", ["-NoExit", "-Command", "prompt 'PS $($pwd.Path)> '"]) 
        else:
            self.process.start("bash")    
 

#Backgrounds handler
    def switch_background(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select an image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if not file_path:  
            return
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Error", "Failed to load the image file.")
                return
            
            self.container.setStyleSheet(f"""
                QWidget {{
                    background-image: url({file_path});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                }}
                QLabel {{
                    background: transparent;
                    color: white;
                    font-weight: bold;
                    font-size: 20pt;
                }}
                QTextEdit, QLineEdit {{
                    background: rgba(0, 0, 0, 120);
                    color: #00ff7f;
                    border: 1px solid rgba(255, 255, 255, 80);
                    border-radius: 3px;
                    font-family: Consolas, monospace;
                }}
            """)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set background:\n{e}")


#Commands Handler
    def execute_command(self):
        command = self.terminal_input.text()
        if command.strip():
            self.terminal_input.clear()
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.write(f"{command}\n".encode()) 
            else:
                self.terminal_output.append("Terminal process not running")


#Output handler
    def handle_stdout(self):
        try:
            data = self.process.readAllStandardOutput().data()
            try:
                decoded_data = data.decode('utf-8')
            except UnicodeDecodeError:
                decoded_data = data.decode('latin-1', errors='replace')
            self.terminal_output.append(decoded_data)
            self.scroll_to_bottom()
        except Exception as e:
            self.terminal_output.append(f"Error reading output: {str(e)}")


#Errors handler
    def handle_stderr(self):
        try:
            data = self.process.readAllStandardError().data()
            try:
                decoded_data = data.decode('utf-8')
            except UnicodeDecodeError:
                decoded_data = data.decode('latin-1', errors='replace')
            self.terminal_output.append(f"<span style='color: red;'>{decoded_data}</span>")
            self.scroll_to_bottom()
        except Exception as e:
            self.terminal_output.append(f"Error reading error output: {str(e)}")


#Scrolling handler
    def scroll_to_bottom(self):
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.terminal_output.setTextCursor(cursor) 


#Cleaning handler
    def clear_terminal(self):
        self.terminal_output.clear()    


#Ending handler
    def process_finished(self):
        self.terminal_output.append("\nTerminal process finished")    

    
#Events     
    def closeEvent(self, event):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            self.process.waitForFinished(1000)
        super().closeEvent(event)

    def resizeEvent(self, event): 
        current_palette = self.palette() 
        if current_palette.brush(QPalette.ColorRole.Window).texture().isNull():
            return
        super().resizeEvent(event)    


#App creation
if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    terminal.show()
    sys.exit(app.exec())