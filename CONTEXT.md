# CONTEXT.md — Chrono-Macro-Lab

> **GELİŞTİRİCİ NOTU / KAPSAM UYARISI**
> Bu dosya yalnızca insan geliştiriciler içindir. Hiçbir model girdisine, kaynak havuzuna,
> prompt'a, retrieval indeksine veya veri hattına **dahil edilmez**. Burada yazan hiçbir şey
> "tarihsel kanıt" sayılmaz.
>
> Bölüm 8 kuralı: Bu dosyaya cutoff sonrası gerçek bilgi yazılmaz. Metinde geçen tüm örnekler
> **varsayımsaldır** ve açıkça "(varsayımsal örnek)" diye işaretlenir. Hiçbir yerde gerçek
> gelecek olayı, gerçek sonuç veya gerçek piyasa verisi iddia edilmez.

---

## 1. Projenin amacı

Chrono-Macro-Lab, haber okuyup doğrudan "BUY / SELL" sinyali üreten klasik bir Forex botu
**değildir**. Amaç, ekonomik, politik, jeopolitik, ticari ve finansal olayları zaman içinde
birbirleriyle ilişkilendirebilen bir **araştırma sistemi** kurmaktır.

Sistem, verilen bir tarih itibarıyla dünyanın durumunu mümkün olduğunca yeniden kurar ve
**yalnızca o tarihte gerçekten erişilebilir olan bilgiyle** ileriye dönük hipotezler üretir.
Olaylar tek tek haberler olarak değil, birbirine bağlı zincirler olarak ele alınır. Temsilî
zincir şeması (kavramsal, veri değil):

```
politika / düzenleme kararı
  → ihracat veya ticaret kısıtı
  → tedarik zinciri etkisi
  → şirketler ve sektörler
  → ticaret akışları
  → büyüme / enflasyon
  → merkez bankası politikası
  → faiz farkları
  → döviz piyasaları
```

Forex, bu araştırmanın **ilerideki olası uygulama alanlarından biri** olabilir. Şu an işlem,
kaldıraç, para yönetimi ve gerçek para kullanımı tamamen kapsam dışıdır.

---

## 2. Temel deney mantığı

Projenin çekirdek fikri iki cümlede özetlenir:

```
GEÇMİŞ  = CEVAP ANAHTARI
GELECEK = SINAV
```

Bir **cutoff** tarihi seçilir (varsayılan: `2010-12-31`). Sistem:

1. cutoff anında erişilebilir bilgiden bir **dünya durumu** kurar,
2. cutoff sonrası dönem için **ölçülebilir tahminler** üretir,
3. gerçekleşen veri **cevap anahtarı** olarak, yalnızca değerlendirme aşamasında devreye girer,
4. tahmin ile gerçekleşme karşılaştırılır.

Bu deney farklı cutoff tarihleriyle (örneğin `2010-12-31`, `2013-12-31`, `2016-12-31`)
tekrarlanabilir olmalıdır. Aynı kod, farklı cutoff ile çalıştırılabilmelidir; cutoff koda
gömülmez, yapılandırmadan gelir (`config.yaml`).

---

## 3. "2010 modeli" ne demek?

"2010 modeli" yalnızca modele 2010 adını vermek değildir. Modelin **bilgi ortamı** cutoff ile
sınırlandırılmıştır. İdeal hedef, zamansal olarak izole edilmiş bir tarihsel dil modelidir;
araştırmada ChronoGPT / ChronoGPT-Instruct gibi kronolojik olarak sınırlandırılmış, **hazır**
(sıfırdan eğitilmeyecek) modeller incelenmektedir.

Kabul edilen gerçek şudur: böyle bir modelin ağırlıklarında bazı tarihsel bilgiler eksik
olabilir. Bu yüzden modelin tüm tarihsel bilgiyi kendi parametrelerinde taşıması beklenmez.
Eksik bilgi, **kapalı ve kilitli bir kaynak havuzundan** (retrieval) tamamlanır.

Kritik ayrım:

| Katman | İşlev |
|---|---|
| Model ağırlıkları | cutoff öncesiyle sınırlı örtük bilgi |
| Kapalı kaynak havuzu | cutoff öncesi kamuya açılmış birincil kaynaklar (retrieval) |
| İnternet | **yok** — backtest sırasında modelin dış erişimi kapalıdır |

---

## 4. Tarihsel bilgi havuzu ve seçim sızıntısı

