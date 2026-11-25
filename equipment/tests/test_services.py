import pytest

from equipment.models import Equipment
from equipment.services import *

@pytest.fixture
def service():
    """Prepare an instance of EquipmentService"""
    return EquipmentService()


@pytest.fixture
def equipment(db):
    """Creates an available Equipment"""
    return Equipment.objects.create(name="Ecran 27", category="Ecran")


def test_borrow_available_equipment(service, equipment):
    """borrow_equipment function test"""
    service.borrow_equipment(equipment.id, "Antoine", "Peschard")

    equipment.refresh_from_db()
    assert equipment.is_available is False
    assert equipment.borrower_first_name == "Antoine"
    assert equipment.borrower_last_name == "Peschard"
    assert equipment.borrowed_at is not None
    assert equipment.returned_at is None
