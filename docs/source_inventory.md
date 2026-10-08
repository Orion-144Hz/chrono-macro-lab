# Kaynak Envanteri — TASLAK

> **GELİŞTİRİCİ BELGESİ.** Bu dosya `docs/` altındadır ve **hiçbir model girdisine, prompt'a,
> kaynak havuzuna veya retrieval indeksine girmez** (bkz. `CONTEXT.md` §8).
>
> **Durum: TASLAK / DOĞRULANMAMIŞ.** Aşağıdaki kategori bilgileri ajanın genel bilgisinden
> yazılmıştır; hiçbiri bu projede test edilmemiş, hiçbir sağlayıcıya bağlanılmamış, hiçbir
> lisans okunmamıştır. Bu belgede **hiçbir URL, lisans şartı veya tarih uydurulmamıştır**;
> sayısal/tarihsel ayrıntılar bilerek belirsiz bırakılmıştır.
>
> **Zaman kuralı:** Bu belge cutoff sonrası **hiçbir olaydan, sonuçtan, ölçümden veya
> değerlendirmeden söz etmez.** Kategoriler yalnızca zaman damgası doğrulanabilirliği, vintage
> varlığı, cutoff anında kapsama ve erişim/lisans kriterlerine göre ele alınır.

---

## 0. Okuma kılavuzu ve işaretleme sözleşmesi

| İşaret | Anlamı |
|---|---|
| `DOĞRULANMADI` | Ajanın genel bilgisinden yazıldı; insan doğrulaması gerekir. Kesin bilgi gibi kullanılamaz. |
| `KULLANICI KARARI` | Ajanın veremeyeceği seçim. Sahibi insandır; gerekçesi yazılı olmalıdır. |
| `YER TUTUCU` | Şablon/örnek değer. Gerçek kaynak, gerçek veri veya gerçek tarih **değildir**. |
| `KURAL` | Proje kuralı (`CONTEXT.md` / `config.yaml`) — doğrulama gerektirmez, bağlayıcıdır. |

**Kapsam dışı bırakılan işler (bu belgede yapılmaz):** kaynak indirme, sağlayıcıya bağlanma,
lisans metni okuma, URL toplama, veri çekme, kod yazma, özet çıkarma, "hangi kaynak önemli"
değerlendirmesi yapma.

---

## 1. Seçim kriterleri (yalnızca bunlar)

Bir kaynağın envantere girip girmemesi **yalnızca** aşağıdaki dört kriterle belirlenir. Bu
kriterler kod tarafından, programatik alanlar üzerinden uygulanır `KURAL`.

| # | Kriter | Nasıl ölçülür (programatik) | Karar |
|---|---|---|---|
| K1 | Zaman damgasının doğrulanabilirliği | Kayıtta `available_time` alanı var mı, ayrıştırılabiliyor mu, kesinliği ne? | Alan yok/ayrıştırılamıyor → **reddet** (fail-closed) |
| K2 | Vintage / revizyon bilgisi | Cutoff anında yayımlanmış sürüm elde edilebiliyor mu? | Seri verisinde vintage yok → **reddet** veya `KULLANICI KARARI` ile kapsam dışı |
| K3 | Cutoff anında kapsama | Kaynağın kapsadığı dönem cutoff'u içeriyor mu? | Kapsamıyor → **reddet** |
| K4 | Erişim ve lisans uygunluğu | İnsan tarafından doğrulanmış lisans/erişim kaydı var mı? | Doğrulanmamış → **havuza alınmaz** |

**Yasak kriterler** (kullanılması açıkça yasaktır) `KURAL`:

- Bir kaynağı, cutoff sonrası dönemde ne olduğuna bakarak öne çıkarmak veya elemek,
- "Bu kaynak önemli/önemsiz" yargısı (önem, kesinlikle bir kabul kriteri değildir),
- Ajanın bir kaynağı kendi yargısıyla "cutoff'a ait" sayması,
- Geriye dönük yazılmış bir metni, konusu eski olduğu için geçerli saymak.

---

## 2. Envanter kaydı şeması (şablon)

Her kaynak için tek bir kayıt tutulur. Aşağıdaki değerler **`YER TUTUCU`**dur; gerçek kaynak
değildir.

