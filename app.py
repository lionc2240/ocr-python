# !pip install pytesseract pillow requests gradio
import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import cv2
import numpy as np
from PIL import Image
#from IPython.display import display, HTML
import io
import re
#import requests
import urllib.parse
import gradio as gr #Cai dat thu vien Gradio

# Khoi tao BANK_LIST de dung trong giao dien Gradio
BANK_LIST = {
    'Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank - VCB)': '970436',
    'Ngân hàng TMCP Đầu tư và Phát triển Việt Nam (BIDV)': '970418',
    'Ngân hàng TMCP Công Thương Việt Nam (VietinBank - ICB)': '970415',
    'Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank)': '970405',
    'Ngân hàng TMCP Kỹ Thương Việt Nam (Techcombank)': '970407',
    'Ngân hàng TMCP Quân đội (MB Bank)': '970422',
    'Ngân hàng TMCP Á Châu (ACB)': '970416',
    'Ngân hàng TMCP Tiên Phong (TPBank)': '970423',
    'Ngân hàng TMCP Phát triển TP.HCM (HDBank)': '970437',
    'Ngân hàng TMCP Quốc tế Việt Nam (VIB)': '970441',
    'Ngân hàng TMCP Sài Gòn Thương Tín (Sacombank)': '970403',
    'Ngân hàng TMCP Đông Nam Á (SeABank)': '970440',
    'Ngân hàng TMCP An Bình (ABBANK)': '970425',
    'Ngân hàng TMCP Bắc Á (Bac A Bank)': '970409',
    'Ngân hàng TMCP Bảo Việt (BaoVietBank)': '970438',
    'Ngân hàng TMCP Đại Chúng Việt Nam (PVcomBank)': '970412',
    'Ngân hàng TMCP Sài Gòn - Hà Nội (SHB)': '970443',
    'Ngân hàng TMCP Sài Gòn (SCB)': '970429',
    'Ngân hàng TMCP Việt Nam Thịnh Vượng (VPBank)': '970432',
    'Ngân hàng TMCP Hàng Hải Việt Nam (MSB)': '970426',
    'Ngân hàng TMCP Bưu điện Liên Việt (LienVietPostBank)': '970449',
    'Ngân hàng TMCP Nam Á (Nam A Bank)': '970428',
    'Ngân hàng TMCP Xăng dầu Petrolimex (PGBank)': '970430',
    'Ngân hàng TMCP Bản Việt (VietCapital Bank)': '970454',
    'Ngân hàng TMCP Kiên Long (KienLongBank)': '970452',
    'Ngân hàng TMCP Đông Á (DongA Bank)': '970406',
    'Ngân hàng TMCP Việt Á (VietABank)': '970427',
    'Ngân hàng TMCP Sài Gòn Công Thương (SaigonBank)': '970400',
    'Ngân hàng TMCP Đại Dương (OceanBank)': '970414',
    'Ngân hàng TMCP Dầu khí Toàn cầu (GPBank)': '970408',
    'Ngân hàng TMCP Việt Nam Thương Tín (VietBank)': '970433',
    'Ngân hàng TNHH MTV Shinhan Việt Nam (Shinhan Bank)': '970424',
    'Ngân hàng TNHH MTV Woori Việt Nam (Woori Bank)': '970457',
    'Ngân hàng TNHH MTV Hong Leong Việt Nam (Hong Leong Bank)': '970442',
    'Ngân hàng TNHH MTV UOB Việt Nam (UOB)': '970458',
    'Ngân hàng TNHH MTV Public Bank Việt Nam (Public Bank)': '970439',
    'Ngân hàng TNHH MTV CIMB Việt Nam (CIMB Bank)': '422589',
    'Ngân hàng TNHH MTV Standard Chartered Việt Nam (Standard Chartered)': '970410',
    'Ngân hàng TNHH MTV HSBC Việt Nam (HSBC)': '458761',
    'Ngân hàng TNHH MTV ANZ Việt Nam (ANZ)': '970410'
}


# --------------------------
# A. LOGIC LAM SACH VA TRICH XUAT SO TIEN
# --------------------------

