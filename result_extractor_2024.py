import pandas as pd
import fitz
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def download_pdf(url, payload, student_name):
    retry_count = 3  # Number of times to retry the request
    for _ in range(retry_count):
        try:
            with requests.Session() as session:
                response = session.post(url, data=payload, verify=False, timeout=10)
                response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
                with open(f'{student_name}.pdf', 'wb') as f:
                    f.write(response.content)
                print(f'Saved {student_name}.pdf')
                return True  # Return True if download is successful
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            # Retry the request
            continue
    else:
        print(f"Failed to download PDF file for {student_name}")
        return False  # Return False if download fails after retries

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('namelist3.csv')

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    seat_no = row['Seat No']
    mother_name = row['Mother Name']
    student_name = row['Student Name']

    # Create a new session for each request
    url = 'https://onlineresults.unipune.ac.in/Result/Dashboard/ViewResult1'
    payload = {
        # 'PatternID': '6Qw72CLlcXSacHyT9a7RkQ==', # Jan 2024
        # 'PatternName': 'RP+zm4rXwFDLUrTpUWU4sAabjAKzjboZ1oOi7r/VvOdAOz6ZfVn8Daoa4awR8XDV', # Jan 2024
        'PatternID' : '6Qw72CLlcXSacHyT9a7RkQ==', # June 2024
        'PatternName': 'RP+zm4rXwFDLUrTpUWU4sEa3GhqzYZU+2WOHorilLYgi2RQ6OKyRcE4pLb5zFaQ9', # June 2024
        'SeatNo': seat_no,
        'MotherName': mother_name
    }

    if not download_pdf(url, payload, student_name):
        # Handle the case where the download fails, e.g., log the failure
        pass

    # time.sleep()
