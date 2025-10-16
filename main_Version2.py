"""
Thiệp 20/10 bằng Pygame
- Chạy: python main.py
- Yêu cầu: pygame (pip install pygame)

Tính năng:
- Vẽ người que tặng hoa với cánh tay/hoa đung đưa nhẹ.
- Vẽ phong thư (thư) có thể click để "mở" (kéo nắp lên) và hiển thị thông điệp.
- Hiệu ứng overlay khi mở thư, nút "Đóng" để đóng thư.
- Phát hiệu ứng âm thanh nếu bạn đặt file 'open_sound.wav' trong cùng thư mục (tùy chọn).
- Nhấn S để lưu screenshot (qua-2010.png).
"""
import pygame
import sys
import math
import os
from datetime import datetime

# ------------------- Cấu hình -------------------
WIDTH, HEIGHT = 1000, 640
FPS = 60

# Màu sắc
BG_COLOR = (18, 24, 43)
ACCENT = (255, 107, 138)
WHITE = (245, 245, 250)
ENVELOPE_BASE = (240, 230, 210)
ENVELOPE_FLAP = (200, 170, 130)
TEXT_COLOR = (230, 230, 235)
OVERLAY_COLOR = (8, 10, 18, 200)

# Thông điệp
MESSAGE = ("Nhân dịp 20/10 tôi chúc bạn luôn mạnh khỏe, vui vẻ, "
           "xinh đẹp và luôn giữ nụ cười trên môi ❤️")

# Assets (tùy chọn)
OPEN_SOUND_FILE = "open_sound.wav"  # nếu có, chương trình sẽ cố gắng phát

# ------------------- Khởi tạo pygame -------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Thiệp 20/10 - Người que tặng hoa")
clock = pygame.time.Clock()

# Font fallback: nếu có font cụ thể bạn muốn, đổi tên ở đây
TITLE_FONT = pygame.font.SysFont("Segoe UI", 36, bold=True)
FONT = pygame.font.SysFont("Segoe UI", 20)
SMALL_FONT = pygame.font.SysFont("Segoe UI", 16)

