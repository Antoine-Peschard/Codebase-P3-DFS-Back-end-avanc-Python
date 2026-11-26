from django.db import transaction
from django.utils import timezone

from .models import Equipment


class EquipmentNotFoundError(Exception):
    """Raised when trying to borrow an equipment that does not exist."""


class EquipmentUnavailableError(Exception):
    """Raised when trying to borrow an equipment that is already borrowed."""


class EquipmentAlreadyAvailableError(Exception):
    """Raised when trying to return an equipment that is already returned."""


class EquipmentService:
    def find_equipment(self, equipment_id: int) -> Equipment:
        try:
            return Equipment.objects.get(pk=equipment_id)
        except Equipment.DoesNotExist as exc:
            raise EquipmentNotFoundError from exc

    @transaction.atomic
    def borrow_equipment(self, equipment_id: int, first_name: str, last_name: str) -> Equipment:
        """Borrow an available equipment for the given person.
        
        Stores the borrower's name and the borrowing date, and resets the return date."""

        equipment = self.find_equipment(equipment_id)

        # An already borrowed equipment cannot be borrowed again
        if not equipment.is_available:
            raise EquipmentUnavailableError
        
        equipment.is_available = False
        equipment.borrower_first_name = first_name
        equipment.borrower_last_name = last_name
        equipment.returned_at = None
        equipment.borrowed_at = timezone.now()
        equipment.save()
        return equipment

    @transaction.atomic
    def return_equipment(self, equipment_id: int) -> Equipment:
        """Return an unavailable equipment.
        
        Erases the borrower's name, keeps the borrowing date and saves the returning date."""

        equipment = self.find_equipment(equipment_id)

        # An already returned equipment raises an error.
        if equipment.is_available:
            raise EquipmentAlreadyAvailableError

        equipment.is_available = True
        equipment.borrower_first_name = ""
        equipment.borrower_last_name = ""
        equipment.returned_at = timezone.now()
        equipment.save()
        return equipment
