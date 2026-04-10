#!/bin/bash

# 1. Arka planda e-posta dinleyiciyi başlat (Sonundaki '&' işareti arka planda çalışmasını sağlar)
python email_dinleyici.py &

# 2. Ön planda Streamlit arayüzünü başlat

python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0