| Alan | Tip | Açıklama |
|---|---|---|
| `inventory_id` | metin | Ör. `SRC-0000` `YER TUTUCU` |
| `category` | numaralı | Bu belgedeki 1–8 kategorilerinden biri |
| `provider_name` | metin | Sağlayıcı adı — **insan onayı olmadan doldurulmaz** `KULLANICI KARARI` |
| `content_scope` | metin | Kapsanan içerik türü |
| `coverage_start` | tarih | Kapsamanın başlangıcı — sağlayıcının kendi meta verisinden okunur |
| `coverage_end` | tarih | Kapsamanın bittiği nokta (varsa) |
| `timestamp_field` | metin | Kaynaktaki zaman alanı adı (ör. yayın anı, yakalama anı) |
| `timestamp_precision` | enum | `gun` / `saat` / `dakika` / `saniye` |
| `vintage_available` | bool | Cutoff anındaki yayımlanmış sürüm elde edilebiliyor mu? |
| `retro_edit_risk` | enum | `dusuk` / `orta` / `yuksek` |
| `access_method` | metin | Erişim biçimi — **doğrulanmadan yazılmaz** |
| `licence_status` | enum | `DOĞRULANMADI` / `doğrulandı (insan, tarih, kanıt)` |
| `leakage_risk` | enum | `dusuk` / `orta` / `yuksek` |
| `mitigation` | metin | Sızıntıyı düşüren önlem |
| `verification_status` | enum | `DOĞRULANMADI` / `doğrulandı` |
| `verified_by` / `verified_at` | metin / tarih | Doğrulayan insan ve tarih |
| `notes` | metin | Açık sorular, belirsizlikler |

---

## 3. Kategoriler

Her kategoride altı başlık vardır: içerik/kapsama, zaman damgası, vintage, geriye dönük
düzenlenme riski, erişim/lisans, sızıntı riski + önlem. **Tüm içerik bilgisi
`DOĞRULANMADI`.**

### 3.1 Resmî istatistik yayınları (vintage/revizyon arşivi olan veri tabanları dâhil)

- **İçerik ve kapsama başlangıcı:** Ulusal istatistik kurumları ve uluslararası kuruluşların
  makro serileri (millî gelir, fiyat endeksleri, işgücü, dış ticaret, sanayi üretimi vb.).
  Kapsama başlangıcı kuruma **ve seriye** göre değişir; bazı seriler uzun geçmişe, bazıları kısa
  geçmişe sahiptir. Bu belgede hiçbir seri için başlangıç tarihi iddia edilmez; her seri kendi
  meta verisinden programatik olarak okunur. `DOĞRULANMADI`
- **Zaman damgası:** İki ayrı zaman vardır ve karıştırılmamalıdır: (i) **referans dönemi**
  (verinin ait olduğu dönem), (ii) **yayın anı** (release). `available_time` **yayın anıdır**;
  referans dönemi asla `available_time` yerine geçmez `KURAL`. Kesinlik: yaygın olarak gün;
  bazı kurumlarda yayın saati de verilir (saat/dakika). `DOĞRULANMADI`
