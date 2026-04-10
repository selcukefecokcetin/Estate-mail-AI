import pandas as pd

# Veriyi oku
df = pd.read_csv('temizlenmis_mailler.csv')

# Her niyet sınıfından kaç tane e-posta olduğunu say ve ekrana yazdır
print(df['Intent'].value_counts())