def clean_amount(extracted_text):
    """Lam sach va trich xuat so tien tu ket qua OCR."""
    if not extracted_text: return 0
    # Remove newline, space
    cleaned_amount_raw = extracted_text.strip().replace('\n', '').replace(' ', '')
    match = re.search(r'(\d[\d.,]*)', cleaned_amount_raw)

    if match:
        temp_amount = match.group(1)
        # Remove separators
        cleaned_amount_no_separator = re.sub(r'[.,]', '', temp_amount)
        cleaned_amount_regex = cleaned_amount_no_separator

        # Fix: remove trailing '4' (potential currency symbol recognition error)
        if cleaned_amount_regex.endswith('4') and len(cleaned_amount_regex) > 3:
            cleaned_amount_regex = cleaned_amount_regex[:-1]

        try:
            return int(cleaned_amount_regex)
        except ValueError:
            return 0
    return 0

# --------------------------
# B. HAM XU LY TONG HOP CHO GRADIO
# --------------------------

def process_and_generate_qr(
    image_pil,
    bank_name, # Changed from bank_id to bank_name
    account_no,
    account_name,
    anchor_text="Thu tien mat"
):
    """Thuc hien xu ly anh, OCR va tao ma QR, tra ve cac buoc hien thi."""

    # Default values for image outputs
    roi_pil = None
    processed_pil = None

    if image_pil is None:
        return None, None, "❌ Loi: Vui long tai len mot file anh.", None
    if not bank_name or not account_no or not account_name:
        return None, None, "❌ Loi: Vui long dien day du thong tin thu huong.", None

    # Look up bank_id from bank_name
    bank_id = BANK_LIST.get(bank_name)
    if bank_id is None:
        return None, None, f"❌ Loi: Khong tim thay ma BIN cho ngan hang '{bank_name}'.", None

    # 1. Chuan bi anh cho OpenCV
    image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    img_h, img_w, _ = image_cv.shape

    # 2. OCR va Tim kiem Anchor text
    anchor_lang = 'vie'
    anchor_config = r'--psm 6'

    data = pytesseract.image_to_data(image_cv, lang=anchor_lang, config=anchor_config, output_type=pytesseract.Output.DICT)
    found_anchor = False
    anchor_box = None
    text_x, text_y, text_w, text_h = data['left'], data['top'], data['width'], data['height']

    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        if word == "Thu" and i + 2 < len(data['text']):
            # Check for "tien mat" next to "Thu"
            if data['text'][i+1].strip() == "tiền" and data['text'][i+2].strip() == "mặt":
                anchor_box = (text_x[i+2], text_y[i+2], text_w[i+2], text_h[i+2])
                found_anchor = True
                break

    if not found_anchor:
        return None, None, f"❌ Loi: Khong tim thay Anchor text '{anchor_text}'. Khong the xac dinh vung ROI.", None

    # 3. Tinh toan va Cat Vung ROI DONG
    ax, ay, aw, ah = anchor_box
    x_start = max(0, ax + aw + int(aw * 0.5))
    y_start = max(0, ay)
    x_end = img_w
    y_end = min(img_h, ay + ah + 10)
    roi_image = image_cv[y_start:y_end, x_start:x_end]

    if roi_image.size == 0:
        return None, None, "❌ Loi: Vung ROI bi cat rong. Vui long kiem tra lai anh.", None

    # Chuyen anh ROI sang PIL de hien thi
    roi_pil = Image.fromarray(cv2.cvtColor(roi_image, cv2.COLOR_BGR2RGB))


    # 4. TIEN XU LY (Upscaling + Morphological Closing)
    gray_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    scale_factor = 3
    # Upscaling (INTER_CUBIC)
    resized_roi = cv2.resize(gray_roi, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # Binarization (Otsu)
    _, binary_roi = cv2.threshold(resized_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Closing
    kernel = np.ones((3, 3), np.uint8)
    binary_roi_closed = cv2.morphologyEx(binary_roi, cv2.MORPH_CLOSE, kernel)
    # Inverse for Tesseract
    binary_final = cv2.bitwise_not(binary_roi_closed)

    # Chuyen anh da xu ly sang PIL de hien thi
    processed_pil = Image.fromarray(cv2.cvtColor(binary_final, cv2.COLOR_GRAY2RGB))

    # 5. OCR tren anh da xu ly
    final_ocr_config = r'--psm 7 -c tessedit_char_whitelist=0123456789.,'
    extracted_text = pytesseract.image_to_string(binary_final, config=final_ocr_config)
    final_amount = clean_amount(extracted_text)

    # 6. Tao Quick Link QR
    if final_amount <= 0:
        return roi_pil, processed_pil, f"❌ Loi: Trich xuat so tien khong thanh cong. Ket qua tho: '{extracted_text}'", None

    encoded_amount_name = urllib.parse.quote(account_name)
    description = urllib.parse.quote(f"CK {final_amount}")
    template = 'compact2'

    qr_code_url = (
        f"https://img.vietqr.io/image/{bank_id}-{account_no}-{template}.png?"
        f"amount={final_amount}&addInfo={description}&accountName={encoded_amount_name}"
    )

    # 7. Dinh dang ket qua dau ra (HTML)
    result_html = f"""
    <h4>✅ Buoc 3: OCR Thanh Cong!</h4>
    <p><strong>Ket qua OCR Tho:</strong> {extracted_text.strip()}</p>
    <p><strong>So tien Trich xuat (Da lam sach):</strong> <span style='color: green; font-size: 1.2em;'>{final_amount:,} VNĐ</span></p>
    <p><strong>Ngan hang:</strong> {bank_name} | <strong>TK:</strong> {account_no}</p>
    """

    return roi_pil, processed_pil, result_html, qr_code_url

# Helper function for uppercase conversion - REMOVED AS REQUESTED
# def to_uppercase(text):
#     return text.upper()

# --------------------------
# C. GRADIO INTERFACE (GIAO DIEN)
# --------------------------

# Su dung Blocks de co the co nhieu output canh nhau
with gr.Blocks() as demo:
    gr.Markdown("# 📸 Ung Dung OCR & Tao QR Chuyen Khoan")
    gr.Markdown("Ung dung su dung **OpenCV (Upscaling, Otsu, Morphology)** va **Pytesseract** de trich xuat so tien tu anh hoa don va tao ma VietQR.")

    # KHU VUC INPUT

    gr.Markdown("## 1. Thong tin Input")

    # Input Anh
    image_input = gr.Image(type="pil", label="1. Tai len anh hoa don (co 'Thu tien mat')", width=400)

    # Input Thong tin Thu huong
    with gr.Row():
        bank_name_input = gr.Dropdown(
            label="2. Ngan hang",
            choices=list(BANK_LIST.keys()),
            value='Ngân hàng TMCP Đầu tư và Phát triển Việt Nam (BIDV)', # Corrected default value
            interactive=True
        )
        account_no_input = gr.Textbox(label="3. So Tai khoan", value="0915118319", interactive=True)
        account_name_input = gr.Textbox(label="4. Ten TK (Khong dau, IN HOA)", value="DAO THE HOANG", interactive=True)
        # Removed .change() event for uppercase conversion as requested
        # account_name_input.change(fn=to_uppercase, inputs=account_name_input, outputs=account_name_input)

    # Nut thuc thi
    process_button = gr.Button("🚀Thuc Hien Xu Ly Anh, OCR & Tao Ma QR")

    # KHU VUC OUTPUT

    gr.Markdown("## 2. Quy Trinh Xu Ly Anh Truc Quan")

    # Hien thi cac buoc xu ly anh truc quan
    with gr.Row():
        roi_output = gr.Image(label="Buoc 1: Vung ROI da Cat (Crop)", type="pil", width=300)
        processed_output = gr.Image(label="Buoc 2: Anh da Tien Xu Ly (Upscale + Closing)", type="pil", width=300)


    gr.Markdown("## 3. Ket Qua OCR va Ma QR")

    with gr.Row():
        result_output = gr.HTML(label="Buoc 3 & 4: OCR va Ket Qua", value="Cho xu ly...")
        qr_output = gr.Image(label="Buoc 5: Ma QR Chuyen Khoan", type="filepath", width=300, height=300)

    # Lien ket nut voi ham xu ly
    process_button.click(
        fn=process_and_generate_qr,
        inputs=[image_input, bank_name_input, account_no_input, account_name_input],
        outputs=[roi_output, processed_output, result_output, qr_output]
    )

if __name__ == "__main__":
# Khoi chay giao dien Gradio
    demo.launch(debug=True, share=False) # <- share=True tao URL cong khai 

