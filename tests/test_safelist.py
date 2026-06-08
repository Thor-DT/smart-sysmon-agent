import hashlib
import os

import safelist
import config


def test_is_safelisted_by_name():
    # Known default safe name should be True
    assert safelist.is_safelisted("explorer.exe", None) is True


def test_is_safelisted_by_hash(tmp_path, monkeypatch):
    data = b"dummy-binary-content"
    f = tmp_path / "dummy.exe"
    f.write_bytes(data)

    h = hashlib.sha256(data).hexdigest()
    monkeypatch.setattr(config, "SYSTEM_SAFELIST_HASHES", frozenset([h]))

    assert safelist.is_safelisted(None, str(f)) is True


def test_not_safelisted(tmp_path, monkeypatch):
    # Unknown name and empty hashes -> not safelisted
    monkeypatch.setattr(config, "SYSTEM_SAFELIST_HASHES", frozenset())
    assert safelist.is_safelisted("unknown_proc.exe", None) is False
