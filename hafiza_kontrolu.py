import pandas as pd
import sqlite3
conn = sqlite3.connect('emlak_verisi.db')
print(pd.read_sql_query("SELECT * FROM talepler", conn))