"""``src/temporal.py`` için otomatik testler (yalnızca standart kütüphane).

Yalnızca **yapay** kayıtlar kullanılır; gerçek tarihsel veri, gerçek olay veya
cutoff sonrası bilgi içermez. Ağ erişimi, paket kurulumu ve model yoktur.

Çalıştırma::

    python -m unittest discover -s tests -p 'test_temporal_filter.py' -v
"""

from __future__ import annotations

import inspect
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

# --- src/ yolunu ekle (paket kurulumu yok) ---------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC_DIR = _PROJECT_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from temporal import (  # noqa: E402  (sys.path ayarından sonra import edilmeli)
    REQUIRED_FIELDS,
    Reason,
    evaluate_record,
    parse_cutoff,
    partition_records,
)

UTC = timezone.utc
CUTOFF = "2010-12-31"
CUTOFF_END = datetime(2010, 12, 31, 23, 59, 59, 999999, tzinfo=UTC)
_MISSING = object()


def make_record(**overrides):
    """Yapay bir kayıt üretir; ``_MISSING`` ile alan silinebilir."""
    record = {
        "record_id": "TEST-0001",
        "event_time": "2010-12-01T10:00:00Z",
        "available_time": "2010-12-02T08:30:00Z",
        "source_date": "2010-12-02",
    }
    for key, value in overrides.items():
        if value is _MISSING:
            record.pop(key, None)
        else:
            record[key] = value
    return record


class TestAcceptance(unittest.TestCase):
    """Cutoff sınırında veya öncesinde kalan geçerli kayıtlar kabul edilir."""

    def test_published_before_cutoff_is_accepted(self):
        result = evaluate_record(make_record(), CUTOFF)
        self.assertTrue(result.accepted)
        self.assertIs(result.reason, Reason.ACCEPTED)

    def test_published_on_cutoff_day_is_accepted(self):
        record = make_record(available_time="2010-12-31T12:00:00Z")
        self.assertTrue(evaluate_record(record, CUTOFF).accepted)

    def test_cutoff_boundary_is_inclusive(self):
        # Günün son mikro saniyesi hâlâ cutoff'un kapsamındadır.
        record = make_record(available_time="2010-12-31T23:59:59.999999Z")
        result = evaluate_record(record, CUTOFF)
        self.assertTrue(result.accepted, result.message)

    def test_date_only_available_time_on_cutoff_day_is_accepted(self):
        # Yalnızca gün verilmişse en kötü durum (günün sonu) varsayılır; sınır dâhil.
        record = make_record(available_time="2010-12-31")
        self.assertTrue(evaluate_record(record, CUTOFF).accepted)

    def test_event_equal_to_available_is_accepted(self):
        stamp = "2010-12-03T09:00:00Z"
        record = make_record(event_time=stamp, available_time=stamp)
        self.assertTrue(evaluate_record(record, CUTOFF).accepted)

    def test_aware_datetime_objects_are_accepted(self):
        record = make_record(
            event_time=datetime(2010, 12, 1, 10, 0, tzinfo=UTC),
            available_time=datetime(2010, 12, 2, 8, 30, tzinfo=UTC),
            source_date=date(2010, 12, 2),
        )
        self.assertTrue(evaluate_record(record, CUTOFF).accepted)


