# Chrono-Macro-Lab

Zamansal olarak izole edilmiş bir **makro/jeopolitik araştırma sistemi** iskeleti.

Bu proje haber okuyup "BUY / SELL" sinyali veren klasik bir Forex botu değildir. Amaç;
ekonomik, politik, jeopolitik, ticari ve finansal olayları zaman içinde birbirleriyle
ilişkilendirmek, belirli bir tarih itibarıyla dünyanın durumunu yeniden kurmak ve **yalnızca o
tarihte kamuya açılmış bilgiyle** ileriye dönük, ölçülebilir hipotezler üretmektir.

```
GEÇMİŞ  = CEVAP ANAHTARI
GELECEK = SINAV
```

Bir **cutoff** tarihi seçilir (varsayılan `2010-12-31`); sistem cutoff anındaki bilgiyle
tahmin üretir, cutoff sonrası gerçekleşmeler ise yalnızca değerlendirme aşamasında
"cevap anahtarı" olarak kullanılır. Aynı kod farklı cutoff tarihleriyle çalıştırılabilir.

> **Kapsam dışı:** canlı işlem, kaldıraç, para yönetimi, gerçek para kullanımı, yatırım
> tavsiyesi. Bu bir araştırma altyapısıdır; Forex ileride yalnızca olası bir uygulama
> katmanıdır.

---

## Mevcut aşama: 0 — yalnızca iskelet

Bu depoda şu an **kod, veri, model veya bağımlılık yoktur**. Yapılan tek şey klasör/dosya
iskeletinin ve yapılandırmanın kurulmasıdır.

Henüz **yapılmayanlar** (bilinçli olarak): internetten araştırma, veri indirme, API kullanımı,
model indirme, Python paketi kurulumu (venv dâhil), scraper, dataset oluşturma, PDF üretimi,
model eğitimi, tahmin üretimi.

---

## Dizin yapısı

```
chrono-macro-lab/
├── data/
│   ├── raw/          # ham indirilen kaynaklar (henüz boş)
│   ├── pit/          # point-in-time katman: zaman alanları doğrulanmış kayıtlar (henüz boş)
│   └── answer_key/   # cutoff SONRASI gerçekleşmeler — tahmin hattı buraya erişemez
├── src/              # kaynak kod (henüz boş)
├── tests/            # testler — öncelik: zamansal sızıntı (look-ahead) testleri
├── eval/             # değerlendirme kodu ve koşu çıktıları
├── docs/             # geliştirici dokümantasyonu
├── CONTEXT.md        # projenin tam bağlamı (YALNIZCA geliştirici için)
├── config.yaml       # cutoff ve koşu yapılandırması
└── README.md         # bu dosya
```

---

## Temel kurallar (özet)

1. **Zaman ayrımı:** Her kayıtta `event_time` (olay ne zaman oldu) ve `available_time` (bilgi
   ne zaman kamuya açıldı) tutulur. Filtreleme **`available_time`** üzerinden yapılır.
2. **Zaman filtresi kodla uygulanır.** Bir kaynağın "cutoff'a ait" olduğuna güncel bir LLM
   kendi yargısıyla karar veremez; karar yalnızca programatik tarih alanlarına bakar.
3. **Fail-closed:** Zaman alanı eksik veya belirsiz kayıtlar havuza alınmaz.
4. **Seçim sızıntısı yasak:** Kaynak seçimi mekanik ve kural tabanlıdır. Güncel LLM'ler
   tarihsel içerik seçmez, elemez, özetlemez, "önem" sıralaması yapmaz.
5. **Kapalı havuz:** Backtest aşamasındaki tarihsel modelin internet erişimi yoktur; yalnızca
   kendisine verilen, cutoff ile kilitlenmiş kaynak havuzuyla çalışır.
6. **Cevap anahtarı ayrıdır:** `data/answer_key/` yalnızca değerlendirme aşamasında okunur.
7. **`CONTEXT.md` ve `docs/` modele verilmez.** Bunlar yalnızca geliştirici dokümanlarıdır ve
   hiçbir model girdisine, prompt'a veya retrieval indeksine dâhil edilmez.
8. **Sızıntı testleri baştan dâhil:** Cutoff sonrası "kanarya" belgelerin filtreden geçmediğini
   doğrulayan testler sistemin parçasıdır.

---

## Yapılandırma

`config.yaml` sistemin tek tarih kaynağıdır. Cutoff koda gömülmez:

```yaml
run:
  cutoff_date: "2010-12-31"
  cutoff_profiles:
    c2010: "2010-12-31"
    c2013: "2013-12-31"
    c2016: "2016-12-31"
```

Farklı bir dönemi çalıştırmak için yalnızca cutoff değiştirilir; aynı kod tabanı kullanılır.
Koşu çıktıları `run_id` (varsayılan `cutoff_<tarih>`) ile ayrıştırılır.

---

## Testler

`tests/` altında şu an **yalnızca zamansal sızıntı testleri için iskelet** bulunur
(`tests/test_temporal_leakage.py`). Testler işaretli (`skip`) durumdadır çünkü veri hattı ve
`src/` henüz yok. Veri katmanı geldiğinde bu testler gerçek kontrollere dönüştürülecektir.

---

## Geliştirici notu

`CONTEXT.md` projenin tam ve bağlayıcı bağlamını içerir; bu depoda çalışan herkes (insan veya
ajan) önce onu okumalıdır. Bu dosyalara cutoff sonrası döneme ait gerçek bilgi yazılmaz;
örnekler varsayımsal olarak işaretlenir.
