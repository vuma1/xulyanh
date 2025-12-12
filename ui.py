"""
ui.py - Giao diện người dùng PhotoLab
Chứa: buttons, windows, layout, theme colors
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from processing import ImageProcessor
from utils import load_image_dialog, save_image_dialog, resize_image_to_fit


# === BẢNG MÀU THEME 2025 - Dark Modern ===
COLORS = {
    'bg_dark': '#0d0d0d',           # Nền chính (gần đen)
    'bg_panel': '#1a1a1a',          # Panel điều khiển bên trái
    'bg_card': '#252525',           # Nền các section/card
    'bg_hover': '#2d2d2d',          # Màu khi hover
    'accent': '#6366f1',            # Màu chủ đạo (Indigo)
    'accent_hover': '#818cf8',      # Màu chủ đạo khi hover
    'accent_success': '#22c55e',    # Màu thành công (xanh lá)
    'accent_danger': '#ef4444',     # Màu nguy hiểm (đỏ)
    'text_primary': '#ffffff',      # Chữ chính (trắng)
    'text_secondary': '#a1a1aa',    # Chữ phụ (xám nhạt)
    'text_muted': '#71717a',        # Chữ mờ (xám đậm)
    'border': '#333333',            # Viền
    'slider_track': '#404040',      # Đường ray slider
}


class PhotoLabApp:
    """
    Class chính của ứng dụng PhotoLab
    Quản lý giao diện và điều phối các chức năng xử lý ảnh
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoLab")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        self.root.configure(bg=COLORS['bg_dark'])
        
        # === BIẾN TRẠNG THÁI ẢNH ===
        self.display_image = None      # Ảnh đang hiển thị trên màn hình
        self.original_image = None     # Ảnh gốc ban đầu (không bao giờ thay đổi)
        self.base_image = None         # Ảnh nền để áp dụng filter (thay đổi khi lật)
        self.is_grayscale = False      # Cờ đánh dấu chế độ trắng đen
        
        # Khởi tạo giao diện
        self._setup_styles()
        self._create_ui()

    def _setup_styles(self):
        """Cấu hình style cho các widget ttk"""
        style = ttk.Style()
        style.theme_use('clam')

    def _create_ui(self):
        """Tạo giao diện chính gồm panel trái (điều khiển) và phải (hiển thị ảnh)"""
        self._create_left_panel()
        self._create_right_panel()

    def _create_left_panel(self):
        """
        Tạo panel điều khiển bên trái
        Bao gồm: nút mở ảnh, các slider chỉnh sửa, nút lưu/reset
        """
        # Main left panel
        left_panel = tk.Frame(self.root, bg=COLORS['bg_panel'], width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        # Scrollable container
        canvas = tk.Canvas(left_panel, bg=COLORS['bg_panel'], 
                          highlightthickness=0, width=280)
        scrollbar = tk.Scrollbar(left_panel, orient=tk.VERTICAL, 
                                command=canvas.yview, width=8)
        self.control_frame = tk.Frame(canvas, bg=COLORS['bg_panel'])
        
        self.control_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.control_frame, anchor="nw", width=272)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", 
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # === HEADER ===
        self._create_header()
        
        # === OPEN BUTTON ===
        self.btn_open = self._create_button(
            self.control_frame, "📂  Mở ảnh", 
            self._on_open_image, COLORS['accent'], full_width=True
        )
        self.btn_open.pack(fill=tk.X, padx=16, pady=(20, 10))
        
        # === ADJUSTMENTS ===
        self._create_section_header("🎨  Chỉnh sửa màu sắc")
        self.scale_brightness = self._create_slider("Độ sáng", -100, 100, 0)
        self.scale_contrast = self._create_slider("Tương phản", -100, 100, 0)
        
        # === FILTERS ===
        self._create_section_header("✨  Bộ lọc")
        
        btn_grayscale = self._create_button(
            self.control_frame, "⚫  Trắng Đen",
            self._on_grayscale, COLORS['bg_card']
        )
        btn_grayscale.pack(fill=tk.X, padx=16, pady=4)
        
        self.scale_sharpen = self._create_slider("Làm nét", 0, 20, 0)
        self.scale_blur = self._create_slider("Làm mờ", 0, 30, 0)
        
        # === TRANSFORM ===
        self._create_section_header("🔄  Biến đổi")
        
        flip_frame = tk.Frame(self.control_frame, bg=COLORS['bg_panel'])
        flip_frame.pack(fill=tk.X, padx=16, pady=4)
        
        btn_flip_h = self._create_button(
            flip_frame, "↔ Lật ngang",
            self._on_flip_horizontal, COLORS['bg_card'], small=True
        )
        btn_flip_h.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        
        btn_flip_v = self._create_button(
            flip_frame, "↕ Lật dọc",
            self._on_flip_vertical, COLORS['bg_card'], small=True
        )
        btn_flip_v.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(4, 0))
        
        # === ACTIONS ===
        self._create_section_header("💾  Lưu trữ")
        
        btn_save = self._create_button(
            self.control_frame, "💾  Lưu ảnh",
            self._on_save_image, COLORS['accent_success']
        )
        btn_save.pack(fill=tk.X, padx=16, pady=4)
        
        btn_reset = self._create_button(
            self.control_frame, "🔄  Reset về gốc",
            self._on_reset_image, COLORS['accent_danger']
        )
        btn_reset.pack(fill=tk.X, padx=16, pady=4)
        
        # Spacer
        tk.Frame(self.control_frame, bg=COLORS['bg_panel'], height=30).pack(fill=tk.X)

    def _create_right_panel(self):
        """Tạo panel hiển thị ảnh bên phải"""
        image_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        image_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        # Image container với border - lưu reference để lấy kích thước khi resize
        self.image_container = tk.Frame(image_frame, 
                                   bg=COLORS['bg_card'],
                                   highlightbackground=COLORS['border'],
                                   highlightthickness=1)
        self.image_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Bind sự kiện resize cửa sổ
        self.image_container.bind('<Configure>', self._on_window_resize)
        
        # Placeholder text
        self.lbl_image = tk.Label(self.image_container, 
                                  text="📷\n\nKéo thả hoặc nhấn 'Mở ảnh'\nđể bắt đầu chỉnh sửa",
                                  font=("Segoe UI", 14),
                                  bg=COLORS['bg_card'],
                                  fg=COLORS['text_muted'],
                                  justify="center")
        self.lbl_image.pack(expand=True)

    def _create_header(self):
        """Tạo header với logo"""
        header_frame = tk.Frame(self.control_frame, bg=COLORS['bg_panel'])
        header_frame.pack(fill=tk.X, padx=16, pady=(20, 10))
        
        tk.Label(header_frame, text="✦ PhotoLab", 
                font=("Segoe UI", 20, "bold"),
                bg=COLORS['bg_panel'], 
                fg=COLORS['text_primary']).pack(anchor="w")
        
        tk.Label(header_frame, text="Professional Photo Editor", 
                font=("Segoe UI", 9),
                bg=COLORS['bg_panel'], 
                fg=COLORS['text_muted']).pack(anchor="w")

    def _create_section_header(self, text):
        """Tạo header cho mỗi section"""
        frame = tk.Frame(self.control_frame, bg=COLORS['bg_panel'])
        frame.pack(fill=tk.X, padx=16, pady=(20, 8))
        
        tk.Label(frame, text=text,
                font=("Segoe UI", 11, "bold"),
                bg=COLORS['bg_panel'],
                fg=COLORS['text_secondary']).pack(anchor="w")
        
        # Separator line
        tk.Frame(frame, bg=COLORS['border'], height=1).pack(fill=tk.X, pady=(8, 0))

    def _create_button(self, parent, text, command, bg_color, full_width=False, small=False):
        """Tạo button hiện đại với hover effect"""
        btn = tk.Label(parent, text=text,
                      font=("Segoe UI", 10 if small else 11, "bold" if not small else "normal"),
                      bg=bg_color,
                      fg=COLORS['text_primary'],
                      cursor="hand2",
                      pady=12 if full_width else 10,
                      padx=16)
        
        # Hover effects
        def on_enter(e):
            if bg_color == COLORS['bg_card']:
                btn.configure(bg=COLORS['bg_hover'])
            elif bg_color == COLORS['accent']:
                btn.configure(bg=COLORS['accent_hover'])
        
        def on_leave(e):
            btn.configure(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", lambda e: command())
        
        return btn

    def _create_slider(self, label_text, from_val, to_val, default_val):
        """Tạo slider hiện đại với label và value display"""
        container = tk.Frame(self.control_frame, bg=COLORS['bg_panel'])
        container.pack(fill=tk.X, padx=16, pady=8)
        
        # Header row (label + value)
        header = tk.Frame(container, bg=COLORS['bg_panel'])
        header.pack(fill=tk.X)
        
        tk.Label(header, text=label_text,
                font=("Segoe UI", 10),
                bg=COLORS['bg_panel'],
                fg=COLORS['text_secondary']).pack(side=tk.LEFT)
        
        value_label = tk.Label(header, text=str(default_val),
                              font=("Segoe UI", 10, "bold"),
                              bg=COLORS['bg_panel'],
                              fg=COLORS['accent'])
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider_frame = tk.Frame(container, bg=COLORS['bg_panel'])
        slider_frame.pack(fill=tk.X, pady=(6, 0))
        
        scale = tk.Scale(slider_frame, 
                        from_=from_val, to=to_val,
                        orient=tk.HORIZONTAL,
                        bg=COLORS['bg_panel'],
                        fg=COLORS['text_primary'],
                        troughcolor=COLORS['slider_track'],
                        activebackground=COLORS['accent'],
                        highlightthickness=0,
                        sliderrelief='flat',
                        showvalue=False,
                        length=230,
                        sliderlength=16,
                        command=lambda v, vl=value_label: self._on_slider_change(v, vl))
        scale.set(default_val)
        scale.pack(fill=tk.X)
        
        # Bind arrow keys
        scale.bind("<Left>", lambda e, s=scale: self._on_arrow_key(s, -1))
        scale.bind("<Right>", lambda e, s=scale: self._on_arrow_key(s, 1))
        
        return scale

    # === XỬ LÝ SỰ KIỆN ===
    
    def _on_slider_change(self, value, value_label):
        """Cập nhật hiển thị giá trị slider và áp dụng tất cả filter"""
        value_label.config(text=str(int(float(value))))
        self._apply_all_filters()

    def _on_arrow_key(self, scale_widget, delta):
        """
        Xử lý phím mũi tên trái/phải cho slider
        delta: -1 (giảm) hoặc +1 (tăng)
        """
        current = scale_widget.get()
        from_val = int(scale_widget.cget("from"))
        to_val = int(scale_widget.cget("to"))
        new_val = max(from_val, min(to_val, current + delta))
        scale_widget.set(new_val)
        return "break"  # Ngăn sự kiện mặc định

    def _on_open_image(self):
        """Mở dialog chọn ảnh và load ảnh vào ứng dụng"""
        file_path = load_image_dialog()
        if file_path:
            img_array = ImageProcessor.load_image(file_path)
            if img_array is not None:
                self.original_image = img_array.copy()
                self.base_image = img_array.copy()
                self.display_image = img_array.copy()
                self.is_grayscale = False
                self._show_image(img_array)
                self._reset_sliders()

    def _on_save_image(self):
        """Mở dialog lưu ảnh đã chỉnh sửa ra file"""
        save_image_dialog(self.display_image)

    def _on_reset_image(self):
        """Khôi phục ảnh về trạng thái gốc ban đầu"""
        if self.original_image is not None:
            self.base_image = self.original_image.copy()
            self.is_grayscale = False
            self._reset_sliders()
            self.display_image = self.original_image.copy()
            self._show_image(self.display_image)

    def _on_grayscale(self):
        """Bật/tắt chế độ ảnh trắng đen"""
        if self.base_image is None:
            return
        self.is_grayscale = not self.is_grayscale
        self._apply_all_filters()

    def _on_flip_horizontal(self):
        """Lật ảnh theo chiều ngang (trái ↔ phải)"""
        if self.base_image is None:
            return
        self.base_image = ImageProcessor.flip_horizontal(self.base_image)
        self._apply_all_filters()

    def _on_flip_vertical(self):
        """Lật ảnh theo chiều dọc (trên ↔ dưới)"""
        if self.base_image is None:
            return
        self.base_image = ImageProcessor.flip_vertical(self.base_image)
        self._apply_all_filters()

    # === CÁC HÀM HỖ TRỢ ===
    
    def _reset_sliders(self):
        """Đặt lại tất cả thanh trượt về giá trị 0"""
        self.scale_brightness.set(0)
        self.scale_contrast.set(0)
        self.scale_sharpen.set(0)
        self.scale_blur.set(0)

    def _apply_all_filters(self):
        """
        Áp dụng tất cả các bộ lọc lên base_image theo thứ tự:
        1. Độ sáng & Tương phản
        2. Làm nét (Sharpen)
        3. Làm mờ (Blur)
        4. Trắng đen (Grayscale)
        """
        if self.base_image is None:
            return
        
        result = self.base_image.copy()
        
        # 1. Áp dụng độ sáng và tương phản
        b = self.scale_brightness.get()
        c = self.scale_contrast.get()
        result = ImageProcessor.apply_brightness_contrast(result, b, c)
        
        # 2. Áp dụng làm nét nếu giá trị > 0
        sharpen = self.scale_sharpen.get()
        if sharpen > 0:
            result = ImageProcessor.apply_sharpen(result, sharpen)
        
        # 3. Áp dụng làm mờ nếu giá trị > 0
        blur = self.scale_blur.get()
        if blur > 0:
            kernel_size = blur * 2 + 1  # Đảm bảo kernel size là số lẻ
            result = ImageProcessor.apply_blur(result, kernel_size)
        
        # 4. Chuyển sang trắng đen nếu được bật
        if self.is_grayscale:
            result = ImageProcessor.to_grayscale(result)
        
        self.display_image = result
        self._show_image(result)

    def _show_image(self, img_array):
        """
        Hiển thị ảnh numpy array lên giao diện Tkinter
        Tự động resize ảnh để vừa khung hiển thị (theo kích thước cửa sổ)
        """
        if img_array is None:
            return
        
        # Lấy kích thước container thực tế (trừ padding)
        self.image_container.update_idletasks()
        container_w = self.image_container.winfo_width() - 40
        container_h = self.image_container.winfo_height() - 40
        
        # Đảm bảo kích thước tối thiểu
        max_width = max(400, container_w)
        max_height = max(300, container_h)
        
        # Resize để vừa khung
        img_array = resize_image_to_fit(img_array, max_width=max_width, max_height=max_height)
        
        # Chuyển sang format Tkinter
        img_pil = Image.fromarray(img_array)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        self.lbl_image.config(image=img_tk, text="", bg=COLORS['bg_card'])
        self.lbl_image.image = img_tk
    
    def _on_window_resize(self, event=None):
        """Xử lý khi cửa sổ thay đổi kích thước - cập nhật lại ảnh"""
        if self.display_image is not None:
            self._show_image(self.display_image)
