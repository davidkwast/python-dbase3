from pathlib import Path
SAMPLES_DIR = Path('tests/dbf_files')
SAMPLE_FILE = SAMPLES_DIR / 'dbase_03.dbf'

from datetime import date
import pytest

import dbase3

def test_open():
    dbase = dbase3.DBase(SAMPLE_FILE)

    with pytest.raises(FileNotFoundError):
        dbase3.DBase('null')


def test_basic():
    db = dbase3.DBase(SAMPLE_FILE)

    assert db.count() == 14

    assert db[13]._pk == 13

    with pytest.raises(dbase3.CorruptStatusFlag):
        db[14]
    
    record = db[0]

    assert record.gps_date == date(2005, 7, 12)
    