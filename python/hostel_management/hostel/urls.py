from django.urls import path
from hostel.views import (
    home, signup, login_view, dashboard, book_room, checkout,
    payment_success, roommate_finder, logout_view, payment,
    process_payment, admin_dashboard, generate_pdf_receipt,
    booking_details, add_room, edit_room, delete_room, cancel_booking,
    notifications, profile_view, edit_profile, mark_all_read,
    chatbot_test, chatbot_direct, available_rooms, about, contact, amenities,
    admin_booking_details, change_password, user_cancel_booking
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('rooms/', available_rooms, name='rooms'),
    path('available-rooms/', available_rooms, name='available_rooms'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('amenities/', amenities, name='amenities'),
    path('book/<int:room_id>/', book_room, name='book_room'),
    path('checkout/<int:booking_id>/', checkout, name='checkout'),
    
    # Payment URL patterns - choose one of these options:
    
    # Option 1: Single URL pattern that accepts both ID and PNR
    path('payment/<str:payment_ref>/', payment, name='payment'),
    
    # Option 2: Separate URL patterns for ID and PNR (uncomment to use)
    # path('payment/id/<int:payment_id>/', payment, name='payment_by_id'),
    # path('payment/pnr/<str:pnr>/', payment_by_pnr, name='payment_by_pnr'),
    
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/process/', process_payment, name='process_payment'),
    path('roommate-finder/', roommate_finder, name='roommate_finder'),
    path('manager/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('manager/room/add/', add_room, name='add_room'),
    path('manager/room/<int:room_id>/edit/', edit_room, name='edit_room'),
    path('manager/room/<int:room_id>/delete/', delete_room, name='delete_room'),
    path('manager/booking/<int:booking_id>/', admin_booking_details, name='admin_booking_details'),
    path('manager/booking/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark-all-read/', mark_all_read, name='mark_all_read'),
    path('download_receipt/<int:booking_id>/', generate_pdf_receipt, name='download_receipt'),
    path('booking/<int:booking_id>/', booking_details, name='booking_details'),
    path('booking/<int:booking_id>/cancel/', user_cancel_booking, name='user_cancel_booking'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/change-password/', change_password, name='change_password')
    
]