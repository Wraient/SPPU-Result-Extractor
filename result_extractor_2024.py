import pandas as pd
import os
import re
import base64

# Define the folder name
folder_name = "static"  # Static folder is needed while importing fitz for some reason

# Get the current working directory
current_directory = os.getcwd()
folder_path = os.path.join(current_directory, folder_name)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"Folder '{folder_name}' created at {folder_path}")
else:
    print(f"Folder '{folder_name}' already exists at {folder_path}")

import fitz
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Auto-OCR for captcha
try:
    import ddddocr
    from PIL import Image, ImageFilter, ImageOps
    import io
    ocr = ddddocr.DdddOcr(show_ad=False)
    AUTO_OCR = True
    print("[OCR] Auto-captcha solving enabled (ddddocr).")
except ImportError:
    AUTO_OCR = False
    print("[OCR] ddddocr not found. Will ask for captcha manually.")

# ------------------------------------------------------------------
# URLs
# ------------------------------------------------------------------
DASHBOARD_URL     = 'https://onlineresults.unipune.ac.in/Result/Dashboard/Default'
VIEWRESULTPOP_URL = 'https://onlineresults.unipune.ac.in/Result/Dashboard/ViewResultpop'
CAPTCHA_URL       = 'https://onlineresults.unipune.ac.in/Result/Dashboard/RFCTLN'
SUBMIT_URL        = 'https://onlineresults.unipune.ac.in/SPPU%20ONLINE%20RESULT%20DISPLAY'

PATTERN_ID   = 'oIX9rlBLNg9oDizOJav7YA=='
PATTERN_NAME = 'r0W+Lo2D7QF3GFDiMu8mqDPdWPTXxUcBtanGx+A5mlny11dSIrcktUTZ313YY8HQxmYIX7c6KCYawvYylWR+4nMUxAZ/lbvTFCGRQoAEkR44j71vAdGlHAN3bbJkKo/g'

BROWSER_HEADERS = {
    'User-Agent'     : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection'     : 'keep-alive',
}

# ------------------------------------------------------------------
# OCR helper: read digits from captcha image bytes
# ------------------------------------------------------------------
def solve_captcha_ocr(image_bytes):
    """Try to auto-read the captcha using ddddocr. Returns string of digits."""
    try:
        from PIL import Image, ImageFilter, ImageOps
        import io

        # Preprocess: grayscale + threshold to remove grid background
        img = Image.open(io.BytesIO(image_bytes)).convert('L')  # grayscale

        # Increase contrast: make text black, background white
        # Grid lines are lighter than digits so threshold removes them
        img = img.point(lambda p: 0 if p < 140 else 255, '1')
        img = img.convert('RGB')

        # Convert back to bytes for ddddocr
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        result = ocr.classification(buf.getvalue())

        # Keep only digits
        digits_only = re.sub(r'[^0-9]', '', result)
        return digits_only
    except Exception as e:
        print(f"  [OCR] Error during auto-solve: {e}")
        return ''

# ------------------------------------------------------------------
# Setup session
# ------------------------------------------------------------------
def create_session():
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)

    print("Step 1: Visiting dashboard to get session cookie...")
    try:
        r = session.get(DASHBOARD_URL, verify=False, timeout=15)
        print(f"  Status: {r.status_code}")
    except Exception as e:
        print(f"  Warning: {e}")

    print("Step 2: Calling ViewResultpop to establish exam context...")
    try:
        session.post(
            VIEWRESULTPOP_URL,
            data={'PatternName': PATTERN_NAME, 'PatternID': PATTERN_ID},
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer'         : 'https://onlineresults.unipune.ac.in/SPPU',
                'Content-Type'    : 'application/x-www-form-urlencoded; charset=UTF-8',
            },
            verify=False, timeout=15
        )
        print("  Done.")
    except Exception as e:
        print(f"  Warning: {e}")

    return session

# ------------------------------------------------------------------
# Fetch captcha from server
# ------------------------------------------------------------------
def fetch_captcha(session, script_dir):
    try:
        r = session.post(
            CAPTCHA_URL,
            data={},
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer'         : VIEWRESULTPOP_URL,
                'Content-Type'    : 'application/x-www-form-urlencoded; charset=UTF-8',
            },
            verify=False, timeout=15
        )
        data = r.json()
        org_captcha_text  = data.get('OrgCaptchaText', '')
        captcha_image_str = data.get('CaptchaImageSTR', '')

        if not org_captcha_text or not captcha_image_str:
            print(f"  Error: Bad captcha response: {data}")
            return None, None, None

        image_bytes = base64.b64decode(captcha_image_str)

        # Save captcha image (useful for debugging or manual fallback)
        img_path = os.path.join(script_dir, 'captcha.jpg')
        with open(img_path, 'wb') as f:
            f.write(image_bytes)

        return org_captcha_text, captcha_image_str, image_bytes

    except Exception as e:
        print(f"  Error fetching captcha: {e}")
        return None, None, None

