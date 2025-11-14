# Chạy cục bộ
## Cài đặt môi trường và thư viện cần thiết
### Cài đặt Python 3.8+
- Tải Installer: [python.org/downloads/](https://python.org/downloads/)
- Kiểm tra phiên bản Python: `python --version`
### Cài đặt Tesseract OCR engine 
- Tải Installer (Windows): [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- Set variable: Trong System Variable - Edit - New hãy dán `C:\Program Files\Tesseract-OCR\` và OK (giả sử đường dẫn cài đặt engine tại`C:\Program Files\Tesseract-OCR\tesseract.exe`)
- Thêm `pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"` bên dưới dòng import pytesseract nếu chưa nhận path, tôi đã để sẵn trong `app.py`, bạn có thể comment nó nếu muốn (Nếu đã set variable rồi thì bỏ qua bước này)
- Bổ sung dữ liệu OCR tiếng Việt vào thư mục data: Tải file tại https://github.com/tesseract-ocr/tessdata/blob/main/vie.traineddata, sau đó đặt file vào `C:\Program Files\Tesseract-OCR\tessdata\`
### Tạo môi trường ảo cho dự án (trong cmd):
- Tạo thư mục dự án:		
```cmd
mkdir <poo>
cd <poo>
```
- Tạo môi trường ảo (`venv`): `python -m venv myVenv`
- Kích hoạt môi trường ảo (`activate`):	`.\myVenv\Scripts\activate` (Để thoát khỏi `venv` dùng lệnh `deactivate`)

## Cài đặt thư viện và Tesseract OCR engine trong môi trường ảo
- Các gói Python: 
```cmd
pip install pytesseract pillow opencv-python gradio requests
```
Đợi một lúc để quá trình cài đặt hoàn tất.


Như vậy là đã đầy đủ các công cụ cần thiết, bước tiếp theo là chạy chương trình.
## Chạy chương trình
### Mở chương trình
Để chạy chương trình trong `venv`, sử dụng lệnh:
```
python app.py
```
Sau đó sẽ xuất hiện:
```
* Running on local URL:  http://127.0.0.1:...
* To create a public link, set `share=True` in `launch()`.
```
Mở local URL và bắt đầu xử lý ảnh với tập data tôi đã để sẵn trong thư mục `\screenshots`
### Thiết lập thụ hưởng
Bạn có thể thiết lập thông tin thụ hưởng tại các mục Ngan hang, So tai khoan và Ten TK.
### Xử lý ảnh và hiển thị mã QR
Sau khi tải ảnh lên và thiết lập đầy đủ thụ hưởng, click nút tạo và chúng ta sẽ có mã QR code được điền sẵn số tiền.

## Tắt chương trình
Sử dụng tổ hợp `Ctrl+C` trong CMD sau đó nhập lệnh `deactivate` để thoát khỏi `venv`

# Chạy trên Colab
- Sử dụng file `OCR_v6_Gradio_components.ipynb`