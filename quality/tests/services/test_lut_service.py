from backend.app.services.lut_service import LUTService


def test_list_luts():
    svc = LUTService()
    luts = svc.list_luts()
    assert isinstance(luts, list) and len(luts) > 0