Havuz, tarihi doğrulanabilir birincil kaynaklardan (haber arşivleri, merkez bankası yayınları,
resmî veri sürümleri vb.) **mekanik ve kural tabanlı** olarak toplanır: cutoff tarihinden önce
kamuya açılmış her şey alınır. Kural koddur, yorum değildir.

**Yasak:** Hangi kaynağın "önemli" olduğuna, neyin alınıp neyin eleneceğine güncel bir LLM
karar veremez. Güncel modeller sonucu bildiği için farkında olmadan doğru delilleri öne
çıkarıp yanlış izleri eleyebilir — yani **"katil bilinerek çizilmiş cinayet panosu"** etkisi.
Bu bir **seçim sızıntısıdır** (selection leakage) ve yalnızca koda tarih kontrolü eklemek bunu
çözmez; çünkü sızıntı verinin kendisinde değil, **seçim kararında** oluşur.

Özetleme, olay çıkarımı ve ilişkilendirme işi **2010 modelinin** görevidir; güncel LLM'lerin
değil.

### Cinayet soruşturması benzetmesi

| Soruşturma | Projedeki karşılığı |
|---|---|
| Deliller | Tarihsel kaynaklar (kapalı havuz) |
| Vaka kayıtları | Çıkarılmış olaylar |
| Bağlantılar | Olaylar arası ilişkiler |
| Olay panosu | Dünya durumu (world state) |
| Dedektif | cutoff ile sınırlı tarihsel model |
| Henüz çözülmemiş olay | cutoff sonrası dönem (sınav) |
| Cevap anahtarı | Gerçekleşen sonuçlar (`data/answer_key/`) |

---

## 5. Zaman ayrımı: iki (ve ileride üç) zaman alanı

Her veri kaydında en az iki farklı zaman tutulur:

- **`event_time`** — olayın gerçekte gerçekleştiği zaman. *Bilgi değeri:* bağlam.
- **`available_time`** — bilginin kamuya açık hale geldiği zaman. *Bilgi değeri:* erişim sınırı.
- **`source_date`** — kaynağın kendi tarih damgası (yayın tarihi). *Bilgi değeri:* yardımcı kontrol.

Bir olay 10 Aralık'ta gerçekleşip haberi 11 Aralık'ta yayınlanmış olabilir. Model 10 Aralık'ta
bu bilgiyi **bilemez**. Bu yüzden filtreleme esas olarak **`available_time` üzerinden** yapılır.

Ek olarak veri revizyonları için ileride **vintage** (bir serinin ilk yayınlanan hâli) bilgisi
tutulması gerekebilir: bugün görülen "geçmiş" veri, geçmişte yayınlanan veriden farklıdır
(revizyonlar). Vintage tutulmadan yapılan bir geri test, revize edilmiş geleceği geçmişe
sızdırır.

---

## 6. Zamansal sızıntı (look-ahead bias)

En önemli teknik problemdir. Cutoff `2010-12-31` ise model şunları **görmemelidir**:

- cutoff sonrası haberler,
- cutoff sonrası analizler,
- sonradan geriye dönük yazılmış tarihsel değerlendirmeler,
- bugünkü hâline göre güncellenmiş maddeler (örneğin sürekli düzenlenen ansiklopedi sayfaları),
- gelecekteki olayları içeren veri setleri ve revize edilmiş veri serileri.

**"2010 hakkında yazılmış olması" bir kaynağı geçerli yapmaz.** Bir metin 2010'da olanları
anlatıyor olsa bile, yazıldığı tarih cutoff'tan sonraysa modele verilemez. Örnek (varsayımsal):

> "(varsayımsal örnek) 20XX'te yazılmış bir metin: '2010'da A oldu, bunun sonucunda 2011'de B
> gerçekleşti.' Bu metin 2010 cutoff'lı bir koşuya **girmez**, çünkü cutoff anında B henüz
> bilinmiyordu; metin B'yi içerdiği için sızıntı taşır."

İlke: geçerlilik, anlatılan döneme değil **kamuya açılma anına** göre belirlenir.

---

## 7. Roller ve yetki sınırları

### Güncel LLM'ler (bu projeye katkı veren ajanlar dâhil) — YALNIZCA KOD

- veri çekme/indirme altyapısı yazmak (yalnızca istenen aşamada),
- filtreleme, doğrulama ve test kodu,
- şema ve altyapı kodu,
- değerlendirme (eval) kodu ve metrikler.

### Güncel LLM'lerin **YAPMADIKLARI**

- tarihsel içerik seçmek veya elemek,
- tarihsel kaynakları özetlemek,
- "hangi olay önemli" diye karar vermek,
- cutoff sonrası dönem hakkında tahmin, yorum veya değerlendirme üretmek,
- bir kaynağın "2010'a ait" olduğunu kendi yargısıyla onaylamak.

