# academic-research-tracker
Türk üniversitelerindeki akademik personelin araştırmalarını HTML formatında dökümünü hazırlayan Python betiği. Bölümlerin akademik çalışmalar sekmelerinde kullanılabilir. Betiği kullanmanız halinde HTML meta tag ile referans vermeniz rica olunur.

```html
<meta name='author' content='ahmetkasif'>
```

Girdiler:

- university_name : Üniversitenin YÖK Akademik sayfasındaki ad karşılığı, Örn: "BURSA TEKNİK ÜNİVERSİTESİ" 
- faculty_name : Fakültenin YÖK Akademik sayfasındaki ad karşılığı, Örn: "MÜHENDİSLİK VE DOĞA BİLİMLERİ FAKÜLTESİ FACULTY OF ENGINEERING AND NATURAL SCIENCES"
- department_name : Bölümün YÖK Akademik sayfasındaki ad karşılığı, Örn: "BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ null" 
- min_year : Hangi yıldan itibaren arama yapılacağı, Örn: 2021 
- exc_delay : İstekler arasındaki bekleme süresi, Örn: 0.2 (sn)

Çıktı:

- Bölümde gerçekleştirilen çalışmaların liste yapısında HTML kodu.

Projenin HTML kodunun stil tasarımında destek olan [Abdullah Öğük](https://github.com/abdullahoguk)'e teşekkür ederim.
