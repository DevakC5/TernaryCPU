import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QComboBox, QSlider, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class SerialWorker(QThread):
    # Updated signal for 6 trits
    data_received = pyqtSignal(int, int, int, int, int, int, int)
    error_signal = pyqtSignal(str)

    def __init__(self, port, baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = True

    def run(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            
            while self.running:
                if self.serial_conn.in_waiting > 0:
                    try:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        parts = line.split(',')
                        if len(parts) == 7: # Expecting 7 items now
                            dec, t5, t4, t3, t2, t1, t0 = map(int, parts)
                            self.data_received.emit(dec, t5, t4, t3, t2, t1, t0)
                    except ValueError:
                        pass 
        except Exception as e:
            self.error_signal.emit(str(e))

    def send_delay(self, delay_ms):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{delay_ms}\n".encode('utf-8'))

    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()

class TernaryVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("6-Trit Hardware Analyzer (729 States)")
        self.setFixedSize(1100, 650) # Expanded window for 6 trits & larger matrix
        self.worker = None
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Connection Bar ---
        conn_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        
        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.setFixedWidth(40)
        self.btn_refresh.clicked.connect(self.refresh_ports)

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.toggle_connection)

        conn_layout.addWidget(QLabel("COM Port:"))
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(self.btn_refresh)
        conn_layout.addWidget(self.btn_connect)
        main_layout.addLayout(conn_layout)

        # --- Main Split Layout ---
        split_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        # LEFT PANEL: Decimal & Trits
        self.lbl_decimal = QLabel("Decimal: --")
        self.lbl_decimal.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.lbl_decimal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.lbl_decimal)

        trit_layout = QHBoxLayout()
        self.trit_labels = []
        # Create 6 trit displays (T5 to T0)
        for i in range(5, -1, -1):
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame_layout = QVBoxLayout(frame)
            
            lbl_title = QLabel(f"Trit {i}")
            lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            lbl_val = QLabel("-")
            lbl_val.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_val.setProperty("state", "default")
            
            frame_layout.addWidget(lbl_title)
            frame_layout.addWidget(lbl_val)
            trit_layout.addWidget(frame)
            self.trit_labels.append(lbl_val)

        left_panel.addLayout(trit_layout)
        
        # RIGHT PANEL: 27x27 Verification Matrix (729 States)
        matrix_title = QLabel("729-State Hardware Verification Matrix")
        matrix_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        matrix_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        right_panel.addWidget(matrix_title)

        self.matrix_grid = QGridLayout()
        self.matrix_grid.setSpacing(2) # Tighter spacing for massive grid
        self.dots = []

        # Create 729 dots for the 27x27 grid
        for i in range(729):
            dot = QLabel()
            dot.setFixedSize(12, 12) # Smaller dots to fit UI
            dot.setStyleSheet("background-color: #333333; border-radius: 6px;")
            
            row = i // 27
            col = i % 27
            self.matrix_grid.addWidget(dot, row, col)
            self.dots.append(dot)

        right_panel.addLayout(self.matrix_grid)
        right_panel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        split_layout.addLayout(left_panel, stretch=1)
        split_layout.addLayout(right_panel, stretch=1)
        main_layout.addLayout(split_layout)

        # --- Delay Controller ---
        delay_layout = QHBoxLayout()
        self.lbl_delay = QLabel("Loop Delay: 50 ms")
        self.slider_delay = QSlider(Qt.Orientation.Horizontal)
        self.slider_delay.setRange(0, 150) 
        self.slider_delay.setValue(50)
        self.slider_delay.setSingleStep(5)
        self.slider_delay.valueChanged.connect(self.update_delay)

        delay_layout.addWidget(QLabel("Speed Control:"))
        delay_layout.addWidget(self.slider_delay)
        delay_layout.addWidget(self.lbl_delay)
        main_layout.addLayout(delay_layout)

    def apply_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #FFFFFF; font-family: 'Segoe UI', Arial, sans-serif; }
            QPushButton { background-color: #2D2D2D; border: 1px solid #404040; padding: 6px 12px; border-radius: 4px; }
            QPushButton:hover { background-color: #3D3D3D; }
            QComboBox { background-color: #2D2D2D; border: 1px solid #404040; padding: 4px; }
            QFrame { background-color: #1E1E1E; border-radius: 8px; padding: 10px; }
            QSlider::groove:horizontal { height: 6px; background: #2D2D2D; border_radius: 3px; }
            QSlider::handle:horizontal { background: #00ADB5; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
            QLabel[state="default"] { color: #555555; }
            QLabel[state="0"] { color: #666666; } 
            QLabel[state="1"] { color: #00ADB5; } 
            QLabel[state="2"] { color: #00FFEA; }
        """)

    def reset_matrix(self):
        self.lbl_decimal.setStyleSheet("color: #FFFFFF;")
        for dot in self.dots:
            dot.setStyleSheet("background-color: #333333; border-radius: 6px;")

    def refresh_ports(self):
        self.port_combo.clear()
        for port in serial.tools.list_ports.comports():
            self.port_combo.addItem(port.device)

    def toggle_connection(self):
        if self.worker is None or not self.worker.running:
            port = self.port_combo.currentText()
            if not port: return
            
            self.reset_matrix() 
            
            self.worker = SerialWorker(port)
            self.worker.data_received.connect(self.update_display)
            self.worker.error_signal.connect(self.handle_error)
            self.worker.start()
            
            self.btn_connect.setText("Disconnect")
            self.btn_connect.setStyleSheet("background-color: #A00000; color: white;")
            self.worker.send_delay(self.slider_delay.value())
        else:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
            self.btn_connect.setText("Connect")
            self.btn_connect.setStyleSheet("")

    def update_display(self, dec, t5, t4, t3, t2, t1, t0):
        self.lbl_decimal.setText(f"Decimal: {dec}")
        read_trits = [t5, t4, t3, t2, t1, t0]
        
        for i, val in enumerate(read_trits):
            label = self.trit_labels[i]
            label.setText(str(val))
            label.setProperty("state", str(val))
            label.style().unpolish(label)
            label.style().polish(label)

        # Hardware Verification Logic for 6 Trits
        expected_t0 = dec % 3
        expected_t1 = (dec // 3) % 3
        expected_t2 = (dec // 9) % 3
        expected_t3 = (dec // 27) % 3
        expected_t4 = (dec // 81) % 3
        expected_t5 = (dec // 243) % 3
        expected_trits = [expected_t5, expected_t4, expected_t3, expected_t2, expected_t1, expected_t0]

        if 0 <= dec < 729:
            dot = self.dots[dec]
            
            if read_trits == expected_trits:
                dot.setStyleSheet("background-color: #00FF66; border-radius: 6px;")
            else:
                dot.setStyleSheet("background-color: #FF0033; border-radius: 6px;")
                self.lbl_decimal.setText(f"HALT AT: {dec}")
                self.lbl_decimal.setStyleSheet("color: #FF0033;")
                
                if self.worker and self.worker.running:
                    self.worker.send_delay(9999999) 
                    self.worker.stop() 
                
                self.btn_connect.setText("Connect")
                self.btn_connect.setStyleSheet("")

    def update_delay(self):
        val = self.slider_delay.value()
        if val == 0:
            self.lbl_delay.setText("Loop Delay: 0 ms (MAX SPEED)")
        else:
            self.lbl_delay.setText(f"Loop Delay: {val} ms")
        if self.worker and self.worker.running:
            self.worker.send_delay(val)

    def handle_error(self, err_msg):
        print(f"Serial Link Alert: {err_msg}")
        self.toggle_connection()

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TernaryVisualizer()
    window.show()
    sys.exit(app.exec())