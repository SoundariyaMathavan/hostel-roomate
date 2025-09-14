from .models import Room, Booking

def create_booking(request, room_id, check_in_date, check_out_date, number_of_days):
    """
    Create a new booking for a room
    """
    try:
        room = Room.objects.get(id=room_id)
        total_price = room.price * number_of_days
        booking = Booking.objects.create(
            user=request.user,
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_amount=total_price
        )
        return booking
    except Exception as e:
        print(f"Error creating booking: {str(e)}")
        return None