### Uygulama kuralı

Tarih filtresi **daima kod tarafından**, programatik alanlar üzerinden uygulanır:

```
source_date , available_time , event_time
```

Varsayılan davranış **fail-closed**: gerekli zaman alanı eksik veya ayrıştırılamıyorsa kayıt
**havuza alınmaz**. "Muhtemelen eskidir" gerekçesiyle hiçbir kayıt elle içeri alınmaz.

---

## 8. Modelin internet erişimi ve doküman kuralı

- Backtest/historical aşamasındaki tarihsel modelin **internet erişimi yoktur**. Model yalnızca
  kendisine verilen kapalı havuzla çalışır. Böylece "2010 modeli → internet → bugünün bilgisi"
  şeklinde bir zaman atlaması teknik olarak imkânsız hâle gelir.
- `CONTEXT.md` ve `docs/` klasörü **yalnızca geliştirici içindir**; model girdisine, kaynak
  havuzuna veya veri hattına dâhil edilmez.
- Bu dosyalara cutoff sonrası **gerçek** bilgi yazılmaz. Örnekler varsayımsal olarak işaretlenir.
- Aynı kural, gelecekte yazılacak geliştirici notları, tasarım belgeleri ve commit mesajları
  için de geçerlidir.

---

## 9. Cevap anahtarı

Cutoff sonrası gerçekleşen veriler ayrı tutulur: **`data/answer_key/`**.

- Model tahmin üretirken bu dizindeki hiçbir şey okunamaz.
- Bu veriler yalnızca **değerlendirme** aşamasında kullanılır.
- Erişim, kod düzeyinde ayrılmalıdır: tahmin hattı `data/answer_key/` yolunu hiçbir zaman
  açmamalıdır; bu, testlerle doğrulanacak bir invaryanttır.

Varsayımsal örnek (gerçek veri değildir):

> Model çıktısı: "İlgili merkez bankasının önümüzdeki 6 ayda politika faizini artırma
> olasılığı: %65." (varsayımsal)
> Cevap anahtarı: "Faiz artırıldı." (varsayımsal)
> Bu eşleşme yalnızca değerlendirme sistemine girer; tahmin aşamasında görünmez.

---

## 10. Değerlendirme

Tahminler mümkün olduğunca **ölçülebilir ve net çözülebilir** sorulara dönüştürülür. Soru
biçimi örneği (varsayımsal): *"X merkez bankası 3 ay içinde politika faizini artırır mı?"*

Binary/olasılıksal hedefler için:

- **Brier score** (ve gerekirse log-loss / kalibrasyon eğrileri),
- çözülemeyen veya belirsiz kalan soruların ayrı raporlanması.

Baseline karşılaştırmaları (model bunlardan anlamlı biçimde iyi olmalı):

- geçmiş taban oran (base rate),
- random-walk benzeri naif baseline,
- piyasanın ima ettiği olasılık (cutoff anında erişilebilir olan).

Asıl soru "model doğru bildi mi?" değil:

> **Model olasılıklarını gerçekten kalibre edebiliyor mu ve basit yöntemlerden anlamlı biçimde
> daha iyi mi?**

Sızıntı testleri baştan sisteme dâhildir: cutoff sonrası bir **"kanarya" belgenin** filtreden
geçmediğini doğrulayan testler yazılacaktır. Aynı sistem farklı cutoff yıllarında çalışabilmeli,
dolayısıyla testler de cutoff'ı yapılandırmadan almalıdır.

---

## 11. Araştırma aşamaları (yol haritası)

Durum: **hiçbiri uygulanmadı.** Aşağıdaki liste yalnızca plan kaydıdır.

| # | Aşama | Durum |
|---|---|---|
| 1 | Point-in-time veri altyapısı | planlandı |
| 2 | Tarihsel kaynak havuzunun oluşturulması | planlandı |
| 3 | Zamansal izolasyonun doğrulanması | planlandı |
| 4 | Tarihsel modelin bilgi ortamına bağlanması | planlandı |
| 5 | Olay çıkarımı | planlandı |
| 6 | Olaylar arası ilişki grafiği | planlandı |
| 7 | Dünya durumu oluşturma | planlandı |
| 8 | Gelecek hipotezleri | planlandı |
| 9 | Olasılıksal tahmin | planlandı |
| 10 | Gerçekleşen sonuçlarla karşılaştırma | planlandı |
| 11 | Hata analizi | planlandı |
| 12 | (Gerekirse) Forex/piyasa tahmin katmanı | kapsam dışı / ertelendi |

