# Ama Neden? — Kurulum Rehberi

> Üçüncü kanal. Kod aynı, ayarlar ve senaryo kuralları farklı.
> **Bu projede yeni bir Gemini anahtarı kullanacaksın** — sebebi aşağıda.

---

## Neden yeni Gemini anahtarı?

Mevcut iki kanal günde 7 video üretiyor ve ikisi de aynı anahtardan hem senaryo
hem seslendirme çekiyor. Üçüncü kanal bu yükü taşıyamaz — kota dolarsa ses
otomatik olarak edge-tts'e düşer ve videolar farklı sesle çıkar.

Bu yüzden bu proje için **ayrı bir Google hesabından ayrı anahtar** alacaksın.

---

## Diğer kanallardan farklar

| | Çocuk | Meraklı Tarih | Ama Neden? |
|---|---|---|---|
| Saat | 08:00 | 11:00 | **14:00** |
| Gemini sesi | Puck | Aoede | **Kore** |
| Geçiş sesi | chime | whoosh | **pop** |
| Görsel stili | 3D çizgi film | Tarihsel resim | **Modern illüstrasyon** |
| Günlük | 4 video | 3 video | **3 video** |
| Gizlilik | public | private | **private** |

Saatler bilerek farklı — aynı anda çalışırlarsa kaynaklar çakışır.

---

## Kanalın çalışma mantığı

Her video tek bir "neden böyle?" sorusuna cevap verir. Konular farklı
alanlardan gelir ama hepsi aynı merakı besler — bu sayede YouTube algoritması
kanalı tanımlayabilir.

**Haftalık tema takvimi** (kod otomatik seçer):

| Gün | Alan |
|---|---|
| Pazartesi | Uzay |
| Salı | Doğa ve hayvanlar |
| Çarşamba | Coğrafya |
| Perşembe | Teknoloji, nasıl çalışır |
| Cuma | Çöküş hikayeleri |
| Cumartesi | İnsan, vücut, davranış |
| Pazar | Karışık |

Değiştirmek istersen `config.py` içinde `TEMALAR` sözlüğünü düzenle.

---

## Kurulum sırası

### 1. Klasörü yerleştir
`neden_otomasyon` klasörünü diğer projelerin yanına koy.

### 2. YouTube kanalını aç
1. youtube.com → profil → **Ayarlar** → **Kanal ekle veya yönet**
2. **Kanal oluştur** → adı: `Ama Neden?`
3. YouTube Studio → Özelleştirme → handle: `@amanneden`

### 3. Yeni Google hesabından Gemini anahtarı al
1. Tarayıcıda **gizli pencere** aç (Ctrl+Shift+N)
2. https://aistudio.google.com/apikey
3. Yeni hesapla giriş yap
4. **Create API key** → **Create API key in new project**
5. Anahtarı kopyala

### 4. `.env` dosyası oluştur

```
notepad .env
```

İçine:

```
GEMINI_API_KEY=AQ.yeni_anahtarin
GEMINI_MODEL=gemini-3.6-flash
SES_MOTORU=gemini
GEMINI_SESI=Kore
SFX_TIPI=pop
YOUTUBE_GIZLILIK=private
MOCK=0
```

Test et:

```
python teshis.py
```

### 5. Müzik ekle
`assets/music` klasörü boş. YouTube Studio > Ses Kitaplığı'ndan indir.
Bu kanal için uygun türler: *upbeat*, *curious*, *light electronic*, *modern*.
Tarih kanalının ağır müzikleri burada yakışmaz.

### 6. client_secret.json'ı kopyala
Tarih projesinden bu projenin `data` klasörüne kopyala. Aynı Google Cloud
projesi üç kanal için de çalışır.

### 7. YouTube yetkilendirmesi

```
python main.py --youtube-giris
```

Tarayıcıda **Ama Neden? kanalını** seç. Konsolda `Bagli kanal: Ama Neden?`
yazdığını doğrula.

### 8. İlk video

```
python main.py --tip shorts
```

### 9. GitHub kurulumu
`GITHUB_KURULUM.md` adımlarının aynısı, ayrı bir depo ile (`ama-neden` gibi).
Secrets'ı yeniden eklemen gerekir — hem Gemini anahtarı hem YouTube token'ı farklı.

---

## Bilmen gerekenler

**Videolar private yükleniyor.** Kontrol edip elle yayına alacaksın. Kaliteden
emin olunca `config.py`'de `YOUTUBE_GIZLILIK = "public"` yaparsın.

**Doğruluk katmanı aktif.** "Dünyanın ilk", "tam 3.472 kişi" gibi kanıtlanması
zor iddialar otomatik yumuşatılıyor. Ama olgunun kendisi yanlışsa yakalayamaz —
ara sıra örnekleme yap.

**Soyut konularda görsel zorlanır.** "Yerçekimi neden var" gibi bir konuda
görsel üretici iyi sonuç vermeyebilir. Somut sahne tarif etmesi için kurallara
talimat koydum ama her zaman tutmayabilir.
