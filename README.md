# SPPU Result Extractor
This simple python script uses the provided csv file containting the Seat No, Student Name and Mother Name to download the results on a mass scale. You can download SPPU results of hundreads or thousands of students. This script is currently working on only single thread and could be adjusted to work on multiple thread to save time and make requests in parallel. 

I use SPPU [official website](http://unipune.ac.in/)'s backend api to download these results. This is not an intended functionality of this api.

This could be illegal due to excesive stress on unipune server and this script is only for demonstration puposes.

Use it at your own risk.

Anyways, heres how to use it

# Usage

- Go to unipune [result page](https://onlineresults.unipune.ac.in/Result/Dashboard/Default)
- Open your dev tools and navigate to the networks tab
- Click on "Go for Results" on the course you want to extract results from
- A "ViewResultpop" request would be sent, click on that request in network tab
- Navigate to "Payload"
- Copy the PatternName and PatternID values and paste them into the script at respective positions
- Start the script, This will start downloading results in current folder.

I recommend you not do this, this is probably illegal.

# Todo list
- [x] Implement course selection from user at start
- [ ] Get the pattern id and pattern name automatically
- [x] Make script run in parallel
- [x] Download the results in specified folder or create a folder to store results

---

# Update — 2026 (by [@ajjuu04](https://github.com/ajjuu04))

The old script (`result_extractor_2024.py`) no longer works because SPPU redesigned their result system.

Back in **2024**, it was simple — one API call and you got the PDF:

```
PatternID + PatternName + SeatNo + MotherName
        ↓
ViewResult1
        ↓
PDF
```

The new system (as of **2026**) now looks like this:

```
ViewResultpop
        ↓
HTML popup form
        ↓
RFCTLN  (AJAX call)
        ↓
Captcha image + hidden encrypted captcha token (OrgCaptchaText)
        ↓
User enters captcha
        ↓
VALCHCT  (AJAX validation)
        ↓
Final form POST to /SPPU ONLINE RESULT DISPLAY
        ↓
PDF result page
```

SPPU added a **server-generated CAPTCHA** to prevent automated bulk requests. Honestly? Good on them. It shows the organisation is actively maintaining and securing their application. The CAPTCHA is a numeric-only 5-digit image on a grid background — which the updated script handles automatically using OCR.

## What the updated script does

The script will:
1. Connect to the SPPU server
2. Automatically solve the CAPTCHA using OCR (`ddddocr`)
3. Download each student's result as a PDF into the `downloaded result pdf\` folder
4. Show a success/failure count at the end

If the auto-OCR fails for a particular CAPTCHA, it will open the image and ask you to type it manually — then continue automatically from there.

## Requirements

```bash
pip install pandas requests PyMuPDF ddddocr pillow openpyxl
```

## How to run

```bash
python result_extractor_2026.py
```

Before running, open `result_extractor_2026.py` and update these two lines with the values from the network tab (same as before):

```python
PATTERN_ID   = 'paste PatternID here'
PATTERN_NAME = 'paste PatternName here'
```