# Envelope geometry
envelope_rect = pygame.Rect(WIDTH - 260, HEIGHT // 2 - 70, 220, 140)

# Stick figure base position
stick_pos = (240, 380)  # x, y của "mắt cá chân" (gốc thân)

# Animation / trạng thái
flower_bob = 0.0
flower_dir = 1
show_message = False
envelope_open_amount = 0.0  # 0.0 đóng, 1.0 mở hoàn toàn
envelope_opening = False

# Load optional sound
open_sound = None
if os.path.exists(OPEN_SOUND_FILE):
    try:
        open_sound = pygame.mixer.Sound(OPEN_SOUND_FILE)
    except Exception as e:
        print("Không thể load âm thanh:", e)

def draw_stick_figure(surface, base_pos, t):
    """Vẽ người que đơn giản, tay phải cầm hoa, tay trái giơ."""
    x, y = base_pos
    # head
    pygame.draw.circle(surface, WHITE, (x, y - 120), 20, 2)
    # body
    pygame.draw.line(surface, WHITE, (x, y - 100), (x, y - 30), 2)
    # legs
    pygame.draw.line(surface, WHITE, (x, y - 30), (x - 24, y + 30), 2)
    pygame.draw.line(surface, WHITE, (x, y - 30), (x + 24, y + 30), 2)
    # left arm (giơ lên, nhỏ)
    pygame.draw.line(surface, WHITE, (x, y - 80), (x - 56, y - 50), 2)

    # right arm (cầm hoa) đung đưa theo flower_bob
    arm_start = (x, y - 80)
    arm_end_x = x + 70
    arm_end_y = y - 70 + int(6 * math.sin(t * 2.0))
    pygame.draw.line(surface, WHITE, arm_start, (arm_end_x, arm_end_y), 2)

    # vẽ hoa ở đầu cánh tay phải
    flower_center = (arm_end_x + 10, arm_end_y - 8)
    petal_colors = [(255, 120, 160), (255, 95, 145)]
    for i in range(6):
        ang = i * (2 * math.pi / 6) + t * 0.5
        px = flower_center[0] + int(9 * math.cos(ang))
        py = flower_center[1] + int(6 * math.sin(ang))
        pygame.draw.ellipse(surface, petal_colors[i % 2], (px - 6, py - 6, 12, 12))
    pygame.draw.circle(surface, (255, 220, 80), flower_center, 6)
    # cuống hoa
    pygame.draw.line(surface, (100, 180, 100), (flower_center[0], flower_center[1] + 4),
                     (flower_center[0], flower_center[1] + 26), 3)

    # một vài phụ kiện: nơ nhỏ trên cổ
    pygame.draw.circle(surface, ACCENT, (x - 6, y - 95), 4)

def draw_envelope(surface, rect, open_amount):
    """Vẽ phong thư. open_amount 0..1 điều khiển nắp mở."""
    # thân phong thư
    body_color = ENVELOPE_BASE
    pygame.draw.rect(surface, body_color, rect, border_radius=8)

    # nắp phong thư (tam giác) - animate bằng open_amount
    # nắp gốc trên cùng
    top_y = rect.top
    mid_x = rect.centerx

    # khi mở, tam giác sẽ dịch lên và có chiều cao giảm
    flap_height = rect.height // 2
    # flap_offset tạo chuyển động nâng nắp
    flap_offset = int(open_amount * (flap_height + 10))

    p1 = (rect.left, top_y)
    p2 = (rect.right, top_y)
    p3 = (mid_x, top_y + flap_height - flap_offset)
    pygame.draw.polygon(surface, ENVELOPE_FLAP, [p1, p2, p3])

    # vẽ đường viền và chi tiết
    pygame.draw.rect(surface, (120, 90, 60), rect, 2, border_radius=8)
    pygame.draw.polygon(surface, (110, 80, 60), [p1, p2, p3], 2)

    # Nếu mở đủ, vẽ tờ thư nhô lên
    if open_amount > 0.05:
        # độ nhô lên của tờ giấy
        paper_offset = int(open_amount * (rect.height * 0.55))
        paper_rect = pygame.Rect(rect.left + 10, rect.top - paper_offset + 10, rect.width - 20, rect.height - 20)
        pygame.draw.rect(surface, (250, 250, 250), paper_rect, border_radius=4)
        # vài đường gợi ý mặt thư
        pygame.draw.line(surface, (220, 220, 220), (paper_rect.left + 12, paper_rect.top + 28),
                         (paper_rect.right - 12, paper_rect.top + 28), 2)
        # small heart decoration
        pygame.draw.circle(surface, ACCENT, (paper_rect.left + 24, paper_rect.top + 16), 6)

    # chữ "Thư" trên phong thư khi đóng hoặc căn lề khi mở
    label = SMALL_FONT.render("Thư", True, (80, 50, 40))
    if open_amount < 0.3:
        surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))
    else:
        surface.blit(label, (rect.left + 12, rect.top + 12))

def render_multiline_text(surface, text, rect, font, color=TEXT_COLOR, line_spacing=6):
    """Wrap và render text trong rect."""
    words = text.split(' ')
    lines = []
    cur = ""
    for w in words:
        test = cur + ("" if cur == "" else " ") + w
        if font.size(test)[0] <= rect.width - 16:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    y = rect.top
    for line in lines:
        if y + font.get_height() > rect.bottom:
            break
        txt = font.render(line, True, color)
        surface.blit(txt, (rect.left + 8, y))
        y += font.get_height() + line_spacing

