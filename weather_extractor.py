import fitz
import numpy as np
import pandas as pd
from pathlib import Path
import requests
from datetime import datetime


pdf_file = 'https://mausam.imd.gov.in/thiruvananthapuram/mcdata/dwr2.pdf'
now = datetime.now()
date_time = now.strftime("%d_%m_%Y-%H_%M")
filename = Path(f'files/{date_time}.pdf')
response = requests.get(pdf_file)
f0 = filename.write_bytes(response.content)

doc = fitz.open(filename)
dictionary_elements = doc[0].get_textpage().extractDICT()
data = []
for block in dictionary_elements['blocks']:
    for line in block['lines']:
        line_text = ''
        for span in line['spans']:
             line_text += ' ' + span['text']
        data.append(line_text)
srts = ['Alappuzha', 'CIAL', 'Kochi', 'Kannur', 'Karipur', 'Kottayam',
        'Kozhikode', 'Palakkad', 'Punalur', 'hapuram', 'Vellanikara',
        'Agathi', 'Aminidivi', 'Kavaratti', 'Minicoy']
extracted = []
for line in data:
    if any(word in line for word in srts):
        extracted.append(line.lstrip().rstrip().\
            replace('hapuram', 'Trivandrum').\
            replace('CIAL Kochi', 'CIAL_Kochi').\
            replace(' AP','_AP').replace(' City', '_City'))
cols = ['PLACE', 'TEMP_MAX_PAST_24HR', 'TEMP_MAX_DEP_NORMAL',
        'TEMP_MIN_PAST_24HR', 'TEMP_MIN_DEP_NORMAL',
        'HUMID_0830_IST_PERCENT', 'HUMID_DEP_NORMAL_PERCENT',
        'RAIN_PAST_24HR_MM', 'RAIN_SEASN_TOT_FROM_JAN_1_MM',
        'RAIN_DEP_NORMAL_CM', 'RAIN_TOT_FRM_1JAN_CM',
        'RAIN_ANNUAL_NORMAL_CM', 'WTHR_REM']

with open(f"{filename}.txt", 'w') as file:
    for line in extracted:
        file.write(line + "\n")

df = pd.read_csv(f"{filename}.txt", sep=r'\s+', names=cols)
df.replace('-', np.nan, inplace=True)
df.RAIN_ANNUAL_NORMAL_CM = pd.to_numeric(df.RAIN_ANNUAL_NORMAL_CM,
                                         errors='coerce')
df.drop(columns=['WTHR_REM'], inplace=True)
df.set_index('PLACE', inplace=True)
df.to_json("output/output.json")
df.to_csv(f"output/{date_time}.csv")
