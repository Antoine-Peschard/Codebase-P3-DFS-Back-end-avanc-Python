import pytest

from equipment.models import Equipment
from equipment.services import (
    EquipmentAlreadyAvailableError,
    EquipmentNotFoundError,
    EquipmentService,
    EquipmentUnavailableError,
)


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


def test_borrow_unavailable_equipment_raises_error(service, equipment):
    """Borrowing an already borrowed equipment raises an error and keeps the borrower"""
    service.borrow_equipment(equipment.id, "Antoine", "Peschard")

    with pytest.raises(EquipmentUnavailableError):
        """Check and act: the borrowing should raise the exception"""
        service.borrow_equipment(equipment.id, "Arthur", "Mardoc")

    """Check: check if the first borrower's name has not been erased"""
    equipment.refresh_from_db()
    assert equipment.borrower_first_name == "Antoine"
    assert equipment.borrower_last_name == "Peschard"


def test_return_borrowed_equipment(service, equipment):
    """A borrowed equipment can be returned and its borrower is cleared."""
    service.borrow_equipment(equipment.id, "Antoine", "Peschard")
    equipment.refresh_from_db()
    borrowed_at = equipment.borrowed_at

    service.return_equipment(equipment.id)

    equipment.refresh_from_db()
    assert equipment.is_available is True
    assert equipment.borrower_first_name == ""
    assert equipment.borrower_last_name == ""
    assert equipment.borrowed_at == borrowed_at
    assert equipment.returned_at is not None


def test_return_already_returned_equipment(service, equipment):
    """An already returned equipment cannot be returned and it should raise and error."""
    with pytest.raises(EquipmentAlreadyAvailableError):
        service.return_equipment(equipment.id) 


@pytest.mark.django_db
def test_equipment_not_found_error(service):
    """Borrowing an unknown equipment id raises a not found error."""
    with pytest.raises(EquipmentNotFoundError):
        service.borrow_equipment(999999, "Carlos", "Spritz")


def test_new_borrowing_after_return(service, equipment):
    service.borrow_equipment(equipment.id, "Antoine", "Peschard")
    service.return_equipment(equipment.id)
    service.borrow_equipment(equipment.id, "Lukas", "Aled")
    equipment.refresh_from_db()
    assert equipment.is_available is False
    assert equipment.borrower_first_name == "Lukas"
    assert equipment.borrower_last_name == "Aled"
    assert equipment.returned_at is None