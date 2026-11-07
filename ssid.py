import requests
import re
from urllib.parse import urlparse, parse_qs, urljoin
import urllib3

urllib3.disable_warnings() # SSL Warning မတက်အောင်

CHECK_URLS = [
    "http://connectivitycheck.gstatic.com/generate_204",
    "http://captive.apple.com/hotspot-detect.html",
    "http://www.msftconnecttest.com/connecttest.txt"
]

def get_sid_from_portal(gateway_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36'
    }
    
    try:
        print(f"\n[*] Gateway ကို ချိတ်ဆက်နေသည်...")
        
        # လင့်ခ်က အတိုချုံး (/api/... လို) ဖြစ်နေရင် အပြည့်အစုံ ပြန်လုပ်မယ်
        if gateway_url.startswith('/'):
            parsed = urlparse(gateway_url)
            params = parse_qs(parsed.query)
            if 'gw_address' in params:
                gw_ip = params['gw_address'][0]
                gateway_url = f"http://{gw_ip}{gateway_url}"
                print(f"[*] လင့်ခ်အပြည့်အစုံ ပြန်လုပ်ပြီး: {gateway_url}")

        session = requests.Session()
        r2 = session.get(gateway_url, headers=headers, timeout=10, verify=False, allow_redirects=True)
        
        final_url = str(r2.url)
        
        # JS Redirect ရှိသေးရင် ရှာမယ်
        match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r2.text)
        if match:
            next_url = match.group(1)
            if next_url.startswith('/'):
                # နောက်တစ်ဆင့် အတိုချုံးဖြစ်နေရင်လည်း အပြည့်အစုံ ပြန်လုပ်မယ်
                base_url = urlparse(final_url)
                next_url = f"{base_url.scheme}://{base_url.netloc}{next_url}"
                
            final_url = str(session.get(next_url, headers=headers, timeout=10, verify=False).url)

        # sessionId ကို ရှာမယ်
        parsed_query = parse_qs(urlparse(final_url).query)
        sid = parsed_query.get('sessionId', parsed_query.get('sid', [None]))[0]
        
        if sid:
            print("\n" + "="*40)
            print("✅ SID ရပါပြီ!")
            print(f"Session ID: {sid}")
            print("="*40)
            print("\n👇 အောက်ပါ Link ကို Copy ကူးပြီး Bot ထဲက SID Mode မှာ ထည့်ပါ:")
            print(f"{final_url}\n")
            return True
        else:
            print("\n❌ SID မတွေ့ပါ။")
            print(f"နောက်ဆုံးရောက်သွားတဲ့ Link: {final_url}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def auto_detect_portal():
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'}
    print("🔍 Wi-Fi Portal ကို အလိုအလျောက် ရှာဖွေနေသည်...\n")
    
    for url in CHECK_URLS:
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=False, verify=False)
            portal_url = None
            
            if response.status_code in [301, 302, 303, 307, 308]:
                portal_url = response.headers.get('Location')
            elif response.status_code == 200:
                match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", response.text)
                if match:
                    portal_url = match.group(1)
            
            if portal_url:
                # တွေ့တဲ့ လင့်ခ်ကို ဆက်ပြီး စစ်မယ်
                if get_sid_from_portal(portal_url):
                    return
                        
            elif response.status_code == 204:
                print("⚠️ ဒီ Wi-Fi က အင်တာနက် ရနေပြီးသား ဖြစ်နေပါတယ်။ (Portal မရှိပါ)")
                return
                
        except Exception:
            continue
            
    print("\n❌ Portal လင့်ခ်ကို ရှာမတွေ့ပါဘူး။")
    print("💡 သေချာစစ်ဆေးပါ - ဖုန်းက Wi-Fi နဲ့ ချိတ်ဆက်ထားရပါမယ်။ Login မဝင်ရသေးတဲ့ အခြေအနေ ဖြစ်ရပါမယ်။")

if __name__ == "__main__":
    auto_detect_portal()