- **Revizyon / vintage:** Bazı kurumlar "ilk yayımlanan hâl" (vintage) veya gerçek-zamanlı
  arşiv sunar; birçok kamuya açık seri ise **yalnızca en güncel, revize edilmiş hâliyle**
  sunulur. `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Yüksek.** Revizyon olağan uygulamadır: hata düzeltmesi,
  mevsimsel düzeltme, metodoloji değişikliği, taban/referans yılı güncellemesi, kaynak
  değişimi. Bugün indirilen bir seri, cutoff anında yayımlanmış değerlerden farklı olabilir.
  `DOĞRULANMADI`
- **Erişim yöntemi ve lisans:** Çoğu resmî kurum verisi kamuya açık kabul edilir; ancak
  atıf/kullanım koşulları, toplu indirme sınırları ve API kuralları kurumdan kuruma değişir.
  **DOĞRULANMADI**
- **Sızıntı riski: ORTA** (vintage varsa **DÜŞÜK**, vintage yoksa **YÜKSEK**). *Gerekçe:*
  revizyon, cutoff sonrasında öğrenilen düzeltmeleri geçmiş değerlere taşır — bu, kaynağın
  "eski" olmasına rağmen sızıntı üretmesinin tipik yoludur. *Önlem:* yalnızca cutoff anında
  yayımlanmış sürüm (vintage) kabul edilir; vintage yoksa seri reddedilir (fail-closed) veya
  `KULLANICI KARARI` ile kapsam dışı bırakılır.

### 3.2 Merkez bankası faiz kararları, açıklamaları, tutanakları

- **İçerik ve kapsama başlangıcı:** Politika faizi kararları, karar metinleri, basın
  açıklamaları, toplantı tutanakları, konuşmalar, periyodik raporlar. Kurumsal arşivlerin
  derinliği kurumdan kuruma değişir; bazı kurumlar yalnızca yakın dönemi çevrimiçi tutar.
  `DOĞRULANMADI`
- **Zaman damgası:** Yayın anı damgalıdır. Karar açıklamaları genellikle gün + saat (bazı
  kurumlarda dakika) kesinliğindedir. Tutanak ve transkriptler karar/toplantı tarihinden
  **gecikmeli** yayımlanır: `event_time` = toplantı tarihi, `available_time` = yayım anı
  `KURAL`. Kesinlik: gün–saat (yaygın), dakika (bazı kurumlar). `DOĞRULANMADI`
- **Revizyon / vintage:** Birincil metinler genelde değişmez artefaktlardır (tarihli/sürümlü
  belge). Ancak: web sayfaları yeniden düzenlenebilir, "hazırlanan metin" ile "yapılan
  konuşma" farkı bulunabilir, transkriptler sonradan düzeltilebilir. `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Düşük–orta.** Metin düzeltmeleri, transkript revizyonu,
  sayfanın yeniden yayımlanması ve arşiv yeniden düzenlemeleri görülebilir. `DOĞRULANMADI`
- **Erişim yöntemi ve lisans:** Kurumun kendi yayın kanalı (web/duyuru/olası API). Çoğunlukla
  serbest erişim; atıf ve yeniden kullanım koşulları kuruma göre değişir. **DOĞRULANMADI**
- **Sızıntı riski: DÜŞÜK** (düzeltilmiş transkript veya sonradan güncellenmiş sayfa
  kullanılırsa **ORTA**). *Gerekçe:* karar anında yayımlanan birincil metin, o an erişilebilir
  olan bilginin en temiz örneğidir; risk esas olarak sonraki sürümlerden gelir. *Önlem:* ilk
  yayın artefaktının ham kopyası + içerik hash'i saklanır; sonraki sürümler ayrı kayıt olarak
  tutulur ve cutoff sonrası sürümler havuza alınmaz.

### 3.3 Piyasa fiyat serileri (döviz, faiz, tahvil getirisi, emtia)

- **İçerik ve kapsama başlangıcı:** Döviz kurları, kısa vadeli faiz oranları, tahvil getirileri,
  emtia fiyatları; çözünürlük günlük–dakika–tick arasında değişir. Kapsama derinliği sağlayıcıya
  ve ücretli/ücretsiz erişime göre değişir. `DOĞRULANMADI`
- **Zaman damgası:** Kesinlik en yüksek kategoridir (dakika–saniye). Ancak zaman dilimi ve
  **bar etiketleme kuralı** (bar başlangıcı mı, kapanışı mı) sağlayıcıya göre değişir ve
  meta veride açıkça yazılmadıysa yanlış hizalamaya yol açar. `KURAL`: `available_time` bir
  barın **kapanış anıdır**; bar başlangıcı asla kullanılmaz. `DOĞRULANMADI`
