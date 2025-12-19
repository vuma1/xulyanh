"""
processing.py - Các thuật toán xử lý ảnh sử dụng OpenCV
Bao gồm: điều chỉnh sáng/tương phản, làm nét, làm mờ, lật ảnh
"""
import cv2
import numpy as np


class ImageProcessor:
    @staticmethod
    def apply_landscape_enhance(image, vibrance=60, saturation=30, sharpen=8, detail=10):
        """
        Tăng cường ảnh phong cảnh: màu sắc sống động, sắc nét, tăng chi tiết môi trường
        - Tăng vibrance (ưu tiên màu chưa bão hòa)
        - Tăng saturation vừa phải
        - Làm nét (sharpen)
        - Tăng chi tiết (detail enhancement)
        Tham số mặc định phù hợp cho ảnh phong cảnh
        """
        result = image.copy()
        # 1. Tăng vibrance & saturation
        result = ImageProcessor.apply_vibrance_saturation(result, vibrance, saturation)
        # 2. Làm nét (sharpen)
        if sharpen > 0:
            result = ImageProcessor.apply_sharpen(result, sharpen)
        # 3. Tăng chi tiết môi trường (detail enhancement)
        if detail > 0:
            # Sử dụng kỹ thuật High Pass Filter để tăng chi tiết
            gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
            # Lấy chi tiết cao tần
            highpass = cv2.GaussianBlur(gray, 1, 3)
            highpass = cv2.addWeighted(gray, 1.5, highpass, -0.5, 0)
            # Ghép lại thành 3 kênh
            highpass_color = cv2.cvtColor(highpass, cv2.COLOR_GRAY2RGB)
            # Blend với ảnh gốc
            result = cv2.addWeighted(result, 1.0, highpass_color, 0.25, 0)
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def apply_vibrance_saturation(image, vibrance=0, saturation=0):
        """
        Tăng cường độ rực rỡ (Vibrance) và độ bão hòa (Saturation) cho ảnh phong cảnh
        - Vibrance chỉ tăng bão hòa cho các màu chưa bão hòa (giữ màu da tự nhiên)
        - Saturation tăng đều cho mọi màu
    
        Tham số:
            image: numpy array RGB
            vibrance: -100 đến 100 (0 = không đổi)
            saturation: -100 đến 100 (0 = không đổi)
        """
        if vibrance == 0 and saturation == 0:
            return image.copy()
        # Chuyển sang HSV để dễ thao tác
        img_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
        h, s, v = img_hsv[:,:,0], img_hsv[:,:,1], img_hsv[:,:,2]
        # 1. Tăng Saturation đều
        if saturation != 0:
            sat_factor = 1.0 + (saturation / 100.0)
            s = s * sat_factor
        # 2. Tăng Vibrance: chỉ tăng cho pixel có S thấp
        if vibrance != 0:
            # Ngưỡng: S < 128 (chưa bão hòa)
            mask = s < 128
            vib_factor = 1.0 + (vibrance / 100.0)
            s[mask] = s[mask] * vib_factor
        # Clamp lại S về [0,255]
        s = np.clip(s, 0, 255)
        img_hsv[:,:,1] = s
        # Ghép lại và chuyển về RGB
        img_hsv = np.clip(img_hsv, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)
        return result
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

    @staticmethod
    def apply_skin_smoothing(image, strength=50):
        """
        Làm mịn da sử dụng Bilateral Filter
        Ưu điểm: làm mờ các chi tiết nhỏ (mụn, nếp nhăn) nhưng giữ lại các cạnh sắc nét
        
        Tham số:
            image: numpy array ảnh đầu vào
            strength: độ mạnh làm mịn từ 0 đến 100
            
        Trả về:
            numpy array ảnh đã làm mịn
        """
        if strength <= 0:
            return image.copy()
        
        # Map strength (0-100) sang các tham số Bilateral Filter
        # d: kích thước vùng lân cận (3-15)
        d = int(3 + (strength / 100.0) * 12)
        # sigmaColor: độ mạnh lọc theo màu (10-150)
        sigma_color = 10 + (strength / 100.0) * 140
        # sigmaSpace: độ mạnh lọc theo không gian (10-150)
        sigma_space = 10 + (strength / 100.0) * 140
        
        # Áp dụng Bilateral Filter
        result = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        
        return result

    @staticmethod
    def apply_bokeh_effect(image, blur_strength=50):
        """
        Hiệu ứng xóa phông (Bokeh Effect)
        Làm mờ hậu cảnh trong khi giữ vùng trung tâm rõ nét
        Sử dụng gradient mask hình elip để tạo độ chuyển tiếp mượt
        
        Tham số:
            image: numpy array ảnh đầu vào
            blur_strength: độ mạnh làm mờ hậu cảnh từ 0 đến 100
            
        Trả về:
            numpy array ảnh với hiệu ứng xóa phông
        """
        if blur_strength <= 0:
            return image.copy()
        
        h, w = image.shape[:2]
        
        # Tạo ảnh mờ cho hậu cảnh
        # Map blur_strength (0-100) sang kernel size (5-101, số lẻ)
        kernel_size = int(5 + (blur_strength / 100.0) * 96)
        if kernel_size % 2 == 0:
            kernel_size += 1
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        # Tạo gradient mask hình elip (vùng trung tâm sáng, viền tối)
        center_x, center_y = w // 2, h // 2
        # Kích thước vùng rõ nét (30-50% ảnh)
        radius_x = int(w * 0.35)
        radius_y = int(h * 0.4)
        
        # Tạo mask với gradient mượt
        Y, X = np.ogrid[:h, :w]
        # Tính khoảng cách chuẩn hóa từ tâm (ellipse)
        dist = np.sqrt(((X - center_x) / radius_x) ** 2 + ((Y - center_y) / radius_y) ** 2)
        
        # Tạo gradient mask: 1 ở tâm, 0 ở viền, với độ chuyển tiếp mượt
        mask = np.clip(1.5 - dist, 0, 1)
        # Làm mượt thêm mask
        mask = cv2.GaussianBlur(mask.astype(np.float32), (51, 51), 0)
        
        # Mở rộng mask thành 3 kênh
        mask_3d = np.dstack([mask] * 3)
        
        # Blend ảnh gốc và ảnh mờ theo mask
        result = (image.astype(np.float32) * mask_3d + 
                  blurred.astype(np.float32) * (1 - mask_3d))
        
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def apply_skin_tone_correction(image, warmth=0):
        """
        Điều chỉnh tone màu da (chỉ điều chỉnh độ ấm)
        Tinh chỉnh các kênh màu đỏ và vàng để da trông ấm hơn hoặc lạnh hơn
        
        Tham số:
            image: numpy array ảnh đầu vào (RGB)
            warmth: độ ấm (-50 đến 50), dương = vàng ấm, âm = xanh lạnh
            
        Trả về:
            numpy array ảnh đã điều chỉnh tone màu
        """
        if warmth == 0:
            return image.copy()
        
        # Chuyển sang float để tính toán
        img_float = image.astype(np.float32)
        
        # Tách các kênh RGB
        r, g, b = img_float[:, :, 0], img_float[:, :, 1], img_float[:, :, 2]
        
        # Điều chỉnh độ ấm (tăng R và G, giảm B cho ấm; ngược lại cho lạnh)
        warm_factor = warmth / 50.0 * 0.1  # ±10%
        r = r * (1.0 + warm_factor)
        g = g * (1.0 + warm_factor * 0.5)  # G tăng ít hơn
        b = b * (1.0 - warm_factor)  # B giảm khi ấm
        
        # Ghép lại các kênh
        result = np.dstack([r, g, b])
        
        # Clamp giá trị về [0, 255]
        return np.clip(result, 0, 255).astype(np.uint8)
