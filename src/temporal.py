"""Zamansal filtre (point-in-time) — cutoff'a göre kayıt kabul/red kararı.

Bu modül, bellek içindeki bir veri kaydını (Python sözlüğü) verilen cutoff
tarihine göre değerlendirir ve kararı **gerekçesiyle** döndürür.

Tasarım kuralları (bkz. ``CONTEXT.md`` ve ``config.yaml`` -> ``time_semantics``):

* Filtreleme **yalnızca kod** tarafından, programatik zaman alanları üzerinden
  yapılır. Doğal dil yorumu, LLM yargısı veya "muhtemelen eskidir" gerekçesi
  kullanılmaz.
* Zorunlu alanlar: ``event_time``, ``available_time``, ``source_date``.
* Cutoff, o günün **tamamını** kapsar: ``"2010-12-31"`` cutoff'u,
  ``2010-12-31T23:59:59.999999Z`` anına kadar (dâhil) erişilebilir bilgiyi kabul
  eder. Karşılaştırma ``<=`` ile yapılır.
* **FAIL-CLOSED:** alan eksik/boş, tarih ayrıştırılamıyor veya saat dilimi
  belirsizse kayıt **reddedilir**.
* Saat dilimi içeren damgalar UTC'ye **normalize edilerek** karşılaştırılır.
* Saat dilimi içermeyen (naive) damgalar sessizce UTC varsayılmaz; reddedilir.
* Kaba (yalnızca gün çözünürlüklü) damgalar en kötü durum varsayımıyla o günün
  **sonu** kabul edilir (``coarse_timestamp_policy: assume_latest_possible``).
  Bu varsayım yalnızca kabulü zorlaştırır, gevşetmez.
* Tutarlılık: ``event_time``, ``available_time``'dan sonra olamaz.

Cutoff **parametredir**, fonksiyon içine sabitlenmez; aynı fonksiyon farklı
cutoff değerleriyle çalışır. ``config.yaml`` entegrasyonu (YAML ayrıştırma) bu
modülün kapsamı **dışındadır**; cutoff çağıran tarafından verilir.

Değerlendirme sırası (gerekçe belirlenirken bu sıra izlenir):

1. kayıt tipi (``Mapping`` değilse ``INVALID_RECORD``),
2. zorunlu alanların varlığı (``MISSING_FIELD``),
3. zaman damgalarının ayrıştırılması
   (``INVALID_TIMESTAMP`` / ``AMBIGUOUS_TIMEZONE``),
4. tutarlılık: ``event_time <= available_time`` (``EVENT_AFTER_AVAILABLE``),
5. ``available_time <= cutoff`` (``AVAILABLE_AFTER_CUTOFF``),
6. ``source_date <= cutoff`` (``SOURCE_DATE_AFTER_CUTOFF``),
7. ``event_time <= cutoff`` (``EVENT_TIME_AFTER_CUTOFF``; 4 ve 5 nedeniyle
   normalde erişilemez, savunma amaçlı korunur).

Örnek::

    >>> rec = {
    ...     "record_id": "TEST-0001",
    ...     "event_time": "2010-12-01T10:00:00Z",
    ...     "available_time": "2010-12-02T08:30:00Z",
    ...     "source_date": "2010-12-02",
    ... }
    >>> sonuc = evaluate_record(rec, "2010-12-31")
    >>> sonuc.accepted, sonuc.reason.value
    (True, 'accepted')
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as _dc_field
from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Any, Iterable, List, Mapping, Optional, Tuple

__all__ = [
    "REQUIRED_FIELDS",
    "Reason",
    "FilterResult",
    "TemporalParseError",
    "UnparsableTimestampError",
    "AmbiguousTimezoneError",
    "parse_cutoff",
    "evaluate_record",
    "partition_records",
]

UTC = timezone.utc

#: Her kayıtta bulunması zorunlu zaman alanları (config.yaml -> time_semantics).
REQUIRED_FIELDS: Tuple[str, ...] = ("event_time", "available_time", "source_date")

_DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_END_OF_DAY = time(23, 59, 59, 999999)


# ---------------------------------------------------------------------------
# Hatalar
# ---------------------------------------------------------------------------
class TemporalParseError(ValueError):
    """Zaman damgası ayrıştırılamadı (fail-closed: kayıt reddedilir)."""


class UnparsableTimestampError(TemporalParseError):
    """Değer bir zaman damgası olarak ayrıştırılamıyor."""


class AmbiguousTimezoneError(TemporalParseError):
    """Saat dilimi belirtilmemiş; sessizce tahmin edilmez, kayıt reddedilir."""


# ---------------------------------------------------------------------------
# Sonuç modeli
# ---------------------------------------------------------------------------
class Reason(str, Enum):
    """Kabul/red gerekçe kodları (makine tarafından okunabilir)."""

    ACCEPTED = "accepted"
    INVALID_RECORD = "invalid_record"
    MISSING_FIELD = "missing_field"
    INVALID_TIMESTAMP = "invalid_timestamp"
    AMBIGUOUS_TIMEZONE = "ambiguous_timezone"
    EVENT_AFTER_AVAILABLE = "event_after_available"
    AVAILABLE_AFTER_CUTOFF = "available_after_cutoff"
    SOURCE_DATE_AFTER_CUTOFF = "source_date_after_cutoff"
    EVENT_TIME_AFTER_CUTOFF = "event_time_after_cutoff"


@dataclass(frozen=True)
class FilterResult:
    """Bir kaydın cutoff değerlendirmesinin sonucu.

    Attributes:
        accepted: Kayıt havuza alınabilir mi?
        reason: Gerekçe kodu (:class:`Reason`).
        message: İnsan tarafından okunabilir açıklama.
        field: Sorunun tespit edildiği alan (varsa).
        record_id: Kaydın kimliği (varsa; ``record_id`` veya ``doc_id``).
        normalized: UTC'ye normalize edilmiş zaman alanları (ayrıştırıldıysa).
    """

    accepted: bool
    reason: Reason
    message: str
    field: Optional[str] = None
    record_id: Optional[str] = None
    normalized: Mapping[str, datetime] = _dc_field(default_factory=dict)


def _iso(value: datetime) -> str:
    """UTC datetime'ı okunabilir ISO-8601 biçimine çevirir."""
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Ayrıştırma
# ---------------------------------------------------------------------------
def _to_utc_datetime(value: Any) -> datetime:
    """Bir zaman alanını UTC'ye normalize edilmiş ``datetime``'a çevirir.

    Kabul edilen girdiler:
      * saat dilimi içeren ``datetime`` veya ISO-8601 metni (``Z`` / ``+03:00``),
      * yalnızca gün içeren ``date`` veya ``"YYYY-MM-DD"`` metni
        (o günün **sonu** kabul edilir — en kötü durum varsayımı).

    Reddedilen girdiler (fail-closed):
      * saat dilimi içermeyen (naive) damgalar -> :class:`AmbiguousTimezoneError`,
      * ayrıştırılamayan veya desteklenmeyen değerler ->
        :class:`UnparsableTimestampError`.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise AmbiguousTimezoneError(
                "saat dilimi belirtilmemiş (naive datetime); sessizce UTC varsayılmaz"
            )
        return value.astimezone(UTC)

    if isinstance(value, date):  # datetime yukarıda ele alındı
        return datetime.combine(value, _END_OF_DAY, tzinfo=UTC)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise UnparsableTimestampError("boş metin")
        if _DATE_ONLY_RE.match(text):
            try:
                day = date.fromisoformat(text)
            except ValueError as exc:
                raise UnparsableTimestampError(f"geçersiz gün: {text!r}") from exc
            return datetime.combine(day, _END_OF_DAY, tzinfo=UTC)

        iso_text = text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text
        try:
            parsed = datetime.fromisoformat(iso_text)
        except ValueError as exc:
            raise UnparsableTimestampError(
                f"ISO-8601 zaman damgası olarak ayrıştırılamadı: {text!r}"
            ) from exc
        if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
            raise AmbiguousTimezoneError(
                f"saat dilimi belirtilmemiş: {text!r}; sessizce UTC varsayılmaz"
            )
        return parsed.astimezone(UTC)

    raise UnparsableTimestampError(
        f"desteklenmeyen değer tipi: {type(value).__name__}"
    )


def parse_cutoff(cutoff: Any) -> datetime:
    """Cutoff değerini UTC'de bir ana çevirir.

    * ``"2010-12-31"`` veya ``date(2010, 12, 31)`` -> o günün sonu
      (``2010-12-31T23:59:59.999999Z``): cutoff günün tamamını kapsar.
    * Saat dilimi içeren damga/``datetime`` -> tam o an (UTC'ye çevrilir).

    Geçersiz ya da saat dilimi belirsiz bir cutoff, programcı hatası sayılarak
    :class:`ValueError` yükseltir (kayıt hatası değildir).
    """
    try:
        return _to_utc_datetime(cutoff)
    except TemporalParseError as exc:
        raise ValueError(f"geçersiz cutoff değeri {cutoff!r}: {exc}") from exc


def _record_id(record: Mapping[str, Any]) -> Optional[str]:
    for key in ("record_id", "doc_id", "id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


# ---------------------------------------------------------------------------
# Ana filtre
# ---------------------------------------------------------------------------
def evaluate_record(record: Mapping[str, Any], cutoff: Any) -> FilterResult:
    """Bir kaydı cutoff'a göre değerlendirir.

    Args:
        record: Zaman alanlarını içeren sözlük (``event_time``,
            ``available_time``, ``source_date``).
        cutoff: ``"YYYY-MM-DD"`` metni, ``date`` veya saat dilimi içeren
            ``datetime``/ISO-8601 metni. Fonksiyon içine sabitlenmez.

    Returns:
        :class:`FilterResult` — kabul/red kararı, gerekçe kodu, açıklama ve
        (varsa) UTC'ye normalize edilmiş zaman alanları.

    Raises:
        ValueError: ``cutoff`` ayrıştırılamıyorsa veya saat dilimi belirsizse.
    """
    cutoff_utc = parse_cutoff(cutoff)

    if not isinstance(record, Mapping):
        return FilterResult(
            accepted=False,
            reason=Reason.INVALID_RECORD,
            message=(
                "kayıt bir sözlük (Mapping) olmalı; "
                f"alınan tip: {type(record).__name__}"
            ),
        )

    record_id = _record_id(record)

    # (2) Zorunlu alanlar
    for name in REQUIRED_FIELDS:
        if name not in record:
            return FilterResult(
                accepted=False,
                reason=Reason.MISSING_FIELD,
                message=f"zorunlu alan yok: {name}",
                field=name,
                record_id=record_id,
            )
        value = record[name]
        if value is None or (isinstance(value, str) and not value.strip()):
            return FilterResult(
                accepted=False,
                reason=Reason.MISSING_FIELD,
                message=f"zorunlu alan boş: {name}",
                field=name,
                record_id=record_id,
            )

    # (3) Ayrıştırma + UTC normalizasyonu
    normalized: dict[str, datetime] = {}
    for name in REQUIRED_FIELDS:
        try:
            normalized[name] = _to_utc_datetime(record[name])
        except AmbiguousTimezoneError as exc:
            return FilterResult(
                accepted=False,
                reason=Reason.AMBIGUOUS_TIMEZONE,
                message=f"{name}: {exc}",
                field=name,
                record_id=record_id,
            )
        except TemporalParseError as exc:
            return FilterResult(
                accepted=False,
                reason=Reason.INVALID_TIMESTAMP,
                message=f"{name}: {exc}",
                field=name,
                record_id=record_id,
            )

    event_time = normalized["event_time"]
    available_time = normalized["available_time"]
    source_date = normalized["source_date"]

    # (4) Tutarlılık: olay, kamuya açılma anından sonra olamaz
    if event_time > available_time:
        return FilterResult(
            accepted=False,
            reason=Reason.EVENT_AFTER_AVAILABLE,
            message=(
                "kayıt tutarsız: event_time "
                f"({_iso(event_time)}) available_time'dan ({_iso(available_time)}) sonra"
            ),
            field="event_time",
            record_id=record_id,
            normalized=normalized,
        )

    # (5) Asıl filtre: available_time cutoff'tan sonra olamaz
    if available_time > cutoff_utc:
        return FilterResult(
            accepted=False,
            reason=Reason.AVAILABLE_AFTER_CUTOFF,
            message=(
                f"available_time ({_iso(available_time)}) cutoff "
                f"({_iso(cutoff_utc)}) anından sonra"
            ),
            field="available_time",
            record_id=record_id,
            normalized=normalized,
        )

    # (6) İkincil alan: source_date cutoff'u aşamaz
    if source_date > cutoff_utc:
        return FilterResult(
            accepted=False,
            reason=Reason.SOURCE_DATE_AFTER_CUTOFF,
            message=(
                f"source_date ({_iso(source_date)}) cutoff "
                f"({_iso(cutoff_utc)}) anından sonra"
            ),
            field="source_date",
            record_id=record_id,
            normalized=normalized,
        )

    # (7) İkincil alan: event_time cutoff'u aşamaz (savunma amaçlı)
    if event_time > cutoff_utc:
        return FilterResult(
            accepted=False,
            reason=Reason.EVENT_TIME_AFTER_CUTOFF,
            message=(
                f"event_time ({_iso(event_time)}) cutoff "
                f"({_iso(cutoff_utc)}) anından sonra"
            ),
            field="event_time",
            record_id=record_id,
            normalized=normalized,
        )

    return FilterResult(
        accepted=True,
        reason=Reason.ACCEPTED,
        message=(
            f"kabul: tüm zaman alanları cutoff ({_iso(cutoff_utc)}) sınırında veya öncesinde"
        ),
        record_id=record_id,
        normalized=normalized,
    )


def partition_records(
    records: Iterable[Mapping[str, Any]], cutoff: Any
) -> Tuple[List[Tuple[Mapping[str, Any], FilterResult]], List[Tuple[Mapping[str, Any], FilterResult]]]:
    """Kayıtları toplu değerlendirir.

    Returns:
        ``(kabul_edilenler, reddedilenler)`` — her öğe ``(kayit, sonuc)`` çifti.
        Reddedilen kayıtlar gerekçeleriyle birlikte döner (denetim için).
    """
    accepted: List[Tuple[Mapping[str, Any], FilterResult]] = []
    rejected: List[Tuple[Mapping[str, Any], FilterResult]] = []
    for record in records:
        result = evaluate_record(record, cutoff)
        (accepted if result.accepted else rejected).append((record, result))
    return accepted, rejected