- **Revizyon / vintage:** Genellikle **yoktur**; sağlayıcılar geçmişi sessizce düzeltebilir
  (hatalı kayıt temizliği, kurumsal işlem düzeltmeleri, kaynak değişimi, seri birleştirme).
  Bazı sağlayıcılar düzeltme/sürüm notu yayımlar. `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Orta–yüksek.** Sessiz düzeltmeler + "bugün geçmişi
  indirme" pratiği doğrudan sızıntı üretir (cutoff sonrası düzeltilmiş değerler geçmişe yazılır).
  `DOĞRULANMADI`
- **Erişim yöntemi ve lisans:** Büyük ölçüde lisanslı/ücretli; yeniden dağıtım ve saklama
  koşulları kısıtlı olabilir. **DOĞRULANMADI**
- **Sızıntı riski: ORTA–YÜKSEK.** *Gerekçe:* seri "geçmiş" görünse de elde edildiği an
  itibarıyla düzeltilmiş olabilir; ayrıca bar hizalaması yanlışsa gelecek verisi kullanılmış
  olur. *Önlem:* yalnızca cutoff anında alınmış/arşivlenmiş anlık görüntüler kullanılır;
  "bugün indirilen geçmiş seri" kabul edilmez; zaman dilimi ve bar etiket kuralı meta veriye
  yazılır; ham dosya + hash saklanır.

### 3.4 Beklenti / konsensüs verisi (varsa)

- **İçerik ve kapsama başlangıcı:** Ekonomist anketleri, tahmin konsensüsü, piyasa ima
  olasılıkları. Kamuya açık arşiv derinliği genellikle sınırlıdır; çoğu içerik ticari
  sağlayıcıdadır. `DOĞRULANMADI`
- **Zaman damgası:** Anket **dönemi** ile **yayın anı** karışabilir; bazı sağlayıcılar yalnızca
  dönem etiketi verir, yayın saati/dakikası yoktur. Kesinlik: gün veya dönem; saat/dakika
  çoğunlukla yok. `DOĞRULANMADI`
- **Revizyon / vintage:** **Nadiren.** Geçmiş anketler sonradan derlenmiş arşivlerde
  görünebilir; "o dönemde yayımlanan" ile "bugün arşivde duran" aynı şey olmayabilir.
  `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Yüksek.** Arşivlerin sonradan derlenmesi, tanım/metodoloji
  değişikliği, örneklem yeniden ağırlıklandırması, sessiz revizyon. `DOĞRULANMADI`
- **Erişim yöntemi ve lisans:** Genellikle ücretli/abonelik; yeniden dağıtım yasak olabilir.
  **DOĞRULANMADI**
- **Sızıntı riski: YÜKSEK.** *Gerekçe:* zaman damgası zayıf, vintage yok, arşiv sonradan
  kurgulanmış olabilir; bu üçü birleşince "cutoff anında erişilebilir" iddiası
  kanıtlanamaz. *Önlem:* yalnızca cutoff öncesi yayımlandığı **damgasıyla kanıtlanabilen** anket
  dokümanı kabul edilir; kanıtlanamıyorsa K4/K1 kriterleri gereği kapsam dışı kalır
  (`KULLANICI KARARI`). Değerlendirmede "piyasanın ima ettiği olasılık" baseline'ı da aynı
  kısıtla ele alınır `KURAL`.

### 3.5 Kurumsal / düzenleyici bildirimler

- **İçerik ve kapsama başlangıcı:** Borsa bildirimleri, periyodik finansal tablolar, pay
  işlem bildirimleri, izahnameler, düzenleyici kararları. Platformların geçmiş derinliği
  farklıdır; bazıları yalnızca yakın dönemi çevrimiçi tutar. `DOĞRULANMADI`
- **Zaman damgası:** Bildirim/kabul anı genellikle tarih + saat olarak verilir; "hazırlanma",
  "gönderim" ve "yayımlanma" anları ayrı alanlar olabilir. `available_time` = kamuya açıldığı
  an `KURAL`. Kesinlik: gün–saat. `DOĞRULANMADI`
