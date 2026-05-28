"""
Baseline (P2P) tests for forgeserde. These exercise the public contract and
must pass on both the vulnerable source tree and the gold-patched one.
"""

import pytest

from forgeserde.core import Fory
from forgeserde.class_resolver import ClassResolver, ResolutionError
from forgeserde.policy import DeserializationPolicy
from forgeserde.metrics import EncodeMetrics
from forgeserde.type_registry import TypeRegistry
from forgeserde.schemas import (
    EncodedRecord,
    FrameHeader,
    TypeDescriptor,
    describe,
    make_type_descriptor,
)
from forgeserde.buffer import BufferError, ReadBuffer, WriteBuffer
from forgeserde.service import SerializationService


def test_dynamic_roundtrip_state_restoration():
    f = Fory()
    payload = {"kind": "dynamic", "class": "forgeserde.policy.PolicyError", "state": None}
    out = f.deserialize(payload)
    assert out.__class__.__name__ == "PolicyError"


def test_class_resolver_imports_known_class():
    r = ClassResolver()
    cls = r.lookup("forgeserde.policy.DeserializationPolicy")
    assert cls is DeserializationPolicy


def test_class_resolver_rejects_malformed():
    r = ClassResolver()
    with pytest.raises(ResolutionError):
        r.lookup("noModulePath")


def test_fory_serializes_primitive_via_dynamic():
    f = Fory()
    out = f.serialize("hello")
    assert b"hello" in out


def test_metrics_record_and_count():
    m = EncodeMetrics()
    m.record_encode("dict", 32)
    m.record_encode("dict", 64)
    m.record_encode("list", 16)
    assert m.count_for("dict") == 2
    assert m.count_for("list") == 1
    assert m.total_bytes_for("dict") == 96


def test_metrics_summary_sorted():
    m = EncodeMetrics()
    m.record_encode("bb", 1)
    m.record_encode("aa", 2)
    summary = m.summary()
    keys = [row[0] for row in summary]
    assert keys == sorted(keys)


def test_metrics_reset_clears_state():
    m = EncodeMetrics()
    m.record_encode("dict", 32)
    m.reset()
    assert m.count_for("dict") == 0
    assert m.summary() == []


def test_schemas_make_type_descriptor():
    d = make_type_descriptor(42, "pkg.Cls")
    assert d.type_id == 42
    assert d.qualified_name == "pkg.Cls"
    assert d.is_reducible is True


def test_schemas_encoded_record_describe():
    rec = EncodedRecord(type_id=7, payload=b"\x00\x01\x02")
    s = describe(rec)
    assert "type_id=7" in s
    assert "bytes=3" in s


def test_schemas_frame_header_defaults():
    h = FrameHeader(protocol_version=1, payload_length=128)
    assert h.flags == 0
    assert h.schema_id is None


def test_type_registry_register_and_lookup():
    r = TypeRegistry()
    d = TypeDescriptor(type_id=10, qualified_name="pkg.A", is_reducible=True)
    r.register(d)
    assert r.get_by_id(10) is d
    assert r.get_by_name("pkg.A") is d
    assert r.count() == 1


def test_type_registry_auto_register_assigns_id():
    r = TypeRegistry()
    a = r.auto_register("pkg.A")
    b = r.auto_register("pkg.B")
    assert a.type_id != b.type_id
    assert r.get_by_name("pkg.A") is a


def test_type_registry_rejects_duplicate_id():
    r = TypeRegistry()
    r.register(TypeDescriptor(type_id=5, qualified_name="pkg.A", is_reducible=True))
    with pytest.raises(ValueError):
        r.register(TypeDescriptor(type_id=5, qualified_name="pkg.B", is_reducible=True))


def test_type_registry_clear():
    r = TypeRegistry()
    r.auto_register("pkg.A")
    r.auto_register("pkg.B")
    r.clear()
    assert r.count() == 0


def test_buffer_round_trip_bytes():
    w = WriteBuffer()
    w.write_bytes(b"hello")
    w.write_bytes(b" world")
    out = w.to_bytes()
    assert out == b"hello world"
    assert w.length() == 11


def test_buffer_uint32_round_trip():
    w = WriteBuffer()
    w.write_uint32(0xDEADBEEF)
    r = ReadBuffer(w.to_bytes())
    assert r.read_uint32() == 0xDEADBEEF
    assert r.at_end() is True


def test_buffer_underflow_raises():
    r = ReadBuffer(b"\x00\x01")
    with pytest.raises(BufferError):
        r.read_bytes(10)


def test_buffer_uint32_out_of_range():
    w = WriteBuffer()
    with pytest.raises(BufferError):
        w.write_uint32(-1)


def test_service_encode_increments_metrics():
    svc = SerializationService()
    svc.encode("hello")
    snap = svc.metrics_snapshot()
    assert snap["registered_types"] == 0
    summary = dict((row[0], row) for row in snap["by_type"])
    assert "str" in summary


def test_service_decode_round_trip():
    svc = SerializationService()
    payload = {"kind": "dynamic", "class": "forgeserde.policy.PolicyError", "state": None}
    out = svc.decode(payload)
    assert out.__class__.__name__ == "PolicyError"
