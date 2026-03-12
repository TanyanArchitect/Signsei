import cv2
import numpy as np
import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont

def get_text_contours(text, font_path, font_size):
    img = Image.new('L', (800, 300), color=255)
    draw = ImageDraw.Draw(img)
    
    actual_font_path = font_path
    if not os.path.exists(actual_font_path):
        win_font_path = os.path.join("C:\\Windows\\Fonts", font_path)
        if os.path.exists(win_font_path):
            actual_font_path = win_font_path
            
    try:
        font = ImageFont.truetype(actual_font_path, font_size)
    except IOError:
        font = ImageFont.truetype("arial.ttf", font_size)

    draw.text((10, 10), text, font=font, fill=0) 
    
    img_np = np.array(img)
    _, thresh = cv2.threshold(img_np, 128, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    if not contours: return [], 0, 0, 0, 0
    contours = list(contours)
    contours.sort(key=lambda c: cv2.boundingRect(c)[0])
    
    all_pts = np.vstack(contours).squeeze()
    if all_pts.ndim == 1: all_pts = all_pts.reshape(-1, 2)
    x, y, w, h = cv2.boundingRect(all_pts)
    return contours, x, y, w, h

def generate_ahk_script(contours, bbox, quad_pts, draw_time_sec, hotkey, filename="draw_signature.ahk"):
    orig_x, orig_y, orig_w, orig_h = bbox
    src_pts = np.array([[orig_x, orig_y], [orig_x + orig_w, orig_y], [orig_x + orig_w, orig_y + orig_h], [orig_x, orig_y + orig_h]], dtype="float32")
    dst_pts = np.array([[quad_pts[0]['x'], quad_pts[0]['y']], [quad_pts[1]['x'], quad_pts[1]['y']], [quad_pts[2]['x'], quad_pts[2]['y']], [quad_pts[3]['x'], quad_pts[3]['y']]], dtype="float32")
    
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    total_raw_points = sum(len(c) for c in contours)
    target_points = draw_time_sec * 80 
    step = max(1, int(total_raw_points / target_points))
    delay_ms = int((draw_time_sec * 1000) / (total_raw_points / step + len(contours)*2))
    delay_ms = max(2, delay_ms)
    
    ahk_code = [
        "; Script Signsei - Full Nét Chữ",
        "#InstallKeybdHook", 
        "#UseHook",          
        "CoordMode, Mouse, Screen",
        "SetBatchLines, -1", 
        f"SetMouseDelay, {delay_ms}", 
        "Sleep, 500", 
        "BlockInput, MouseMove",      
    ]
    
    for contour in contours:
        pts_float = contour.astype("float32")
        transformed_pts = cv2.perspectiveTransform(pts_float, matrix).astype("int32")
        
        start_pt = transformed_pts[0][0]
        ahk_code.append(f"MouseMove, {start_pt[0]}, {start_pt[1]}, 0") 
        ahk_code.append("Click, Down")
        
        for i in range(1, len(transformed_pts), step):
            pt = transformed_pts[i][0]
            ahk_code.append(f"MouseMove, {pt[0]}, {pt[1]}, 0")
            
        end_pt = transformed_pts[-1][0]
        ahk_code.append(f"MouseMove, {end_pt[0]}, {end_pt[1]}, 0")
        
        ahk_code.append("Sleep, 20") 
        ahk_code.append("Click, Up")
        ahk_code.append("Sleep, 20")
        
    ahk_code.append("BlockInput, MouseMoveOff") 
    ahk_code.append("ExitApp")

    if hotkey:
        ahk_code.append(f"\n{hotkey}::")
        ahk_code.append("BlockInput, MouseMoveOff") 
        ahk_code.append("Click, Up")                
        ahk_code.append("ExitApp")                  

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(ahk_code))
    return filename

if __name__ == "__main__":
    if len(sys.argv) > 5:
        text_can_ky = sys.argv[1]
        quad_pts = json.loads(sys.argv[2]) 
        draw_time_sec = float(sys.argv[3])
        hotkey = sys.argv[4] 
        font_filename = sys.argv[5]
    else:
        sys.exit()
        
    kich_thuoc = 100
    contours, cx, cy, cw, ch = get_text_contours(text_can_ky, font_filename, kich_thuoc)
    generate_ahk_script(contours, (cx, cy, cw, ch), quad_pts, draw_time_sec, hotkey)
    print("SUCCESS")