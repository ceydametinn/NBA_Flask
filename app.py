from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# 1. Eğitilmiş Modeli Yükle
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # --- KULLANICIDAN VERİLERİ AL ---
            age = float(request.form['age'])
            # mp (Dakika) ve ast (Asist) modelden elendiği için almıyoruz/kullanmıyoruz.
            
            fga = float(request.form['fga'])    # Toplam Şut Denemesi
            fta = float(request.form['fta'])    # Serbest Atış
            trb = float(request.form['trb'])    # Ribaund
            
            pos_secimi = request.form['position'] # Seçilen Pozisyon
            
            # --- DATA MÜHENDİSLİĞİ (Modelin Anlayacağı Dile Çevirme) ---
            
            # 1. FGA'yı Parçala (Çünkü model 3PA ve 2PA istiyor)
            # Varsayım: Şutların %35'i üçlük, %65'i ikiliktir (Modern NBA ortalaması)
            pa3 = fga * 0.35 
            pa2 = fga * 0.65

            # 2. Pozisyonları Ayarla (One-Hot Encoding)
            # Modelde sadece Pos_PG, Pos_SF ve Pos_SG sütunları kaldı.
            # Diğerleri (PF ve C) modelden atıldığı için hepsi 0 olacak.
            
            pos_pg = 0
            pos_sf = 0
            pos_sg = 0
            
            if pos_secimi == 'PG':
                pos_pg = 1
            elif pos_secimi == 'SF':
                pos_sf = 1
            elif pos_secimi == 'SG':
                pos_sg = 1
            # PF veya C seçilirse hepsi 0 kalır (Base Case)

            # --- TAHMİN ---
            # Modelin beklediği tam 8 özellik sırasıyla:
            # [Age, 3PA, 2PA, FTA, TRB, Pos_PG, Pos_SF, Pos_SG]
            
            final_features = np.array([[age, pa3, pa2, fta, trb, pos_pg, pos_sf, pos_sg]])
            
            prediction = model.predict(final_features)
            output = round(prediction[0], 2) # Sonucu yuvarla

            return render_template('index.html', prediction_text=f'🏀 Tahmini Puan: {output} Sayı')

        except Exception as e:
            return render_template('index.html', prediction_text=f'Hata: {str(e)}')

if __name__ == "__main__":
    app.run(debug=True)