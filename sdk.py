import tkinter as tk
from tkinter import messagebox
from andor3 import Andor3, FEATURES

class CameraController:
    # 定义类属性
    search_button = None
    start_button = None
    stop_button = None
    capture_button = None

    def __init__(self, root):
        self.root = root
        self.root.title("Andor3 Camera Controller")

        # 设置窗口大小
        self.root.geometry("300x200")

        # 使窗口居中显示
        self.center_window()

        # 初始化相机变量
        self.cam = None

        # 创建GUI组件
        self.create_widgets()

    def center_window(self):
        # 获取屏幕宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 获取窗口宽度和高度
        window_width = 300
        window_height = 200

        # 计算窗口的位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_widgets(self):
        # 创建按钮
        self.search_button = tk.Button(self.root, text="查找相机", command=self.search_camera)
        self.search_button.pack(pady=10)

        self.start_button = tk.Button(self.root, text="开始拍照", command=self.start_capture)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="停止拍照", command=self.stop_capture)
        self.stop_button.pack(pady=10)

        self.capture_button = tk.Button(self.root, text="捕获图像", command=self.capture_image)
        self.capture_button.pack(pady=10)

    def search_camera(self):
        try:
            # 初始化相机
            self.cam = Andor3()
            print("Camera initialized successfully.")
            messagebox.showinfo("Info", "Camera found and initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            messagebox.showerror("Error", f"Failed to initialize camera: {e}")
            self.cam = None

    def configure_camera(self):
        if self.cam is None:
            messagebox.showerror("Error", "Camera not initialized. Please search for the camera first.")
            return

        # 使用相机的各种功能配置捕获设置
        self.set_feature("SensorCooling", True)
        self.set_feature("FanSpeed", "On")
        self.set_feature("CycleMode", "Fixed")
        self.set_feature("AccumulateCount", 1)
        self.set_feature("TriggerMode", "Internal")
        self.set_feature("ExposureTime", 0.01)
        self.set_feature("ElectronicShutteringMode", "Rolling")
        self.set_feature("Overlap", True)
        self.set_feature("SimplePreAmpGainControl", "16-bit (low noise & high well capacity)")
        self.set_feature("PixelReadoutRate", "280 MHz")
        self.set_feature("PixelEncoding", "Mono16")
        self.set_feature("SpuriousNoiseFilter", False)
        self.set_feature("StaticBlemishCorrection", False)
        self.set_feature("MetadataEnable", False)

        # 仅捕获传感器中间的128像素
        self.set_feature("AOIHeight", 128)
        self.set_feature("AOILeft", 1)
        self.set_feature("AOIWidth", 2560)
        self.set_feature("VerticallyCentreAOI", True)

    def set_feature(self, feature, value):
        if feature not in FEATURES:
            messagebox.showerror("Error", f"Unknown feature '{feature}'.")
            return

        try:
            if FEATURES[feature] == "Integer":
                self.cam.setInt(feature, value)
            elif FEATURES[feature] == "Floating Point":
                self.cam.setFloat(feature, value)
            elif FEATURES[feature] == "Boolean":
                self.cam.setBool(feature, value)
            elif FEATURES[feature] == "String":
                self.cam.setString(feature, value)
            elif FEATURES[feature] == "Enumerated":
                self.cam.setEnumString(feature, value)
            else:
                messagebox.showerror("Error", f"Unsupported data type '{FEATURES[feature]}' for feature '{feature}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set feature '{feature}': {e}")

    def start_capture(self):
        if self.cam is None:
            messagebox.showerror("Error", "Camera not initialized. Please search for the camera first.")
            return

        try:
            self.configure_camera()
            # 创建一个缓冲区用于存储图像数据
            self.cam.queueBuffer()
            # 开始采集
            self.cam.start()
            messagebox.showinfo("Info", "Capture started.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start capture: {e}")

    def stop_capture(self):
        if self.cam is None:
            messagebox.showerror("Error", "Camera not initialized. Please search for the camera first.")
            return

        try:
            # 停止采集
            self.cam.stop()
            messagebox.showinfo("Info", "Capture stopped.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop capture: {e}")

    def capture_image(self):
        if self.cam is None:
            messagebox.showerror("Error", "Camera not initialized. Please search for the camera first.")
            return

        try:
            # 从缓冲区获取原始数据
            data = self.cam.waitBuffer(timeout=1000)
            if data is not None:
                # 解码原始数据为图像（作为2D numpy数组）
                img, timestamp = self.cam.decode_image(data)
                messagebox.showinfo("Info", f"Image captured successfully. Timestamp: {timestamp}")
                # 可以在这里添加显示图像的逻辑
            else:
                messagebox.showerror("Error", "Failed to capture image.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraController(root)
    root.mainloop()