**Şu anki aşama: 0 — yalnızca iskelet.** Bu aşamada internetten veri çekilmez, model
indirilmez, paket kurulmaz, scraper yazılmaz, dataset üretilmez.

---

## 12. Dizin düzeni ve veri bölgeleri

```
chrono-macro-lab/
├── data/
│   ├── raw/          # ham, işlenmemiş indirilen kaynaklar (henüz boş)
│   ├── pit/          # point-in-time katman: zaman alanları doğrulanmış, filtrelenmiş kayıtlar
│   └── answer_key/   # cutoff SONRASI gerçekleşmeler; tahmin hattı buraya erişemez
├── src/              # kaynak kod
├── tests/            # testler (öncelik: zamansal sızıntı testleri)
├── eval/             # değerlendirme kodu, metrikler, rapor çıktıları
├── docs/             # geliştirici dokümantasyonu (modele verilmez)
├── CONTEXT.md        # bu dosya (modele verilmez)
├── config.yaml       # cutoff ve koşu yapılandırması
└── README.md         # kısa amaç + mevcut aşama
```

Bölge kuralları:

- `raw/` → kaynağın indirildiği hâli; üzerine yazılmaz, türetilmez.
- `pit/` → yalnızca kural tabanlı filtrelerden geçmiş, zaman alanları doğrulanmış kayıtlar.
- `answer_key/` → tahmin hattı için **erişilemez bölge** (kod düzeyinde ayrılacak).

---

## 13. Bu depoda geçerli invaryantlar (özet kontrol listesi)

1. Cutoff koda gömülmez; `config.yaml`'dan gelir ve tüm filtreler onu kullanır.
2. Filtreleme `available_time` (ve `source_date`) üzerinden **kodla** yapılır; yargıyla değil.
3. Zaman alanı eksik kayıt varsayılan olarak **reddedilir** (fail-closed).
4. Tahmin hattı `data/answer_key/` içeriğini hiçbir koşulda okumaz.
5. Tarihsel modelin dış ağ erişimi yoktur; yalnızca kapalı havuz.
6. `CONTEXT.md` ve `docs/` hiçbir model girdisine, prompt'a veya indekse girmez.
7. Kaynak seçimi mekaniktir; güncel LLM'ler içerik seçmez, özetlemez, eleme yapmaz.
8. Sızıntı testleri (kanarya belgeler dâhil) kod tabanının parçasıdır, sonradan eklenen
   bir "kontrol" değildir.
9. Aynı kod farklı cutoff değerleriyle çalışabilir; koşular birbirinden izole edilir.
10. Gelecek dönem hakkında hiçbir gerçek iddia bu depoda (özellikle CONTEXT.md/docs içinde)
    kayıt altına alınmaz; örnekler varsayımsal olarak işaretlenir.

---

## 14. Kısa terimler sözlüğü

| Terim | Anlam |
|---|---|
| **cutoff** | Bilgi erişiminin kesildiği an; koşunun "şimdi"si |
| **available_time** | Bilginin kamuya açıldığı an; filtrelemenin ana ekseni |
| **event_time** | Olayın gerçekleştiği an |
| **source_date** | Kaynağın kendi yayın tarih damgası |
| **vintage** | Bir veri serisinin ilk yayınlanmış sürümü (revizyon öncesi) |
| **PIT (point-in-time)** | Yalnızca o anda erişilebilir bilgiyi temsil eden veri katmanı |
| **look-ahead bias** | Gelecekteki bilginin geçmişe sızması |
| **selection leakage** | Sızıntının veride değil, kaynak seçim kararında oluşması |
| **canary document** | Filtreden geçmemesi gereken, test amaçlı cutoff sonrası belge |
| **world state** | Cutoff anındaki olaylar ve ilişkiler bütünü ("olay panosu") |
| **Brier score** | Olasılıksal tahminlerin kalibrasyon/doğruluk metriği |

---

## 15. Mevcut durum

**Aşama 0 — iskelet.** Oluşturulan: klasör ağacı, `CONTEXT.md`, `config.yaml`, `README.md`,
`data/` bölge notu ve `tests/` altında zamansal sızıntı testleri için (henüz çalışmayan, hepsi
`skip` işaretli) iskelet.

Yapılmayanlar: veri indirme, internet erişimi, model indirme, paket kurulumu, scraper, dataset,
model eğitimi, tahmin üretimi.

Sonraki adım **kullanıcı talimatıyla** başlar; ajan kendi inisiyatifiyle ilerlemez.
