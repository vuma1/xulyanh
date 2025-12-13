"""
processing.py - Các thuật toán xử lý ảnh sử dụng OpenCV
Bao gồm: điều chỉnh sáng/tương phản, làm nét, làm mờ, lật ảnh
"""
import cv2
import numpy as np


class ImageProcessor:
    """
    Class chứa các thuật toán xử lý ảnh
    Tất cả các phương thức đều là static - không cần khởi tạo instance
    """
    
    @staticmethod
    def load_image(filepath):
        """
        Đọc ảnh từ đường dẫn file
        
        Tham số:
            filepath: đường dẫn tới file ảnh
            
        Trả về:
            numpy array định dạng RGB, hoặc None nếu không đọc được
        """
        img = cv2.imread(filepath)
        if img is None:
            return None
        # OpenCV đọc màu theo chuẩn BGR, cần chuyển sang RGB để hiển thị đúng
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def apply_brightness_contrast(image, brightness=0, contrast=0):
        """
        Điều chỉnh độ sáng và tương phản của ảnh
        
        Công thức:
            - Tương phản: g(x) = (f(x) - 128) * alpa + 128
            - Độ sáng: g(x) = f(x) + beta
        
        Tham số:
            image: numpy array ảnh đầu vào
            brightness: độ sáng từ -100 đến 100 (0 = không đổi)
            contrast: tương phản từ -100 đến 100 (0 = không đổi)
            
        Trả về:
            numpy array ảnh đã xử lý
        """
        if image is None:
            return None

        # Nếu không có chỉnh sửa, trả về ảnh gốc
        if brightness == 0 and contrast == 0:
            return image.copy()

        # Chuyển sang float để tính toán
        img_float = image.astype(np.float32, copy=True)
        
        # Áp dụng tương phản
        # Contrast: Map từ [-100, 100] sang [0.5, 3.0] (1.0 là gốc)
        if contrast != 0:
            if contrast > 0:
                alpha = 1.0 + (contrast / 100.0) * 2.0  # 1.0 to 3.0
            else:
                alpha = 1.0 + (contrast / 100.0) * 0.5  # 0.5 to 1.0
            
            # Áp dụng tương phản: (pixel - 128) * alpha + 128
            img_float -= 128.0
            img_float *= alpha
            img_float += 128.0
        
        # Áp dụng độ sáng
        if brightness != 0:
            img_float += brightness
        
        # Clamp giá trị về [0, 255]
        np.clip(img_float, 0, 255, out=img_float)
        return img_float.astype(np.uint8)

    @staticmethod
    def to_grayscale(image):
        """
        Chuyển ảnh màu sang trắng đen (Grayscale)
        
        Tham số:
            image: numpy array ảnh RGB
            
        Trả về:
            numpy array grayscale (vẫn giữ 3 kênh màu để hiển thị)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Chuyển lại thành 3 kênh để Tkinter có thể hiển thị
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    @staticmethod
    def apply_blur(image, kernel_size=5):
        """
        Làm mờ ảnh bằng bộ lọc Gaussian Blur
        
        Tham số:
            image: numpy array ảnh đầu vào
            kernel_size: kích thước ma trận kernel (phải là số lẻ: 3, 5, 7...)
            
        Trả về:
            numpy array ảnh đã làm mờ
        """
        if len(image.shape) == 2:  # Nếu là ảnh grayscale
            result = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
            return cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    @staticmethod
    def apply_sharpen(image, strength=1):
        """
        Làm nét ảnh bằng kỹ thuật Unsharp Masking
        Sử dụng ma trận tích chập (Convolution Kernel) 3x3
        
        Tham số:
            image: numpy array ảnh đầu vào
            strength: độ mạnh làm nét từ 0 đến 20
            
        Trả về:
            numpy array ảnh đã làm nét
        """
        # Giới hạn strength để tránh làm nét quá mức
        strength = min(strength, 20)
        
        # Chuyển đổi strength: 0-20 → alpha: 2.0-10.0 (làm nét mạnh)
        alpha = 2.0 + (strength / 20.0) * 8.0
        
        # Ma trận kernel làm nét kiểu Unsharp Masking
        # Tâm = 1 + alpha, các cạnh = -alpha/4
        kernel = np.array([
            [0, -alpha/4, 0],
            [-alpha/4, 1 + alpha, -alpha/4],
            [0, -alpha/4, 0]
        ], dtype=np.float32)
        
        # Áp dụng bộ lọc
        img_float = image.astype(np.float32)
        result = cv2.filter2D(src=img_float, ddepth=-1, kernel=kernel)
        
        # Giới hạn giá trị pixel trong khoảng [0, 255]
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        if len(image.shape) == 2:
            return cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
        return result

    @staticmethod
    def flip_horizontal(image):
        """Lật ảnh theo chiều ngang (trái ↔ phải)"""
        return cv2.flip(image, 1)

    @staticmethod
    def flip_vertical(image):
        """Lật ảnh theo chiều dọc (trên ↔ dưới)"""
        return cv2.flip(image, 0)
