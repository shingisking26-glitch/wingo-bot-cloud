import os
import time
import requests
from supabase import create_client, Client

# 1. गेमचा लाईव्ह API लिंक आणि तुमचे Supabase क्रेडेंशियल्स
API_URL = "https://ar-lottery01.com"
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_KGB6K0zarkhbgyJi75YXQA_SK0qfL71"

# Supabase क्लाइंट कनेक्ट करणे
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_store():
    try:
        # गेमच्या API कडून लाईव्ह डेटा खेचणे
        response = requests.get(API_URL, timeout=10)
        if response.status_code != 200:
            print(f"🔄 गेम API एरर: {response.status_code}. पुन्हा प्रयत्न करत आहे...")
            return
            
        json_data = response.json()
        raw_list = json_data.get("data", {}).get("list", [])
        
        if not raw_list:
            print("⏳ सध्या कोणताही नवीन डेटा मिळाला नाही.")
            return
            
        print(f"🔎 गेममधून {len(raw_list)} लेटेस्ट रिझल्ट्स मिळाले. डुप्लिकेट फिल्टर चालू आहे...")
        
        # जुने पीरियड्स उलटे (reversed) करून तपासणार जेणेकरून डेटा योग्य टाइमलाईननुसार सेव्ह होईल
        for item in reversed(raw_list):
            issue = str(item.get("issueNumber"))
            num = str(item.get("number"))
            col = str(item.get("color"))
            
            # 🎯 ऑटोमॅटिक Big / Small कॅल्क्युलेटर (0-4 = small, 5-9 = big)
            if num.isdigit():
                n = int(num)
                size = "small" if n <= 4 else "big"
            else:
                size = "unknown"
            
            # 🚀 डुप्लिकेट चेकर: हा पीरियड डेटाबेसमध्ये आधीपासून आहे का ते तपासणे
            check = supabase.table("wingo_data").select("issueNumber").eq("issueNumber", issue).execute()
            
            if len(check.data) == 0:
                # जर पीरियड नवीन असेल, तरच तो डेटाबेसमध्ये सेव्ह करा
                data_to_insert = {
                    "issueNumber": issue,
                    "number": num,
                    "color": col,
                    "size": size
                }
                supabase.table("wingo_data").insert(data_to_insert).execute()
                print(f"✅ नवीन पीरियड सेव्ह झाला: {issue} -> {num} ({col}) -> {size.upper()}")
            else:
                # डेटा आधीपासून असेल तर सोडन देणे (Skip करणे)
                pass
                
    except Exception as e:
        print(f"⚠️ नेटवर्क किंवा कोडमध्ये समस्या आली: {e}")

# 24 तास सलग बॅकग्राउंडमध्ये चालणारा लूप (दर 30 सेकंदांनी नवीन डेटा तपासणार)
print("🚀 Big/Small फिल्टर असलेला 24/7 ऑनलाईन क्लाउड स्क्रॅपर यशस्वीरित्या चालू झाला आहे...")
while True:
    scrape_and_store()
    time.sleep(30)
