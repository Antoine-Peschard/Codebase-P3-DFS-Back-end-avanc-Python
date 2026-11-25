from django.db import transaction
from django.utils import timezone

from .models import Equipment


class EquipmentNotFoundError(Exception):
    pass


class EquipmentUnavailableError(Exception):
    pass


class EquipmentAlreadyAvailableError(Exception):
    pass


class EquipmentService:
    def find_equipment(self, equipment_id: int) -> Equipment:
        try:
            return Equipment.objects.get(pk=equipment_id)
        except Equipment.DoesNotExist as exc:
            raise EquipmentNotFoundError from exc

    @transaction.atomic
    def borrow_equipment(self, equipment_id: int, first_name: str, last_name: str) -> Equipment:
        equipment = self.find_equipment(equipment_id)

        """Raise Unavailability error if no equipment is available"""
        if not equipment.is_available:
            raise EquipmentUnavailableError
        
        """Updates the equipment's parameters when borrowed"""
        equipment.is_available = False
        equipment.borrower_first_name = first_name
        equipment.borrower_last_name = last_name
        equipment.returned_at = None
        equipment.borrowed_at = timezone.now()
        equipment.save()
        return equipment

    @transaction.atomic
    def return_equipment(self, equipment_id: int) -> Equipment:
        equipment = self.find_equipment(equipment_id)

        """Raise stock error if the equipment trying to be returned is already available"""
        if equipment.is_available:
            raise EquipmentAlreadyAvailableError

        """Updates the equipment's parameters when returned"""
        equipment.is_available = True
        equipment.borrower_first_name = ""
        equipment.borrower_last_name = ""
        equipment.returned_at = timezone.now()
        equipment.save()
        return equipment