# ------------------------------------------------------------------
# Download PDF for one student
# ------------------------------------------------------------------
def download_pdf(session, seat_no, mother_name, student_name, output_dir, script_dir):
    max_attempts = 5

    for attempt in range(1, max_attempts + 1):
        print(f"  [Attempt {attempt}] Fetching captcha...")
        org_captcha_text, captcha_image_str, image_bytes = fetch_captcha(session, script_dir)
        if not org_captcha_text:
            print("  Could not get captcha. Skipping student.")
            return False

        # Try auto OCR first
        captcha_answer = ''
        if AUTO_OCR:
            captcha_answer = solve_captcha_ocr(image_bytes)
            if captcha_answer and len(captcha_answer) == 5:
                print(f"  [OCR] Auto-read captcha: {captcha_answer}")
            else:
                print(f"  [OCR] Auto-read failed (got '{captcha_answer}'). Opening image for manual entry...")
                os.startfile(os.path.join(script_dir, 'captcha.jpg'))
                captcha_answer = input("  >> Type the 5-character captcha shown in the image: ").strip()
        else:
            # No OCR — open image and ask manually
            os.startfile(os.path.join(script_dir, 'captcha.jpg'))
            captcha_answer = input("  >> Type the 5-character captcha shown in the image: ").strip()

        if len(captcha_answer) != 5:
            print(f"  Captcha must be 5 characters (got '{captcha_answer}'). Retrying...")
            continue

        payload = {
            'PatternID'      : PATTERN_ID,
            'PatternName'    : PATTERN_NAME,
            'SeatNo'         : str(seat_no).strip(),
            'MotherName'     : str(mother_name).strip().upper(),
            'OrgCaptchaText' : org_captcha_text,
            'CaptchaImageSTR': captcha_image_str,
            'CaptchaText'    : captcha_answer,
        }

        try:
            response = session.post(
                SUBMIT_URL,
                data=payload,
                headers={
                    'Referer'     : VIEWRESULTPOP_URL,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept'      : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
                verify=False, timeout=30
            )

            if response.status_code != 200:
                title = re.search(r'<title>(.*?)</title>', response.text, re.DOTALL)
                err = title.group(1).strip() if title else response.text[:300]
                print(f"  Server error {response.status_code}: {err}")
                continue

            if b'%PDF' in response.content[:10]:
                out_path = os.path.join(output_dir, f'{student_name}.pdf')
                with open(out_path, 'wb') as f:
                    f.write(response.content)
                print(f"  [OK] Saved: {out_path}")
                return True
            else:
                title = re.search(r'<title>(.*?)</title>', response.text, re.DOTALL)
                page_title = title.group(1).strip() if title else "(no title)"
                print(f"  Not a PDF — Page: '{page_title}'. Likely wrong captcha. Retrying...")
                time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
            time.sleep(2)

    print(f"  [FAILED] Could not download PDF for {student_name} after {max_attempts} attempts.")
    return False

# ------------------------------------------------------------------
# Load CSV
# ------------------------------------------------------------------
script_dir  = os.path.dirname(os.path.abspath(__file__))
output_dir  = os.path.join(script_dir, 'downloaded result pdf')
os.makedirs(output_dir, exist_ok=True)

csv_path = os.path.join(script_dir, 'namelist.csv')
df = pd.read_csv(csv_path)
df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

print(f"\nLoaded {len(df)} student(s) from namelist.csv")
print(f"Columns: {list(df.columns)}")
print(f"PDFs will be saved to: {output_dir}")
print("----------------------------")

session = create_session()
print("----------------------------\n")

success_count = 0
fail_count    = 0

for index, row in df.iterrows():
    seat_no      = row['Seat No']
    mother_name  = row['Mother Name']
    student_name = row['Student Name']

    print(f"Processing [{index+1}/{len(df)}]: {student_name} (Seat No: {seat_no})")

    if download_pdf(session, seat_no, mother_name, student_name, output_dir, script_dir):
        success_count += 1
    else:
        fail_count += 1

    time.sleep(1)

print("\n===========================")
print(f"Done!  Success: {success_count}  |  Failed: {fail_count}")
print("===========================")
input("\nPress Enter to exit...")