class TestCutoffRejection(unittest.TestCase):
    """Cutoff'u aşan kayıtlar gerekçesiyle reddedilir."""

    def test_published_after_cutoff_is_rejected(self):
        record = make_record(
            event_time="2010-12-20T10:00:00Z",
            available_time="2011-01-01T00:00:00Z",
            source_date="2011-01-01",
        )
        result = evaluate_record(record, CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.AVAILABLE_AFTER_CUTOFF)
        self.assertEqual(result.field, "available_time")

    def test_old_event_published_after_cutoff_is_rejected(self):
        # Eski bir olayı anlatıyor olması kaydı geçerli yapmaz.
        record = make_record(
            event_time="2009-06-01T00:00:00Z",
            available_time="2011-02-01T00:00:00Z",
            source_date="2011-02-01",
        )
        result = evaluate_record(record, CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.AVAILABLE_AFTER_CUTOFF)

    def test_source_date_after_cutoff_is_rejected(self):
        record = make_record(
            event_time="2010-06-01T00:00:00Z",
            available_time="2010-06-02T00:00:00Z",
            source_date="2011-01-15",
        )
        result = evaluate_record(record, CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.SOURCE_DATE_AFTER_CUTOFF)
        self.assertEqual(result.field, "source_date")

    def test_event_time_after_cutoff_is_rejected(self):
        record = make_record(
            event_time="2011-03-01T00:00:00Z",
            available_time="2011-03-01T00:00:00Z",
            source_date="2011-03-01",
        )
        result = evaluate_record(record, CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIn(
            result.reason,
            {
                Reason.EVENT_TIME_AFTER_CUTOFF,
                Reason.AVAILABLE_AFTER_CUTOFF,
                Reason.EVENT_AFTER_AVAILABLE,
            },
        )

    def test_one_second_after_boundary_is_rejected(self):
        record = make_record(available_time="2011-01-01T00:00:00Z")
        result = evaluate_record(record, CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.AVAILABLE_AFTER_CUTOFF)


class TestFailClosed(unittest.TestCase):
    """Eksik, boş veya ayrıştırılamayan zaman bilgisi reddedilir."""

    def test_missing_available_time_is_rejected(self):
        result = evaluate_record(make_record(available_time=_MISSING), CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.MISSING_FIELD)
        self.assertEqual(result.field, "available_time")

    def test_missing_event_time_is_rejected(self):
        result = evaluate_record(make_record(event_time=_MISSING), CUTOFF)
        self.assertIs(result.reason, Reason.MISSING_FIELD)
        self.assertEqual(result.field, "event_time")

    def test_missing_source_date_is_rejected(self):
        result = evaluate_record(make_record(source_date=_MISSING), CUTOFF)
        self.assertIs(result.reason, Reason.MISSING_FIELD)
        self.assertEqual(result.field, "source_date")

    def test_every_required_field_is_enforced(self):
        self.assertEqual(
            REQUIRED_FIELDS, ("event_time", "available_time", "source_date")
        )
        for field in REQUIRED_FIELDS:
            with self.subTest(field=field):
                result = evaluate_record(make_record(**{field: _MISSING}), CUTOFF)
                self.assertFalse(result.accepted)
                self.assertIs(result.reason, Reason.MISSING_FIELD)
                self.assertEqual(result.field, field)

    def test_blank_string_is_rejected(self):
        result = evaluate_record(make_record(available_time="   "), CUTOFF)
        self.assertIs(result.reason, Reason.MISSING_FIELD)
        self.assertEqual(result.field, "available_time")

    def test_none_value_is_rejected(self):
        result = evaluate_record(make_record(source_date=None), CUTOFF)
        self.assertIs(result.reason, Reason.MISSING_FIELD)

    def test_malformed_date_is_rejected(self):
        result = evaluate_record(make_record(available_time="2010-13-45T00:00:00Z"), CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.INVALID_TIMESTAMP)
        self.assertEqual(result.field, "available_time")

    def test_unparsable_text_is_rejected(self):
        result = evaluate_record(make_record(event_time="dun ogleden sonra"), CUTOFF)
        self.assertIs(result.reason, Reason.INVALID_TIMESTAMP)
        self.assertEqual(result.field, "event_time")

    def test_non_string_value_is_rejected(self):
        result = evaluate_record(make_record(available_time=20101202), CUTOFF)
        self.assertIs(result.reason, Reason.INVALID_TIMESTAMP)

    def test_naive_timestamp_string_is_rejected(self):
        # Saat dilimi yoksa sessizce UTC varsayılmaz.
        result = evaluate_record(make_record(available_time="2010-12-02T08:30:00"), CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.AMBIGUOUS_TIMEZONE)
        self.assertEqual(result.field, "available_time")

    def test_naive_datetime_object_is_rejected(self):
        record = make_record(available_time=datetime(2010, 12, 2, 8, 30))
        result = evaluate_record(record, CUTOFF)
        self.assertIs(result.reason, Reason.AMBIGUOUS_TIMEZONE)

    def test_non_mapping_record_is_rejected(self):
        result = evaluate_record(["event_time", "available_time"], CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.INVALID_RECORD)

    def test_invalid_cutoff_raises_value_error(self):
        for bad_cutoff in ("2010-13-99", "2010-12-31T00:00:00", None, 5):
            with self.subTest(cutoff=bad_cutoff):
                with self.assertRaises(ValueError):
                    evaluate_record(make_record(), bad_cutoff)


class TestTimezoneNormalization(unittest.TestCase):
    """Saat dilimi içeren damgalar UTC'ye çevrilerek karşılaştırılır."""

    def test_negative_offset_crossing_boundary_is_rejected(self):
        # 2010-12-31T22:00:00-05:00 == 2011-01-01T03:00:00Z -> cutoff sonrası
        record = make_record(available_time="2010-12-31T22:00:00-05:00")
        result = evaluate_record(record, CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.AVAILABLE_AFTER_CUTOFF)

    def test_positive_offset_still_before_boundary_is_accepted(self):
        # 2011-01-01T01:30:00+02:00 == 2010-12-31T23:30:00Z -> cutoff içinde
        record = make_record(available_time="2011-01-01T01:30:00+02:00")
        self.assertTrue(evaluate_record(record, CUTOFF).accepted)

    def test_same_instant_different_notations_agree(self):
        first = evaluate_record(
            make_record(available_time="2010-12-31T22:00:00-05:00"), CUTOFF
        )
        second = evaluate_record(
            make_record(available_time="2011-01-01T03:00:00Z"), CUTOFF
        )
        self.assertEqual(first.accepted, second.accepted)
        self.assertIs(first.reason, second.reason)

    def test_normalized_values_are_reported_in_utc(self):
        record = make_record(available_time="2011-01-01T01:30:00+02:00")
        result = evaluate_record(record, CUTOFF)
        self.assertTrue(result.accepted)
        normalized = result.normalized["available_time"]
        self.assertEqual(normalized, datetime(2010, 12, 31, 23, 30, tzinfo=UTC))
        self.assertEqual(normalized.utcoffset(), timezone.utc.utcoffset(None))

    def test_lowercase_z_is_handled(self):
        record = make_record(available_time="2010-12-30t23:00:00z")
        self.assertTrue(evaluate_record(record, CUTOFF).accepted)


class TestConsistency(unittest.TestCase):
    """event_time, available_time'dan sonra olamaz."""

    def test_event_after_available_is_rejected(self):
        record = make_record(
            event_time="2010-12-05T00:00:00Z",
            available_time="2010-12-02T00:00:00Z",
            source_date="2010-12-05",
        )
        result = evaluate_record(record, CUTOFF)
        self.assertFalse(result.accepted)
        self.assertIs(result.reason, Reason.EVENT_AFTER_AVAILABLE)
        self.assertEqual(result.field, "event_time")

    def test_consistency_is_reported_before_cutoff_rule(self):
        # İki sorun da varsa tutarlılık gerekçesi döner (belgelenen sıra).
        record = make_record(
            event_time="2011-02-01T00:00:00Z",
            available_time="2011-01-15T00:00:00Z",
            source_date="2011-02-01",
        )
        result = evaluate_record(record, CUTOFF)
        self.assertIs(result.reason, Reason.EVENT_AFTER_AVAILABLE)


class TestCutoffVariants(unittest.TestCase):
    """Cutoff koda gömülü değildir; farklı değerlerle çalışır."""

    def test_later_cutoff_accepts_previously_rejected_record(self):
        record = make_record(
            event_time="2011-05-30T00:00:00Z",
            available_time="2011-06-01T00:00:00Z",
            source_date="2011-06-01",
        )
        self.assertFalse(evaluate_record(record, "2011-05-31").accepted)
        self.assertTrue(evaluate_record(record, "2011-06-01").accepted)
        self.assertTrue(evaluate_record(record, "2013-12-31").accepted)

    def test_cutoff_function_has_no_default_value(self):
        parameter = inspect.signature(evaluate_record).parameters["cutoff"]
        self.assertIs(parameter.default, inspect.Parameter.empty)

    def test_cutoff_date_object_covers_whole_day(self):
        self.assertEqual(parse_cutoff(date(2010, 12, 31)), CUTOFF_END)

    def test_cutoff_aware_datetime_is_exact_instant(self):
        cutoff = datetime(2010, 12, 31, 12, 0, tzinfo=UTC)
        before = make_record(available_time="2010-12-31T11:59:59Z")
        after = make_record(available_time="2010-12-31T12:00:01Z")
        self.assertTrue(evaluate_record(before, cutoff).accepted)
        self.assertFalse(evaluate_record(after, cutoff).accepted)

    def test_cutoff_with_offset_is_normalized(self):
        # 2011-01-01T02:00:00+03:00 == 2010-12-31T23:00:00Z
        cutoff = "2011-01-01T02:00:00+03:00"
        self.assertTrue(
            evaluate_record(make_record(available_time="2010-12-31T22:00:00Z"), cutoff).accepted
        )
        self.assertFalse(
            evaluate_record(
                make_record(
                    event_time="2010-12-31T23:00:00Z",
                    available_time="2010-12-31T23:45:00Z",
                    source_date="2010-12-31",
                ),
                cutoff,
            ).accepted
        )


class TestResultReporting(unittest.TestCase):
    """Sonuç nesnesi gerekçeyi ve normalize edilmiş değerleri taşır."""

    def test_rejected_result_has_reason_and_message(self):
        result = evaluate_record(make_record(available_time="2011-05-05T00:00:00Z"), CUTOFF)
        self.assertFalse(result.accepted)
        self.assertTrue(result.message.strip())
        self.assertIn("available_time", result.message)
        self.assertTrue(result.reason.value)

    def test_reason_is_string_enum(self):
        result = evaluate_record(make_record(), CUTOFF)
        self.assertIsInstance(result.reason, str)
        self.assertEqual(result.reason.value, "accepted")
        self.assertEqual(str(result.reason), "Reason.ACCEPTED")

    def test_record_id_is_carried_into_result(self):
        record = make_record(record_id="TEST-0042")
        self.assertEqual(evaluate_record(record, CUTOFF).record_id, "TEST-0042")

    def test_unparsable_record_result_has_no_normalized_values(self):
        result = evaluate_record(make_record(event_time="bozuk"), CUTOFF)
        self.assertEqual(dict(result.normalized), {})

    def test_partition_records_splits_accepted_and_rejected(self):
        records = [
            make_record(record_id="TEST-A"),
            make_record(
                record_id="TEST-B",
                event_time="2010-05-30T00:00:00Z",
                available_time="2010-06-01T00:00:00Z",
                source_date="2010-06-01",
            ),
            make_record(record_id="TEST-C", available_time="2011-03-01T00:00:00Z"),
        ]
        accepted, rejected = partition_records(records, CUTOFF)
        self.assertEqual([r["record_id"] for r, _ in accepted], ["TEST-A", "TEST-B"])
        self.assertEqual([r["record_id"] for r, _ in rejected], ["TEST-C"])
        self.assertIs(rejected[0][1].reason, Reason.AVAILABLE_AFTER_CUTOFF)


if __name__ == "__main__":
    unittest.main(verbosity=2)
