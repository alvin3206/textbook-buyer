import pandas as pd
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

df = pd.read_csv(r'Book-Data-Sheet1.csv')
isbn_lib = df['ISBN/ID'].tolist()
temp_lib = isbn_lib[:]

for i in isbn_lib:
    if (len(i) != 10) and (len(i) != 13) or i.isdigit() == False :
        temp_lib.remove(i)
