from django.core.management.base import BaseCommand
from hostel.models import Room

class Command(BaseCommand):
    help = 'Creates initial rooms in the database'

    def handle(self, *args, **kwargs):
        # Create rooms with different capacities
        rooms_data = [
            {'room_number': '101', 'capacity': 2},
            {'room_number': '102', 'capacity': 2},
            {'room_number': '201', 'capacity': 1},
            {'room_number': '202', 'capacity': 1},
        ]

        for room_data in rooms_data:
            Room.objects.get_or_create(
                room_number=room_data['room_number'],
                defaults={'capacity': room_data['capacity']}
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created room {room_data["room_number"]}')
            ) 