- **Revizyon / vintage:** Değişmez kayıt kültürü vardır; düzeltmeler genellikle **tadil/ek
  bildirim** olarak ayrı kayıt hâlinde gelir — bu, vintage ayrımını kolaylaştırır.
  `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Düşük–orta.** Platform yeniden yapılandırması, bağlantı
  ve dosya adı değişimi, yeniden yükleme; içerik düzeyinde sessiz değişiklik olasılığı daha
  düşüktür. `DOĞRULANMADI`
- **Erişim yöntemi ve lisans:** Kamuya açık kabul edilir; toplu indirme kısıtları ve kullanım
  koşulları kuruma göre değişir. **DOĞRULANMADI**
- **Sızıntı riski: DÜŞÜK–ORTA.** *Gerekçe:* yayım anı damgalı, tadil kaydı ayrı tutulabilen,
  görece değişmez kayıtlar. *Önlem:* bildirim damgası `available_time` olarak alınır; tadiller
  ayrı kayıt; ham dosya + hash saklanır.

### 3.6 Haber ajansı arşivleri

- **İçerik ve kapsama başlangıcı:** Ajans telleri/haberleri; olayların zaman damgalı kaydı.
  Arşiv derinliği ve ücretsiz erişim penceresi ajansa göre değişir. `DOĞRULANMADI`
- **Zaman damgası:** Yayın anı çoğunlukla dakika kesinliğinde verilir. Ancak canlı haber
  sayfaları **yerinde güncellenir**: ilk yayın damgası kaybolabilir, güncelleme damgası ilk
  yayın gibi görünebilir. Kesinlik: dakika (iddia), güvenilirlik koşullu. `DOĞRULANMADI`
- **Revizyon / vintage:** Genellikle **yok**; madde gövdesi yerinde değiştirilir. Bazı ajanslar
  düzeltme notu ekler, bazıları sessizce düzeltir. `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Yüksek.** Yerinde güncelleme, yeniden yayın, arşiv
  sayfalarının yeniden düzenlenmesi, içerik kaldırma. `DOĞRULANMADI`
- **Erişim yöntemi ve lisans:** Telifli; arşiv erişimi çoğunlukla ücretli/abonelik, yeniden
  dağıtım kısıtlı. **DOĞRULANMADI**
- **Sızıntı riski: YÜKSEK.** *Gerekçe:* kaynağın bugünkü hâli, cutoff anındaki hâlinden farklı
  olabilir ve bu fark sessizdir. *Önlem:* yalnızca **ilk görülme anında alınmış ham kopya +
  içerik hash'i** olan maddeler kabul edilir; yerinde değişen sayfalar için yalnızca
  `capture_time ≤ cutoff` olan tarihli anlık görüntüler kullanılır.

### 3.7 Web arşivi anlık görüntüleri

- **İçerik ve kapsama başlangıcı:** Herkese açık sayfaların tarihli kopyaları. Yakalama
  yoğunluğu yıllara ve sitelere göre çok değişir; bazı dönemler seyrek, bazı sayfalar hiç
  yakalanmamıştır. Arşivin başlangıç yılı burada iddia edilmez. `DOĞRULANMADI`
- **Zaman damgası:** **Yakalama (capture) anı** güvenilir biçimde damgalıdır; içeriğin ilk
  yayın anı bu damgadan **eski** olabilir. Yani yakalama anı, "en geç bu anda erişilebilirdi"
  demektir — muhafazakâr ve güvenli yöndür. Kesinlik: gün–saat–dakika. `DOĞRULANMADI`
