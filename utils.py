"""
utils.py - Các hàm tiện ích cho PhotoLab
Bao gồm: mở/lưu file ảnh, resize ảnh
"""
import cv2
from tkinter import filedialog, messagebox


# Danh sách định dạng ảnh được hỗ trợ
IMAGE_FILETYPES = [
    ("Tất cả ảnh", "*.jpg *.jpeg *.png *.bmp"),
    ("JPEG", "*.jpg *.jpeg"),
    ("PNG", "*.png"),
    ("BMP", "*.bmp"),
    ("Tất cả file", "*.*")
]


def load_image_dialog():
    """
    Mở dialog để chọn file ảnh
    
    Trả về:
        Đường dẫn file nếu chọn, None nếu hủy
    """
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh",
        filetypes=IMAGE_FILETYPES
    )
    return file_path if file_path else None


def save_image_dialog(image):
    """
    Mở dialog để lưu ảnh ra file
    
    Tham số:
        image: numpy array định dạng RGB
        
    Trả về:
        True nếu lưu thành công, False nếu hủy hoặc lỗi
    """
    if image is None:
        messagebox.showwarning("Cảnh báo", "Không có ảnh để lưu!")
        return False
    
    file_path = filedialog.asksaveasfilename(
        title="Lưu ảnh",
        defaultextension=".jpg",
        filetypes=[
            ("JPEG", "*.jpg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp")
        ]
    )
    
    if file_path:
        # OpenCV yêu cầu định dạng BGR khi lưu
        if len(image.shape) == 2:  # Ảnh grayscale
            save_img = image
        else:
            save_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        cv2.imwrite(file_path, save_img)
        messagebox.showinfo("Thành công", "Đã lưu ảnh!")
        return True
    
    return False


def resize_image_to_fit(image, max_width=800, max_height=600):
    """
    Resize ảnh để vừa với khung hiển thị, giữ nguyên tỷ lệ
    
    Tham số:
        image: numpy array ảnh đầu vào
        max_width: chiều rộng tối đa cho phép
        max_height: chiều cao tối đa cho phép
        
    Trả về:
        numpy array ảnh đã resize (hoặc ảnh gốc nếu đã nhỏ hơn giới hạn)
    """
    if image is None:
        return None
    
    h, w = image.shape[:2]
    
    # Tính tỷ lệ thu nhỏ cần thiết
    ratio_h = max_height / h if h > max_height else 1
    ratio_w = max_width / w if w > max_width else 1
    ratio = min(ratio_h, ratio_w)
    
    # Chỉ resize nếu ảnh lớn hơn giới hạn
    if ratio < 1:
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        return cv2.resize(image, (new_w, new_h))
    
    return image
