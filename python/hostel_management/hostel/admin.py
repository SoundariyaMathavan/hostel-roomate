from django.contrib import admin
from .models import Room, Booking, Payment, RoommatePreference, Notification
from django.utils import timezone

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'capacity', 'price', 'is_available', 'current_occupants', 'floor', 'last_maintenance')
    list_filter = ('room_type', 'capacity', 'is_available', 'floor')
    search_fields = ('room_number', 'description')
    list_editable = ('price', 'is_available')
    actions = ['mark_as_available', 'mark_as_unavailable', 'schedule_maintenance']
    
    def current_occupants(self, obj):
        bookings = obj.booking_set.filter(status='confirmed').count()
        return f"{bookings}/{obj.capacity}"
    
    current_occupants.short_description = 'Occupancy'

    def mark_as_available(self, request, queryset):
        queryset.update(is_available=True)
    mark_as_available.short_description = "Mark selected rooms as available"
    
    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = "Mark selected rooms as unavailable"
    
    def schedule_maintenance(self, request, queryset):
        queryset.update(last_maintenance=timezone.now().date(), is_available=False)
    schedule_maintenance.short_description = "Schedule maintenance for selected rooms"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in_date', 'check_out_date', 'status', 'booking_date', 'total_amount')
    list_filter = ('status', 'check_in_date', 'check_out_date')
    search_fields = ('user__username', 'room__room_number', 'guest_name', 'pnr')
    date_hierarchy = 'booking_date'
    actions = ['mark_as_confirmed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Mark selected bookings as confirmed"
    
    def mark_as_cancelled(self, request, queryset):
        # First, get all the booking objects before updating them
        bookings_to_cancel = list(queryset)
        
        # Update the status
        queryset.update(status='cancelled')
        
        # Create notification for each cancelled booking
        for booking in bookings_to_cancel:
            # Refresh the booking from the database to get the updated status
            booking.refresh_from_db()
            
            # Create the notification
            Notification.objects.create(
                user=booking.user,
                message=f"Your booking #{booking.id} for {booking.room.room_number} has been cancelled by the administrator.",
                booking=booking
            )
            
            # Log the notification creation for debugging
            print(f"Notification created for user {booking.user.username} about booking {booking.id}")
    
    mark_as_cancelled.short_description = "Mark selected bookings as cancelled"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'amount', 'status', 'payment_method', 'timestamp')
    list_filter = ('status', 'payment_method', 'timestamp')
    search_fields = ('user__username', 'booking__room__room_number')
    date_hierarchy = 'timestamp'
    actions = ['mark_as_completed', 'mark_as_refunded']

    def mark_as_completed(self, request, queryset):
        queryset.update(status='Completed')
        for payment in queryset:
            if payment.booking:
                payment.booking.is_paid = True
                payment.booking.save()
    mark_as_completed.short_description = "Mark payments as completed"

    def mark_as_refunded(self, request, queryset):
        queryset.update(status='Refunded')
    mark_as_refunded.short_description = "Mark payments as refunded"

@admin.register(RoommatePreference)
class RoommatePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'study_habits', 'cleanliness', 'created_at', 'updated_at')
    list_filter = ('study_habits', 'cleanliness')
    search_fields = ('user__username', 'interests', 'additional_preferences')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'booking', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected notifications as unread"
