# data/ — veri bölgeleri

Bu dizin üç ayrı bölgeye ayrılmıştır. Bölgeler arasındaki sınır, projenin en kritik
güvenlik kuralıdır: **zamansal sızıntıyı (look-ahead bias) önlemek.**

| Bölge | İçerik | Kural |
|---|---|---|
| `raw/` | Ham, işlenmemiş kaynaklar | İndirildiği hâliyle saklanır; üzerine yazılmaz, türetilmez |
| `pit/` | Point-in-time katman | Yalnızca zaman alanları doğrulanmış ve cutoff filtresinden geçmiş kayıtlar |
| `answer_key/` | Cutoff **sonrası** gerçekleşmeler | Tahmin hattı için **erişilemez bölge**; yalnızca değerlendirmede okunur |

## Kurallar

1. Her kayıtta `event_time`, `available_time` ve `source_date` alanları bulunur.
2. Filtreleme **`available_time`** üzerinden, kod tarafından yapılır — yargıyla değil.
3. Zaman alanı eksik veya ayrıştırılamayan kayıtlar havuza alınmaz (**fail-closed**).
4. Cutoff `config.yaml` içindeki `run.cutoff_date` değerinden gelir; buraya elle tarih yazılmaz.
5. `answer_key/` altındaki hiçbir dosya tahmin aşamasında okunamaz; bu bir test
   invaryantıdır (`tests/test_temporal_leakage.py`).
6. Bu dizinler şu an **boştur**; aşama 0 kapsamında hiçbir veri indirilmemiştir.

Not: `CONTEXT.md` ve `docs/` hiçbir zaman bu veri hattına veya model girdisine dâhil edilmez.
