import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
from min import *
import threading
import time
import sys

class PythonMin:
    def __init__(self) -> None:
        self.minHandle    = None
        self.connectState = False
        self.min_id       = 16
    def isConnected(self) -> bool:
        return self.connectState

    def connect(self, port:str, baudrate:int) -> bool:
        retVal = False
        try:
            self.minHandle = MINTransportSerial(port=port, baudrate=baudrate)
            self.connectState = True
            retVal = True
        except MINConnectionError:
            retVal = False
        return retVal
    
    def close(self) -> None:
        self.minHandle.close()
        self.minHandle.portStatus = False
        self.connectState = False

    def send(self, payload:bytes) -> None:
        self.minHandle.send_frame(min_id=self.min_id, payload=payload)




class UARTInterface:
    def __init__(self, root, minHandler:PythonMin):
        self.root = root
        self.root.title("MinDiagnostic")
        self.minHandler = minHandler
        
        # Kích thước cố định cho giao diện
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # Frame chứa phần chọn cổng và baudrate
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10, anchor='w')

        # Nút connect/disconnect lệch hẳn về bên trái
        self.connect_button = tk.Button(self.top_frame, text="Connect", command=self.toggle_connection, bg="lightgreen", width=15)
        self.connect_button.grid(row=0, column=0, padx=5)

        # Drop list để chọn cổng UART
        self.port_label = tk.Label(self.top_frame, text="Select Port:")
        self.port_label.grid(row=0, column=1, padx=5)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self.top_frame, textvariable=self.port_var, state="readonly", width=15)
        self.port_dropdown.grid(row=0, column=2, padx=5)

        # Drop list để chọn baudrate
        self.baudrate_label = tk.Label(self.top_frame, text="Baudrate:")
        self.baudrate_label.grid(row=0, column=3, padx=5)

        self.baudrate_var = tk.StringVar()
        self.baudrate_dropdown = ttk.Combobox(self.top_frame, textvariable=self.baudrate_var, state="readonly", width=10)
        self.baudrate_dropdown['values'] = ['9600', '115200', '57600', '38400']
        self.baudrate_dropdown.grid(row=0, column=4, padx=5)
        self.baudrate_dropdown.current(1)

        # Nút refresh để cập nhật danh sách cổng UART
        self.refresh_button = tk.Button(self.top_frame, text="Refresh Ports", command=self.refresh_ports, bg="lightblue")
        self.refresh_button.grid(row=0, column=5, padx=5)

        # Frame chứa ô nhập liệu và nút send
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10, anchor='w')

        # Ô nhập ID gửi đi
        self.id_label = tk.Label(self.input_frame, text="ID:")
        self.id_label.grid(row=0, column=0, padx=5)
        
        self.id_entry = tk.Entry(self.input_frame, width=10)
        self.id_entry.grid(row=0, column=1, padx=5)

        # Ô nhập dữ liệu dạng số hex, to hơn và lệch về bên trái
        self.data_entry = tk.Entry(self.input_frame, width=50)
        self.data_entry.grid(row=0, column=2, padx=5)

        # Liên kết phím Enter với hàm send_data
        self.data_entry.bind('<Return>', self.send_data_event)

        # Nút gửi dữ liệu
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_data, bg="lightblue", width=15)
        self.send_button.grid(row=0, column=3, padx=5)
        self.send_button.config(state='disabled')

        # Khung cuộn để hiển thị dữ liệu đã gửi và nhận
        self.log_text = scrolledtext.ScrolledText(root, width=80, height=26, state='disabled')
        self.log_text.pack(pady=10)

        # Thêm nút Clear Data
        self.clear_button = tk.Button(root, text="Clear Data", command=self.clear_data, bg="lightgray")
        self.clear_button.pack(pady=5)

        # Biến để quản lý kết nối serial
        self.serial_conn = None

        # Refresh danh sách cổng UART khi khởi động
        self.refresh_ports()
    def refresh_ports(self):
        """Cập nhật danh sách cổng UART có sẵn."""
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_dropdown['values'] = port_list
        if port_list:
            self.port_dropdown.current(0)

    def toggle_connection(self):
        """Kết nối hoặc ngắt kết nối tới cổng UART."""
        # if self.min_handler.isSerialAvaiable():
        if self.minHandler.isConnected():
            self.minHandler.close()
            # Ngắt kết nối
            self.log_info("Disconnected.")
            self.connect_button.config(text="Connect", bg="lightgreen")
            self.send_button.config(state='disabled')
        else:
            # Kết nối
            self.clear_data()
            port = self.port_var.get()
            baudrate = self.baudrate_var.get()

            if port and baudrate:
                    if self.minHandler.connect(port=port,baudrate=baudrate):
                        self.log_info(f"Connected to {port} at {baudrate} baudrate.")
                        self.connect_button.config(text="Disconnect", bg="lightcoral")
                        self.send_button.config(state='normal')
                    else:
                        self.log_error(f"Serial port {port} opening error!")

            else:
                self.log_error("Please select a port and baudrate!")
    
    def send_data_event(self, event):
        """Gửi dữ liệu khi nhấn phím Enter."""
        self.send_data()

    def send_data(self):
        """Gửi dữ liệu hex qua UART và hiển thị kết quả."""
        # if self.serial_conn and self.serial_conn.is_open:
        if self.minHandler.isConnected():
            hex_data = self.data_entry.get().replace(" ", "")
            id_data = self.id_entry.get().replace(" ", "")

            if id_data:
                try:
                    min_id = int(id_data, 16)

                    if min_id > 0x3F:
                        raise ValueError("Please enter ID below 0x80!")
                    else:
                        self.minHandler.min_id = min_id
                except ValueError as e:
                    self.log_error(f"{e}")
                if hex_data:
                    try:
                        # Chuyển đổi dữ liệu từ chuỗi hex sang byte
                        data_bytes = bytes.fromhex(hex_data)
                        self.minHandler.send(data_bytes)
                        self.log_tx(f"[{hex(self.minHandler.min_id)[2:]}] <<< {self.format_hex(hex_data)}".upper())
                    except ValueError:
                        self.log_error("Invalid hex data!")
                else:
                    self.log_error("Please enter hex data!")
            else:
                self.log_error("Please enter ID data!")
        else:
            self.log_error("Not connected to any port!")

    def format_hex(self, hex_str):
        """Định dạng chuỗi hex theo dạng '01 02 03 04'."""
        return ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))

    def log_tx(self, message):
        self.log(message=message, color="orange")

    def log_rx(self, message):
        self.log(message=message, color="blue")

    def log_error(self, message):
        self.log(message=message, color="red")
    
    def log_info(self, message):
        self.log(message=message, color="green")

    def log(self, message, color:str):
        """Hiển thị thông điệp trong khung log."""
        self.log_text.config(state='normal')
        self.log_text.tag_configure(color, foreground=color, font=("Helvetica", 13))
        self.log_text.insert(tk.END, message + "\n", color)
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)

    def clear_data(self):
        """Xóa toàn bộ dữ liệu trong khung log."""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def on_closing(self):
        """Đảm bảo ngắt kết nối và dừng thread khi đóng ứng dụng."""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.root.destroy()
        sys.exit()
            
        
def background_task(app:UARTInterface, minHandler:PythonMin):
    while True:
        if minHandler.isConnected():
            frames = minHandler.minHandle.poll()
            if frames:
                for frame in frames:
                    hexdata = frame.payload.hex()
                    app.log_rx(f"[{hex(frame.min_id)[2:]}] >>> {app.format_hex(hexdata).upper()}")
        time.sleep(0.1)

if __name__ == "__main__":

    root      = tk.Tk()
    guiMin    = PythonMin()
    app       = UARTInterface(root, guiMin)
    
    background_thread = threading.Thread(target=background_task, args=(app,guiMin,), daemon=True)
    background_thread.start()
    root.protocol("WM_DELETE_WINDOW", app.on_closing) 
    root.mainloop()