from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def get_default_checkout_date():
    return timezone.now() + timezone.timedelta(days=30)

# Constants for cleanliness levels
CLEANLINESS_LEVELS = {
    'very_neat': 3,
    'moderately_neat': 2,
    'relaxed': 1
}

class Room(models.Model):
    ROOM_TYPES = [
        ('standard', 'Standard Room'),
        ('deluxe', 'Deluxe Room'),
        ('luxury', 'Luxury Suite'),
        ('premium', 'Premium Suite'),
    ]
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='standard')
    capacity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    floor = models.IntegerField(default=1)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    has_ac = models.BooleanField(default=False)
    has_attached_bathroom = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=False)
    has_fridge = models.BooleanField(default=False)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of additional amenities")
    last_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_room_type_display()} - {self.room_number}"

    def get_amenities_list(self):
        return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]

    def is_fully_occupied(self):
        active_bookings = self.booking_set.filter(status='confirmed').count()
        return active_bookings >= self.capacity

    def current_occupants_count(self):
        return self.booking_set.filter(status='confirmed').count()

    def save(self, *args, **kwargs):
        if not self.price:
            if self.room_type == 'standard':
                self.price = 50.00
            elif self.room_type == 'deluxe':
                self.price = 80.00
            elif self.room_type == 'luxury':
                self.price = 120.00
            elif self.room_type == 'premium':
                self.price = 150.00
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['room_number']

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    guest_name = models.CharField(max_length=100, default='')
    pnr = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, default='')
    email = models.EmailField(default='')
    address = models.TextField(default='')
    id_proof = models.CharField(max_length=50, default='')
    id_number = models.CharField(max_length=50, default='')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.guest_name} - Booking #{self.id}"

    def calculate_total_days(self):
        return (self.check_out_date - self.check_in_date).days

    def calculate_total_price(self):
        days = self.calculate_total_days()
        return days * self.room.price

    class Meta:
        ordering = ['-booking_date']

class RoommatePreference(models.Model):
    STUDY_HABITS_CHOICES = [
        ('early_bird', 'Early Bird'),
        ('night_owl', 'Night Owl'),
        ('flexible', 'Flexible'),
    ]
    
    CLEANLINESS_CHOICES = [
        ('very_neat', 'Very Neat'),
        ('moderately_neat', 'Moderately Neat'),
        ('relaxed', 'Relaxed'),
    ]
    
    ROOM_PREFERENCE_CHOICES = [
        ('quiet', 'Quiet Room'),
        ('social', 'Social Room'),
        ('balanced', 'Balanced'),
    ]
    
    SHARING_PREFERENCE_CHOICES = [
        ('social', 'Very Social'),
        ('moderate', 'Moderately Social'),
        ('private', 'Private Person'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    study_habits = models.CharField(max_length=20, choices=STUDY_HABITS_CHOICES, default='flexible')
    cleanliness = models.CharField(max_length=20, choices=CLEANLINESS_CHOICES, default='moderately_neat')
    room_preference = models.CharField(max_length=20, choices=ROOM_PREFERENCE_CHOICES, default='balanced')
    sharing_preference = models.CharField(max_length=20, choices=SHARING_PREFERENCE_CHOICES, default='moderate')
    interests = models.TextField(default='')
    additional_preferences = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Roommate Preferences"

    class Meta:
        ordering = ['-updated_at']

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('QR', 'QR Code'),
        ('Manual', 'Manual Payment'),
    ]
    
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='Manual')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of ${self.amount} by {self.user.username}"

    class Meta:
        ordering = ['-timestamp']

class BookingPreference(models.Model):
    DURATION_TYPES = [
        ('days', 'Days'),
        ('months', 'Months'),
        ('year', 'Year'),
    ]
    
    FOOD_PREFERENCES = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('both', 'Both'),
        ('none', 'No Food Service Required'),
    ]

    MEAL_PLANS = [
        ('breakfast', 'Breakfast Only'),
        ('breakfast_dinner', 'Breakfast and Dinner'),
        ('all_meals', 'All Meals'),
        ('none', 'No Meals'),
    ]
    
    PARKING_TYPES = [
        ('none', 'No Parking Required'),
        ('two_wheeler', 'Two-Wheeler Parking'),
        ('car', 'Car Parking'),
        ('both', 'Both Car and Two-Wheeler'),
    ]
    
    AC_PREFERENCES = [
        ('required', 'AC Required'),
        ('preferred', 'AC Preferred but not mandatory'),
        ('not_required', 'AC Not Required'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    duration_type = models.CharField(max_length=10, choices=DURATION_TYPES, default='months')
    duration_value = models.IntegerField(default=1)
    food_preference = models.CharField(max_length=10, choices=FOOD_PREFERENCES, default='none')
    meal_plan = models.CharField(max_length=20, choices=MEAL_PLANS, default='none')
    parking_type = models.CharField(max_length=15, choices=PARKING_TYPES, default='none')
    ac_preference = models.CharField(max_length=15, choices=AC_PREFERENCES, default='preferred')
    needs_laundry = models.BooleanField(default=False)
    needs_cleaning = models.BooleanField(default=False)
    special_dietary_requirements = models.TextField(blank=True)
    additional_requests = models.TextField(blank=True)
    preferred_roommate = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='roommate_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking Preferences for {self.booking.user.username}"

    def calculate_total_days(self):
        if self.duration_type == 'days':
            return self.duration_value
        elif self.duration_type == 'months':
            return self.duration_value * 30
        else:  # year
            return self.duration_value * 365

    def calculate_additional_charges(self):
        base_charge = 0
        # Parking charges
        if self.parking_type == 'two_wheeler':
            base_charge += 30  # Monthly two-wheeler parking charge
        elif self.parking_type == 'car':
            base_charge += 60  # Monthly car parking charge
        elif self.parking_type == 'both':
            base_charge += 80  # Monthly both vehicles parking charge
            
        # AC preference charges
        if self.ac_preference == 'required':
            base_charge += 50  # Monthly AC charge
            
        # Other services
        if self.needs_laundry:
            base_charge += 30  # Monthly laundry charge
        if self.needs_cleaning:
            base_charge += 40  # Monthly cleaning charge
            
        # Meal plan charges
        if self.meal_plan == 'breakfast':
            base_charge += 100
        elif self.meal_plan == 'breakfast_dinner':
            base_charge += 200
        elif self.meal_plan == 'all_meals':
            base_charge += 300
            
        return base_charge

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:50]}"

    class Meta:
        ordering = ['-created_at']

