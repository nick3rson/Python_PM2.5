import requests
import json
import os
import time
from colorama import Fore, Style, init
from dotenv import load_dotenv

# เริ่มต้นระบบสีและโหลด Environment Variables
init(autoreset=True)
load_dotenv()

# ตั้งค่าตัวแปรหลัก
API_KEY = os.getenv("AIRVISUAL_API_KEY")
HISTORY_FILE = "aqi_history.json"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + r"""
   ╔══════════════════════════════════════════╗
   ║   🌬️  AQI & PM 2.5 MONITORING SYSTEM     ║
   ╚══════════════════════════════════════════╝
    """)

def get_data(url):
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('status') == 'success':
            return data
        return None
    except:
        return None

def save_history(country, state, city):
    history = load_history()
    entry = {"country": country, "state": state, "city": city, "time": time.strftime("%H:%M:%S")}
    # เก็บเฉพาะ 5 รายการล่าสุดไม่ซ้ำกัน
    history = [h for h in history if not (h['city'] == city and h['state'] == state)]
    history.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:5], f, ensure_ascii=False, indent=4)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_aqi_status(aqi):
    if aqi <= 50:
        return Fore.GREEN + "🟢 ดีมาก (Good)", "เหมาะสำหรับกิจกรรมกลางแจ้ง"
    elif aqi <= 100:
        return Fore.YELLOW + "🟡 ปานกลาง (Moderate)", "กลุ่มเสี่ยงควรระวัง"
    elif aqi <= 150:
        return Fore.LIGHTRED_EX + "🟠 เริ่มมีผลกระทบ (Unhealthy for Sensitive Groups)", "ควรสวมหน้ากาก"
    else:
        return Fore.RED + "🔴 อันตรายต่อสุขภาพ (Unhealthy)", "งดกิจกรรมกลางแจ้งและสวมหน้ากาก N95"

def show_result(country, state, city):
    print_header()
    print(f"📡 กำลังดึงข้อมูล: {Fore.YELLOW}{city}...")
    
    url = f"http://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={API_KEY}"
    res = get_data(url)
    
    if res:
        aqi = res['data']['current']['pollution']['aqius']
        temp = res['data']['current']['weather']['tp']
        hum = res['data']['current']['weather']['hu']
        status, advice = get_aqi_status(aqi)
        
        print("\n" + "─"*45)
        print(f"📍 {Fore.CYAN}{city}, {state} ({country})")
        print(f"🌡️  อุณหภูมิ: {temp}°C | 💧 ความชื้น: {hum}%")
        print(f"😷 ค่า AQI (US): {Fore.WHITE}{Style.BRIGHT}{aqi}")
        print(f"📊 ระดับ: {status}")
        print(f"💡 คำแนะนำ: {advice}")
        print("─"*45)
        save_history(country, state, city)
    else:
        print(Fore.RED + "❌ ไม่พบข้อมูลสำหรับพื้นที่นี้")
    
    input(f"\n{Fore.WHITE}กด Enter เพื่อกลับเมนูหลัก...")

def main():
    if not API_KEY:
        print(Fore.RED + "❌ ไม่พบ API KEY ในไฟล์ .env")
        return

    while True:
        print_header()
        print(f"{Fore.WHITE}[1] 🔍 ค้นหาตามพื้นที่")
        print(f"{Fore.WHITE}[2] 🕒 ประวัติการค้นหาล่าสุด")
        print(f"{Fore.WHITE}[3] 🚪 ออกจากโปรแกรม")
        
        choice = input(f"\n{Fore.GREEN}เลือกเมนู: ")

        if choice == '1':
            # ดึงประเทศ
            c_data = get_data(f"http://api.airvisual.com/v2/countries?key={API_KEY}")
            if not c_data: continue
            
            print(f"\n--- {Fore.CYAN}เลือกประเทศ{Fore.RESET} ---")
            for i, item in enumerate(c_data['data']):
                print(f"[{i+1}] {item['country']}")
            c_idx = int(input("หมายเลขประเทศ: ")) - 1
            country = c_data['data'][c_idx]['country']

            # ดึงรัฐ
            s_data = get_data(f"http://api.airvisual.com/v2/states?country={country}&key={API_KEY}")
            print(f"\n--- {Fore.CYAN}เลือกจังหวัด{Fore.RESET} ---")
            for i, item in enumerate(s_data['data']):
                print(f"[{i+1}] {item['state']}")
            s_idx = int(input("หมายเลขจังหวัด: ")) - 1
            state = s_data['data'][s_idx]['state']

            # ดึงเมือง
            ct_data = get_data(f"http://api.airvisual.com/v2/cities?state={state}&country={country}&key={API_KEY}")
            print(f"\n--- {Fore.CYAN}เลือกเมือง{Fore.RESET} ---")
            for i, item in enumerate(ct_data['data']):
                print(f"[{i+1}] {item['city']}")
            ct_idx = int(input("หมายเลขเมือง: ")) - 1
            city = ct_data['data'][ct_idx]['city']

            show_result(country, state, city)

        elif choice == '2':
            history = load_history()
            if not history:
                print(Fore.RED + "\nยังไม่มีประวัติการค้นหา")
                time.sleep(1.5)
                continue
            
            print(f"\n--- {Fore.YELLOW}รายการล่าสุด{Fore.RESET} ---")
            for i, h in enumerate(history):
                print(f"[{i+1}] {h['city']} ({h['time']})")
            
            h_choice = int(input("เลือกหมายเลขเพื่อดูอีกครั้ง (หรือ 0 เพื่อกลับ): "))
            if h_choice > 0:
                selected = history[h_choice-1]
                show_result(selected['country'], selected['state'], selected['city'])

        elif choice == '3':
            print(Fore.CYAN + "\nขอบคุณครับ! รักษาสุขภาพด้วยนะ 👋")
            break

if __name__ == "__main__":
    main()