- **Revizyon / vintage:** Anlık görüntülerin kendisi doğal vintage'dır; aynı sayfanın birden
  çok yakalaması yan yana konabilir. `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Düşük–orta.** Arşiv kaydı değişmez; ancak yakalanan
  kopya, sayfanın **cutoff sonrası güncellenmiş** bir sürümü olabilir → bu durumda kopya
  kullanılamaz. Ayrıca sayfa gövdesindeki tarih damgaları güvenilir değildir. `DOĞRULANMADI`
- **Erişim yöntemi ve lisans:** Kamuya açık arayüzler; toplu erişim kotaları ve kullanım
  koşulları vardır. **DOĞRULANMADI**
- **Sızıntı riski: ORTA.** *Gerekçe:* yakalama damgası güçlü bir point-in-time kanıtıdır, ancak
  kapsama boşlukları ve "güncellenmiş sürümün yakalanması" tuzağı vardır. *Önlem:* yalnızca
  `capture_time ≤ cutoff` olan kopyalar havuza girer; kopya ham olarak saklanır; sayfa içi
  tarih damgalarına `available_time` olarak güvenilmez.

### 3.8 Ansiklopedik / sürekli güncellenen kaynaklar

- **İçerik ve kapsama başlangıcı:** Topluluk tarafından düzenlenen maddeler, wiki'ler,
  "yaşayan" referans dokümanları. Kapsam geniştir; derinlik düzensizdir. `DOĞRULANMADI`
- **Zaman damgası:** Madde düzeyinde tek bir yayın anı **yoktur**. Revizyon geçmişi sunuluyorsa
  revizyon damgası vardır (gün–saat–dakika); sunulmuyorsa yalnızca "son güncelleme" görünür ve
  bu, `available_time` için yetersizdir. `DOĞRULANMADI`
- **Revizyon / vintage:** Revizyon geçmişi varsa teknik olarak vintage mümkündür; ancak içerik
  **sentezdir**, birincil kaynak değildir ve birden çok kaynağı tarihsiz biçimde birleştirir.
  `DOĞRULANMADI`
- **Geriye dönük düzenlenme riski:** **Çok yüksek.** Sürekli düzenleme, yeniden yazma, silme;
  ayrıca içerik cutoff sonrası bilgiyle geçmişe dönük olarak zenginleştirilir (bu, tam olarak
  `CONTEXT.md` §6'daki yasak örnektir) `KURAL`.
- **Erişim yöntemi ve lisans:** Çoğu açık lisanslı, atıf koşullu. **DOĞRULANMADI**
- **Sızıntı riski: YÜKSEK.** *Gerekçe:* zaman damgası madde düzeyinde belirsiz, içerik sürekli
  değişir ve geriye dönük zenginleştirme olağandır. *Önlem:* tercihen hiç kullanılmaz; zorunlu
  ise **yalnızca** `revision_time ≤ cutoff` olan, damgası kayıtlı revizyon kabul edilir; güncel
  sürüm hiçbir koşulda havuza girmez `KURAL`.

---

## 4. Kategori karşılaştırma tablosu (özet)

| # | Kategori | Zaman kesinliği | Vintage | Geriye dönük düzenlenme | Sızıntı riski |
|---|---|---|---|---|---|
| 1 | Resmî istatistik yayınları | gün (bazıları saat) | bazılarında var | yüksek (revizyon olağan) | **ORTA** (vintage: düşük / yoksa: yüksek) |
| 2 | MB kararları/açıklamalar/tutanaklar | gün–saat | birincil metinde var | düşük–orta | **DÜŞÜK** |
| 3 | Piyasa fiyat serileri | dakika–saniye | genelde yok | orta–yüksek | **ORTA–YÜKSEK** |
| 4 | Beklenti/konsensüs | gün/dönem | nadiren | yüksek | **YÜKSEK** |
| 5 | Kurumsal/düzenleyici bildirimler | gün–saat | tadil kaydı ayrı | düşük–orta | **DÜŞÜK–ORTA** |
| 6 | Haber ajansı arşivleri | dakika (koşullu) | genelde yok | yüksek | **YÜKSEK** |
| 7 | Web arşivi anlık görüntüleri | gün–saat–dakika | kopyanın kendisi | düşük–orta | **ORTA** |
| 8 | Ansiklopedik/sürekli güncellenen | madde düzeyinde belirsiz | sürüm varsa | çok yüksek | **YÜKSEK** |

Tüm hücreler `DOĞRULANMADI`.

---

## 5. (a) Sızıntı riskine göre önerilen inşa sırası

Sıralama **yalnızca** K1–K4 kriterlerine (zaman damgası doğrulanabilirliği, vintage, cutoff
anında kapsama, erişim/lisans) dayanır. **Bilgi içeriği, "önem" veya sonuçlara dair hiçbir
değerlendirme sıralamaya girmez** `KURAL`. En düşük riskli katman önce kurulur, çünkü sızıntı
testleri (kanarya dâhil) önce en temiz katmanda doğrulanabilir.

1. **Merkez bankası birincil yayınları** (DÜŞÜK) — karar anı damgalı, değişmez artefakt.
2. **Kurumsal/düzenleyici bildirimler** (DÜŞÜK–ORTA) — yayım anı damgalı, tadil ayrı kayıt.
3. **Resmî istatistik yayınları — yalnızca vintage sunan alt küme** (ORTA → vintage ile DÜŞÜK).
   Vintage sunmayan seriler bu aşamada **alınmaz** (fail-closed).
4. **Web arşivi anlık görüntüleri** (ORTA) — yakalama damgası güçlü point-in-time kanıtı.
5. **Piyasa fiyat serileri — yalnızca arşivlenmiş anlık görüntü bulunabildiği ölçüde**
   (ORTA–YÜKSEK); aksi hâlde ertelenir.
6. **Haber ajansı arşivleri** (YÜKSEK) — yalnızca ham kopya + hash + ilk görülme damgası
   disiplini kurulduktan sonra.
7. **Ansiklopedik/sürekli güncellenen kaynaklar** (YÜKSEK) — yalnızca damgalı revizyonla, tercihen
   hiç.
8. **Beklenti/konsensüs verisi** (YÜKSEK) — erişim/lisans ve zaman damgası nedeniyle büyük
   olasılıkla kapsam dışı; karar `KULLANICI KARARI`.

Not: Bu sıra bir **altyapı sırasıdır**, bir "hangi kaynak değerli" sıralaması değildir.

---

## 6. (b) Kullanıcıya açık sorular

1. **Sağlayıcı seçimi:** Somut sağlayıcı listesini kim ve hangi yazılı mekanik kurala göre
   onaylayacak? (Ajan bu seçimi yapmaz `KURAL`.)
2. **Lisans doğrulaması:** Lisans/erişim koşulları hangi kanıtla (ekran görüntüsü, kayıtlı metin,
   tarih) ve kim tarafından doğrulanacak? `verified_by` / `verified_at` alanlarını kim doldurur?
3. **Ücretli kaynaklar:** Abonelik/ücret gerektiren kaynaklar (özellikle 3.3 ve 3.4) kabul
   edilecek mi? Bütçe ve yeniden dağıtım kısıtı politikası nedir?
4. **Vintage yoksa:** Bir seri için vintage bulunamazsa tümden mi dışlanacak, yoksa
   "cutoff anında yayımlandığı kanıtlanan tek bir sürüm" yeterli mi?
5. **Ham kopya saklama:** Telifli içerikte ham kopya saklamak (kanıt için) kabul edilecek mi;
   depolama hacmi ve saklama süresi politikası ne olacak?
6. **Düzeltilmiş metinler:** Tutanak/transkript düzeltmelerinde "ilk yayın" hangi sürüm sayılır?
7. **Bar/zaman dilimi kuralı:** `available_time` = bar kapanışı kabulü onaylanıyor mu; tüm
   zamanlar UTC mi olacak (config'te UTC yazıyor, onay gerekiyor)?
8. **Cutoff anının kesinliği:** `2010-12-31` cutoff'u gün sonu (23:59:59 UTC) olarak mı
   yorumlanacak? Farklı yorum, sınır kayıtların kabul/red kararını değiştirir.
9. **Kapsam dışı kararı:** 3.4 ve 3.8 (ve gerekirse 3.6) için "kapsam dışı" kararını kim,
   hangi yazılı gerekçeyle verir?
10. **Kapsama boşlukları:** Bir dönem için hiç kaynak yoksa bu, rapora "boşluk" olarak mı
    yazılacak, yoksa o dönem için tahmin üretimi duracak mı?
11. **Yeniden kullanım:** Bu envanterin gerçek kayıtlarla (satırlarla) doldurulması için
    hangi aşamada izin veriliyor? (Şu an yalnızca şablon ve kriterler var.)

---

## 7. Bu belgenin sınırları

- Hiçbir sağlayıcı adı, URL, lisans metni, kapsama tarihi veya kesinlik iddiası **doğrulanmış
  değildir**; hepsi `DOĞRULANMADI`.
- Bu belge **veri içermez**, veri çekmez, veri çekme izni vermez.
- Bu belge hiçbir model girdisine girmez; cutoff anındaki model bunu görmez.
- Sonraki adım: kullanıcı §6'daki soruları yanıtladıktan sonra, envanter satırları K1–K4
  kriterlerine göre **kod tarafından** doldurulur; seçim ajana bırakılmaz.