def draw_scene(surface, t, mouse_pos):
    surface.fill(BG_COLOR)
    # tiêu đề
    tit = TITLE_FONT.render("Chúc mừng 20/10", True, ACCENT)
    surface.blit(tit, (40, 30))

    # trang trí trái tim nhỏ ở góc trên trái
    for i in range(6):
        hx = 40 + i * 28
        hy = 80 + (i % 2) * 6
        heart_s = 6 + (i % 3)
        pygame.draw.circle(surface, (255, 120, 160), (hx, hy), heart_s)

    # người que
    draw_stick_figure(surface, stick_pos, t)

    # phong thư
    hovered = envelope_rect.collidepoint(mouse_pos)
    draw_envelope(surface, envelope_rect, envelope_open_amount)

    # gợi ý
    hint = SMALL_FONT.render("Click vào phong thư để mở thư", True, (200, 200, 200))
    surface.blit(hint, (envelope_rect.left - 12 - hint.get_width(), envelope_rect.bottom - 6))

    # hướng dẫn lưu ảnh
    hint2 = SMALL_FONT.render("Nhấn S để lưu ảnh (screenshot)", True, (180, 180, 180))
    surface.blit(hint2, (40, HEIGHT - 36))

def draw_message_overlay(surface, message):
    """Vẽ overlay bán trong suốt và hộp thông điệp ở giữa. Trả về rect nút đóng."""
    # overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    surface.blit(overlay, (0, 0))

    # hộp message
    box_w, box_h = 720, 240
    box_rect = pygame.Rect((WIDTH - box_w) // 2, (HEIGHT - box_h) // 2, box_w, box_h)
    pygame.draw.rect(surface, (28, 34, 50), box_rect, border_radius=12)
    pygame.draw.rect(surface, (210, 170, 190), box_rect, 2, border_radius=12)

    # tiêu đề
    t = TITLE_FONT.render("Thư gửi bạn", True, ACCENT)
    surface.blit(t, (box_rect.centerx - t.get_width() // 2, box_rect.top + 12))

    # nội dung
    content_rect = pygame.Rect(box_rect.left + 20, box_rect.top + 64, box_w - 40, box_h - 110)
    render_multiline_text(surface, message, content_rect, FONT)

    # nút đóng
    btn_rect = pygame.Rect(box_rect.centerx - 50, box_rect.bottom - 46, 100, 34)
    pygame.draw.rect(surface, ACCENT, btn_rect, border_radius=8)
    btn_txt = FONT.render("Đóng", True, (20, 20, 20))
    surface.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2, btn_rect.centery - btn_txt.get_height() // 2))
    return btn_rect

def save_screenshot():
    """Lưu screenshot màn hình hiện tại."""
    filename = f"qua-2010-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    try:
        pygame.image.save(screen, filename)
        print("Saved screenshot:", filename)
    except Exception as e:
        print("Lưu ảnh thất bại:", e)

def main():
    global flower_bob, flower_dir, show_message, envelope_open_amount, envelope_opening
    running = True
    t = 0.0

    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt
        mouse_pos = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    save_screenshot()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True

        # update animation
        flower_bob += flower_dir * dt * 2.5
        if abs(flower_bob) > 6:
            flower_dir *= -1

        # handle envelope click -> bắt đầu animation mở
        if clicked and not show_message:
            if envelope_rect.collidepoint(mouse_pos):
                envelope_opening = True
                # play sound nếu có
                if open_sound:
                    try:
                        open_sound.play()
                    except Exception:
                        pass

        # animate envelope_open_amount
        if envelope_opening and envelope_open_amount < 1.0:
            envelope_open_amount = min(1.0, envelope_open_amount + dt * 3.0)
            if envelope_open_amount >= 1.0:
                envelope_opening = False
                show_message = True
        elif not envelope_opening and not show_message and envelope_open_amount > 0.0:
            # nếu người đóng (sau khi hiện message), quay lại đóng
            envelope_open_amount = max(0.0, envelope_open_amount - dt * 2.5)

        # nếu message đang hiển thị, vẽ overlay và kiểm tra click đóng
        draw_scene(screen, t, mouse_pos)
        if show_message:
            btn_rect = draw_message_overlay(screen, MESSAGE)
            if clicked and btn_rect.collidepoint(mouse_pos):
                # đóng message, thu lại phong thư
                show_message = False
                envelope_opening = False
                # bắt đầu đóng phong thư (giảm open amount)
                # sẽ được animate trong loop
        # Nếu user click khi phong thư đang mở (open_amount>0) nhưng chưa hiển thị message,
        # ta vẫn cho phép click để reveal tức thì: (handled above)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()