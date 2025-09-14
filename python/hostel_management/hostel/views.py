from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Room, Booking, Payment, RoommatePreference, BookingPreference, Notification
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone, date
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.template.loader import get_template
# from xhtml2pdf import pisa  # Temporarily commented out due to dependency issues
from io import BytesIO
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import EditProfileForm, CustomPasswordChangeForm
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

@csrf_exempt
def chatbot_direct(request):
    """API endpoint for chatbot interactions"""
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        # Get URLs for links
        booking_url = request.build_absolute_uri(reverse('available_rooms'))
        dashboard_url = request.build_absolute_uri(reverse('dashboard'))
        contact_url = request.build_absolute_uri(reverse('contact'))
        
        # Define chatbot responses with HTML links
        responses = {
            'hello': 'Hi there! How can I help you with your hostel booking?',
            'booking': f'To make a booking, please <a href="{booking_url}">click here</a> to view our available rooms.',
            'check in': 'Check-in time is 2:00 PM. Please bring your ID and booking confirmation.',
            'check out': 'Check-out time is 11:00 AM. Please return your key to the reception.',
            'wifi': 'Yes, we provide free WiFi in all our rooms and common areas.',
            'breakfast': 'Breakfast is served from 7:00 AM to 10:00 AM in the dining area.',
            'parking': 'Yes, we have parking available for guests at an additional charge.',
            'rooms': f'We offer various room types including single, double, and shared rooms. <a href="{booking_url}">View available rooms</a>.',
            'payment': 'We accept credit cards, debit cards, and bank transfers.',
            'cancel': f'To cancel a booking, please go to your <a href="{dashboard_url}">dashboard</a> and select the booking you wish to cancel.',
            'contact': f'Need more help? <a href="{contact_url}">Contact our support team</a>.',
            'help': f'I can help you with booking rooms, checking availability, and general inquiries. For specific assistance, please <a href="{contact_url}">contact our support team</a>.'
        }
        
        # Check message for keywords and get response
        response = f"I'm not sure how to help with that. Please <a href='{contact_url}'>contact our reception</a> for assistance."
        for keyword, resp in responses.items():
            if keyword.lower() in message.lower():
                response = resp
                break
                
        return JsonResponse({
            'response': response,
            'hasLinks': '<a' in response  # Flag to indicate if response contains links
        })
    
    return JsonResponse({'error': 'Only POST requests are supported'}, status=400)



def home(request):
    context = {}
    if request.user.is_authenticated:
        context['welcome_message'] = f"Welcome, {request.user.first_name}!"
    return render(request, "home.html", context)


def about(request):
    """View to display the about page"""
    return render(request, "about.html")     

def contact(request):
    """View to display the contact page"""
    return render(request, "contact.html")

def amenities(request):
    """View to display the amenities page with hostel features"""
    return render(request, "amenities.html")


@login_required
def available_rooms(request):
    """View to display all available rooms for booking"""
    rooms = Room.objects.filter(is_available=True)
    return render(request, "available_rooms.html", {"rooms": rooms})




stripe.api_key = settings.STRIPE_SECRET_KEY

# SIGNUP
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return render(request, "signup.html")

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name
            )
            messages.success(request, "Account created successfully! Please login.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, "signup.html")

    return render(request, "signup.html")

# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect("home")  # Already redirects to home
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

# DASHBOARD
@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    # Count bookings by status
    confirmed_count = bookings.filter(is_paid=True).count()
    pending_count = bookings.filter(is_paid=False).count()
    
    # Ensure each booking has a payment record
    for booking in bookings:
        if not booking.is_paid and not booking.payment_set.exists():
            # Create a payment record if one doesn't exist
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                amount=booking.total_amount,
                status='Pending',
                payment_method='Manual'
            )
    
    # Get the next upcoming booking
    next_booking = bookings.filter(
        check_in_date__gte=timezone.now().date(),
        is_paid=True
    ).order_by('check_in_date').first()
    
    context = {
        'bookings': bookings,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'next_booking': next_booking,
    }
    
    return render(request, "dashboard.html", context)

# ROOM BOOKING
@login_required(login_url='login')
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Get potential roommates (users with roommate preferences)
    potential_roommates = User.objects.filter(
        roommatepreference__isnull=False
    ).exclude(id=request.user.id)
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to book a room.')
            return redirect('login')
            
        try:
            # Get form data
            guest_name = request.POST.get('guest_name')
            pnr = request.POST.get('pnr')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            address = request.POST.get('address')
            id_proof = request.POST.get('id_proof')
            id_number = request.POST.get('id_number')
            check_in_date = request.POST.get('check_in_date')
            check_out_date = request.POST.get('check_out_date')
            duration_type = request.POST.get('duration_type')
            duration_value = int(request.POST.get('duration_value'))
            
            # Get additional preferences
            food_preference = request.POST.get('food_preference', 'none')
            meal_plan = request.POST.get('meal_plan', 'none')
            parking_type = request.POST.get('parking_type', 'none')
            ac_preference = request.POST.get('ac_preference', 'preferred')
            needs_laundry = request.POST.get('needs_laundry') == 'on'
            needs_cleaning = request.POST.get('needs_cleaning') == 'on'
            special_dietary_requirements = request.POST.get('special_dietary_requirements', '')
            additional_requests = request.POST.get('additional_requests', '')
            
            # Get preferred roommate if selected
            preferred_roommate_id = request.POST.get('preferred_roommate')
            preferred_roommate = None
            if preferred_roommate_id and preferred_roommate_id != 'none':
                preferred_roommate = User.objects.get(id=preferred_roommate_id)
            
            # Validate dates
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
            
            if check_in < date.today():
                messages.error(request, 'Check-in date cannot be in the past.')
                return redirect('book_room', room_id=room_id)
                
            if check_out <= check_in:
                messages.error(request, 'Check-out date must be after check-in date.')
                return redirect('book_room', room_id=room_id)
            
            # Calculate total amount
            nights = (check_out - check_in).days
            total_amount = room.price * nights
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                room=room,
                guest_name=guest_name,
                pnr=pnr,
                phone_number=phone_number,
                email=email,
                address=address,
                id_proof=id_proof,
                id_number=id_number,
                check_in_date=check_in,
                check_out_date=check_out,
                total_amount=total_amount,
                status='pending'
            )
            
            # Create booking preference with all the new options
            booking_pref = BookingPreference.objects.create(
                booking=booking,
                duration_type=duration_type,
                duration_value=duration_value,
                food_preference=food_preference,
                meal_plan=meal_plan,
                parking_type=parking_type,
                ac_preference=ac_preference,
                needs_laundry=needs_laundry,
                needs_cleaning=needs_cleaning,
                special_dietary_requirements=special_dietary_requirements,
                additional_requests=additional_requests,
                preferred_roommate=preferred_roommate
            )
            
            # Calculate additional charges and update total amount
            additional_charges = booking_pref.calculate_additional_charges()
            booking.total_amount += additional_charges
            booking.save()
            
            # If a roommate was selected, create a notification for them
            if preferred_roommate:
                Notification.objects.create(
                    user=preferred_roommate,
                    message=f"{request.user.username} has requested you as a roommate for booking #{booking.id} in room {room.room_number}.",
                    booking=booking
                )
            
            # Redirect to checkout page
            return redirect('checkout', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('book_room', room_id=room_id)
    
    # Get recommended roommates based on preferences if the user has set preferences
    recommended_roommates = []
    try:
        user_preferences = RoommatePreference.objects.get(user=request.user)
        all_preferences = RoommatePreference.objects.exclude(user=request.user)
        
        # Calculate compatibility scores
        for roommate_pref in all_preferences:
            score = 0
            total_factors = 4  # Number of factors we're comparing
            
            # Compare study habits
            if roommate_pref.study_habits == user_preferences.study_habits:
                score += 1
            
            # Compare cleanliness
            if roommate_pref.cleanliness == user_preferences.cleanliness:
                score += 1
            
            # Compare room preference
            if roommate_pref.room_preference == user_preferences.room_preference:
                score += 1
            
            # Compare sharing preference
            if roommate_pref.sharing_preference == user_preferences.sharing_preference:
                score += 1
            
            # Calculate percentage
            compatibility = int((score / total_factors) * 100)
            
            # Add to recommended list if compatibility is above 50%
            if compatibility >= 50:
                recommended_roommates.append({
                    'user': roommate_pref.user,
                    'compatibility': compatibility
                })
        
        # Sort by compatibility score
        recommended_roommates = sorted(recommended_roommates, key=lambda x: x['compatibility'], reverse=True)
    except RoommatePreference.DoesNotExist:
        # User doesn't have preferences set yet
        pass
    
    return render(request, 'book_room.html', {
        'room': room,
        'potential_roommates': potential_roommates,
        'recommended_roommates': recommended_roommates
    })

# PAYMENT CHECKOUT
@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # If booking is already paid, redirect to dashboard
    if booking.is_paid:
        messages.info(request, "This booking has already been paid.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Mark the booking as paid immediately
        booking.is_paid = True
        booking.status = 'confirmed'
        booking.save()
        
        # Create or update payment record
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            user=request.user,
            defaults={
                'amount': booking.total_amount,
                'status': 'Completed',
                'payment_method': 'Direct Payment'
            }
        )
        
        if not created:
            payment.status = 'Completed'
            payment.payment_method = 'Direct Payment'
            payment.save()
        
        # Create notification for booking confirmation
        Notification.objects.create(
            user=booking.user,
            message=f"Your booking #{booking.id} for {booking.room.room_number} has been confirmed.",
            booking=booking
        )
        
        messages.success(request, "Payment confirmed! Your room has been booked.")
        return redirect("dashboard")
    
    # Show the checkout page for GET requests
    return render(request, "checkout.html", {'booking': booking})

@login_required
def payment_success(request):
    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        payment_method = request.POST.get('payment_method')
        
        try:
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            # Only proceed if payment method is provided (from QR scan)
            if payment_method:
                # Mark the booking as paid
                booking.is_paid = True
                booking.status = 'confirmed'
                booking.save()

                # Update existing payment record
                payment = booking.payment_set.first()
                if payment:
                    payment.status = "Completed"
                    payment.payment_method = payment_method
                    payment.save()

                # Create notification for booking confirmation
                Notification.objects.create(
                    user=booking.user,
                    message=f"Your booking #{booking.id} for {booking.room.room_number} has been confirmed.",
                    booking=booking
                )

                messages.success(request, "Payment confirmed! Your room has been booked.")
                return redirect("dashboard")
            else:
                messages.error(request, "Please complete the payment process.")
                return redirect('checkout', booking_id=booking_id)
            
        except Booking.DoesNotExist:
            messages.error(request, "Invalid booking reference.")
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
    
    return redirect("dashboard")

# ROOMMATE FINDER
@login_required
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "booking_details.html", {'booking': booking})

@login_required
def roommate_finder(request):
    user_preferences = None
    roommates = []
    
    if request.method == 'POST':
        # Save user's preferences
        user_preferences = RoommatePreference.objects.update_or_create(
            user=request.user,
            defaults={
                'study_habits': request.POST.get('study_habits'),
                'cleanliness': request.POST.get('cleanliness'),
                'room_preference': request.POST.get('room_preference'),
                'sharing_preference': request.POST.get('sharing_preference'),
                'interests': request.POST.get('interests'),
            }
        )[0]
        
        # Find potential roommates
        roommates = RoommatePreference.objects.exclude(user=request.user)
        
        # Calculate compatibility scores
        for roommate in roommates:
            score = 0
            total_factors = 4  # Number of factors we're comparing
            
            # Compare study habits
            if roommate.study_habits == user_preferences.study_habits:
                score += 1
            
            # Compare cleanliness
            if roommate.cleanliness == user_preferences.cleanliness:
                score += 1
            
            # Compare room preference
            if roommate.room_preference == user_preferences.room_preference:
                score += 1
            
            # Compare sharing preference
            if roommate.sharing_preference == user_preferences.sharing_preference:
                score += 1
            
            # Calculate percentage
            roommate.compatibility_score = int((score / total_factors) * 100)
        
        # Sort by compatibility score
        roommates = sorted(roommates, key=lambda x: x.compatibility_score, reverse=True)
    
    return render(request, "roommate_finder.html", {
        'roommates': roommates,
        'user_preferences': user_preferences
    })

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect("home")

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def payment(request, payment_ref):
    # Check if payment_ref is a numeric ID or a PNR
    try:
        payment_id = int(payment_ref)
        payment = get_object_or_404(Payment, id=payment_id, booking__user=request.user)
    except ValueError:
        # If not a numeric ID, treat as PNR
        payment = get_object_or_404(Payment, booking__pnr=payment_ref, booking__user=request.user)
    
    booking = payment.booking
    
    if payment.status == 'Completed':
        messages.info(request, 'This payment has already been completed.')
        return redirect('dashboard')
    
    # Handle POST request (payment confirmation)
    if request.method == 'POST':
        # Mark the booking as paid
        booking.is_paid = True
        booking.status = 'confirmed'
        booking.save()
        
        # Update payment status
        payment.status = 'Completed'
        payment.save()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            message=f"Your payment for booking #{booking.id} has been confirmed.",
            booking=booking
        )
        
        messages.success(request, "Payment confirmed! Your booking has been confirmed.")
        return redirect('dashboard')
    
    # For development mode, show QR code scanner
    if getattr(settings, 'SKIP_STRIPE_PAYMENT', True):
        return render(request, "payment.html", {
            'booking': booking,
            'payment': payment,
            'qr_data': {
                'booking_id': booking.id,
                'amount': payment.amount,
                'reference': f"DORM-{booking.id}-{booking.user.username}"
            }
        })
    
    # For all modes, just show the payment page without QR
    context = {
        'payment': payment,
        'booking': booking,
        'amount': payment.amount,
    }
    return render(request, 'payment.html', context)

@login_required
def process_payment(request, payment_id):
    if settings.SKIP_STRIPE_PAYMENT:
        return JsonResponse({'message': 'Payment processing is disabled in development mode'})
        
    payment = get_object_or_404(Payment, id=payment_id, booking__user=request.user)
    
    if request.method == 'POST':
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Convert to cents
                currency='usd',
                metadata={'payment_id': payment.id}
            )
            
            # Update payment status
            payment.status = 'Pending'
            payment.save()
            
            return JsonResponse({
                'client_secret': intent.client_secret
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Get statistics
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(is_available=False).count()
    available_rooms = Room.objects.filter(is_available=True).count()
    current_bookings = Booking.objects.filter(status='confirmed').count()
    
    # Get current bookings
    bookings = Booking.objects.filter(status='confirmed').order_by('-check_in_date')
    
    # Get upcoming check-outs
    today = timezone.now().date()
    seven_days_later = today + timedelta(days=7)
    upcoming_checkouts = Booking.objects.filter(
        status='confirmed',
        check_out_date__range=[today, seven_days_later]
    ).order_by('check_out_date')
    
    # Get all rooms
    rooms = Room.objects.all().order_by('room_number')
    
    context = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'current_bookings': current_bookings,
        'bookings': bookings,
        'upcoming_checkouts': upcoming_checkouts,
        'rooms': rooms,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def add_room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        floor = request.POST.get('floor')
        capacity = request.POST.get('capacity')
        price = request.POST.get('price')
        description = request.POST.get('description')
        
        # Create new room
        room = Room.objects.create(
            room_number=room_number,
            room_type=room_type,
            floor=floor,
            capacity=capacity,
            price=price,
            description=description,
            has_ac=request.POST.get('has_ac') == 'on',
            has_wifi=request.POST.get('has_wifi') == 'on',
            has_tv=request.POST.get('has_tv') == 'on',
            has_fridge=request.POST.get('has_fridge') == 'on',
            has_balcony=request.POST.get('has_balcony') == 'on',
            has_attached_bathroom=request.POST.get('has_attached_bathroom') == 'on',
        )
        
        # Handle room image
        if 'room_image' in request.FILES:
            room.image = request.FILES['room_image']
            room.save()
        
        messages.success(request, 'Room added successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'room_form.html')

@login_required
@user_passes_test(is_admin)
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room.room_number = request.POST.get('room_number')
        room.room_type = request.POST.get('room_type')
        room.floor = request.POST.get('floor')
        room.capacity = request.POST.get('capacity')
        room.price = request.POST.get('price')
        room.description = request.POST.get('description')
        room.has_ac = request.POST.get('has_ac') == 'on'
        room.has_wifi = request.POST.get('has_wifi') == 'on'
        room.has_tv = request.POST.get('has_tv') == 'on'
        room.has_fridge = request.POST.get('has_fridge') == 'on'
        room.has_balcony = request.POST.get('has_balcony') == 'on'
        room.has_attached_bathroom = request.POST.get('has_attached_bathroom') == 'on'
        
        if 'room_image' in request.FILES:
            room.image = request.FILES['room_image']
        
        room.save()
        messages.success(request, 'Room updated successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'room_form.html', {'room': room})

@login_required
@user_passes_test(is_admin)
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        # Check if room has active bookings
        has_active_bookings = Booking.objects.filter(
            room=room,
            status='confirmed',
            check_out_date__gt=timezone.now()
        ).exists()
        
        if has_active_bookings:
            messages.error(request, 'Cannot delete room with active bookings.')
            return redirect('admin_dashboard')
        
        room.delete()
        messages.success(request, 'Room deleted successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'confirm_delete.html', {'room': room})

@login_required
def booking_details(request, booking_id):
    # Get the booking with related user and room data
    booking = get_object_or_404(Booking.objects.select_related('user', 'room'), id=booking_id)
    
    # Check if the user is authorized to view this booking
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this booking.")
        return redirect('dashboard')
    
    # Render the appropriate template based on user type
    if request.user.is_staff:
        return render(request, 'admin_booking_details.html', {'booking': booking})
    else:
        return render(request, 'booking_details.html', {'booking': booking})

# This function has been moved to avoid duplication
# See the staff_member_required decorated cancel_booking function below

def generate_pdf_receipt(request, booking_id):
    # Get the booking
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is authorized to view this booking
    if booking.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to view this receipt")
    
    # Get the template
    template = get_template('receipt_pdf.html')
    
    # Prepare context
    context = {
        'booking': booking,
        'payment': booking.payment_set.first(),
        'pnr': f"DS{booking.id}{booking.check_in_date.strftime('%Y%m%d')}",
        'generated_date': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Render the template
    html = template.render(context)
    
    # Create PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    # Check if PDF generation was successful
    if not pdf.err:
        # Prepare response
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{booking.id}.pdf"'
        return response
    
    return HttpResponse("Error generating PDF", status=500)

@login_required
def notifications(request):
    # Get all notifications for the user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'notifications.html', {
        'notifications': notifications
    })

def get_notifications_count(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count(),
            'notifications': Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:5]
        }
    return {}


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully. You can now use your new password to sign in.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

def generate_pdf_receipt(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to view this receipt")

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))   

def chatbot_test(request):
    """View for testing the chatbot functionality"""
    return render(request, 'chatbot-test.html')

def chatbot_direct(request):
    """View for direct testing of the chatbot without Django dependencies"""
    return render(request, 'chatbot-direct.html')
# For Option 1
def payment(request, payment_ref):
    try:
        # First try to find by ID
        payment_obj = get_object_or_404(Payment, id=int(payment_ref))
    except (ValueError, TypeError):
        # If that fails, try by PNR
        payment_obj = get_object_or_404(Payment, pnr=payment_ref)
    # Rest of your view logic

# For Option 2 (if using separate patterns)
def payment_by_pnr(request, pnr):
    payment_obj = get_object_or_404(Payment, pnr=pnr)
    # Rest of your view logic
@login_required
def generate_pdf_receipt(request, booking_id):
    """Generate a PDF receipt for a booking"""
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Check if booking is paid
        if not booking.is_paid:
            messages.error(request, "Cannot generate receipt for unpaid booking.")
            return redirect('dashboard')
        
        # Get payment information
        payment = booking.payment_set.filter(status='Completed').first()
        if not payment:
            # If no completed payment is found, use any payment
            payment = booking.payment_set.first()
            if not payment:
                messages.error(request, "No payment found for this booking.")
                return redirect('dashboard')
        
        # Prepare context for PDF template
        context = {
            'booking': booking,
            'payment': payment,
            'user': request.user,
            'date': timezone.now().strftime('%B %d, %Y'),
            'receipt_number': f"DORM-{booking.id}-{payment.id}"
        }
        
        # Get the template
        template = get_template('receipt_template.html')
        html = template.render(context)
        
        # Create PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            # Set up the response with PDF mime type
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"receipt_{booking.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            # If PDF generation failed due to pisa error
            messages.error(request, f"Error generating PDF receipt: {pdf.err}")
            return redirect('dashboard')
    
    except Exception as e:
        # Catch any other exceptions
        messages.error(request, f"Error generating PDF receipt: {str(e)}")
        return redirect('dashboard')

@login_required
def process_payment(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Mark the booking as paid
        booking.is_paid = True
        booking.status = 'confirmed'
        booking.save()
        
        # Create or update payment record
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            user=request.user,
            defaults={
                'amount': booking.total_amount,
                'status': 'Completed',
                'payment_method': 'Direct Payment'
            }
        )
        
        if not created:
            payment.status = 'Completed'
            payment.save()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            message=f"Your payment for booking #{booking.id} has been confirmed.",
            booking=booking
        )
        
        messages.success(request, "Payment confirmed! Your booking has been confirmed.")
        return redirect('payment_success')
    
    return redirect('dashboard')

@login_required
def payment_success(request):
    return render(request, 'payment_success.html')

@staff_member_required
def add_room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        capacity = request.POST.get('capacity')
        price = request.POST.get('price')
        floor = request.POST.get('floor')
        is_available = request.POST.get('is_available') == 'True'
        amenities = request.POST.get('amenities')
        description = request.POST.get('description')
        
        # Check if room number already exists
        if Room.objects.filter(room_number=room_number).exists():
            messages.error(request, f"Room number {room_number} already exists.")
            return redirect('admin_dashboard')
        
        # Create new room
        Room.objects.create(
            room_number=room_number,
            room_type=room_type,
            capacity=capacity,
            price=price,
            floor=floor,
            is_available=is_available,
            amenities=amenities,
            description=description
        )
        
        messages.success(request, f"Room {room_number} has been added successfully.")
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')

@staff_member_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if room has active bookings
    if Booking.objects.filter(room=room, status='confirmed').exists():
        messages.error(request, f"Cannot delete room {room.room_number} as it has active bookings.")
        return redirect('admin_dashboard')
    
    room_number = room.room_number
    room.delete()
    
    messages.success(request, f"Room {room_number} has been deleted successfully.")
    return redirect('admin_dashboard')

@staff_member_required
def admin_dashboard(request):
    # Get statistics
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    occupied_rooms = total_rooms - available_rooms
    current_bookings = Booking.objects.filter(status='confirmed').count()
    
    # Get all rooms
    rooms = Room.objects.all().order_by('room_number')
    
    # Get active bookings (confirmed and not cancelled)
    bookings = Booking.objects.filter(status='confirmed').order_by('-booking_date')
    
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'current_bookings': current_bookings,
        'rooms': rooms,
        'bookings': bookings,
    }
    
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        capacity = request.POST.get('capacity')
        price = request.POST.get('price')
        floor = request.POST.get('floor')
        is_available = request.POST.get('is_available') == 'True'
        amenities = request.POST.get('amenities')
        description = request.POST.get('description')
        
        # Check if room number already exists and is not this room
        if Room.objects.filter(room_number=room_number).exclude(id=room_id).exists():
            messages.error(request, f"Room number {room_number} already exists.")
            return redirect('admin_dashboard')
        
        # Update room
        room.room_number = room_number
        room.room_type = room_type
        room.capacity = capacity
        room.price = price
        room.floor = floor
        room.is_available = is_available
        room.amenities = amenities
        room.description = description
        room.save()
        
        messages.success(request, f"Room {room_number} has been updated successfully.")
        return redirect('admin_dashboard')
    
    context = {
        'room': room
    }
    
    return render(request, 'edit_room.html', context)

@staff_member_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        # Only allow cancellation if the booking is not already cancelled
        if booking.status != 'cancelled':
            booking.status = 'cancelled'
            booking.save()
            
            # Make room available again
            room = booking.room
            room.is_available = True
            room.save()
            
            # Create notification for the user
            Notification.objects.create(
                user=booking.user,
                message=f"Your booking #{booking.id} for room {room.room_number} has been cancelled by the administrator.",
                booking=booking
            )
            
            messages.success(request, f"Booking #{booking_id} has been cancelled and notification sent to the user.")
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'This booking is already cancelled.')
            return redirect('admin_dashboard')
    
    # For GET requests, show confirmation page
    return render(request, 'cancel_booking.html', {
        'booking': booking
    })

@login_required
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "booking_details.html", {'booking': booking})

@login_required
def user_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        # Only allow cancellation if the booking is not already cancelled
        if booking.status != 'cancelled':
            booking.status = 'cancelled'
            booking.save()
            
            # Make room available again
            room = booking.room
            room.is_available = True
            room.save()
            
            # Create notification for the user
            Notification.objects.create(
                user=booking.user,
                message=f"Your booking #{booking.id} for room {room.room_number} has been cancelled successfully.",
                booking=booking
            )
            
            messages.success(request, f"Your booking #{booking_id} has been cancelled successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, 'This booking is already cancelled.')
            return redirect('dashboard')
    
    # For GET requests, show confirmation page
    return render(request, 'user_cancel_booking.html', {
        'booking': booking
    })

@staff_member_required
def admin_booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "admin_booking_details.html", {'booking': booking})

def chatbot_test(request):
    """View for testing the chatbot interface"""
    return render(request, "chatbot_test.html")

def chatbot_direct(request):
    """API endpoint for direct chatbot interactions"""
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        # Simple response logic - in a real app, this would connect to a more sophisticated chatbot
        responses = {
            'hello': 'Hi there! How can I help you with your hostel booking?',
            'booking': 'To make a booking, please go to our rooms page and select a room.',
            'check in': 'Check-in time is 2:00 PM. Please bring your ID and booking confirmation.',
            'check out': 'Check-out time is 11:00 AM. Please return your key to the reception.',
            'wifi': 'Yes, we provide free WiFi in all our rooms and common areas.',
            'breakfast': 'Breakfast is served from 7:00 AM to 10:00 AM in the dining area.',
            'parking': 'Yes, we have parking available for guests at an additional charge.',
            'cancel': 'To cancel a booking, please go to your dashboard and select the booking you wish to cancel.',
        }
        
        # Default response if no keywords match
        response = "I'm not sure how to help with that. Please contact our reception for assistance."
        
        # Check if any keywords match
        for keyword, resp in responses.items():
            if keyword.lower() in message.lower():
                response = resp
                break
        
        return JsonResponse({'response': response})
    
    return JsonResponse({'error': 'Only POST requests are supported'}, status=400)

@login_required
def profile_view(request):
    """View user profile"""
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')
    
    context = {
        'user': user,
        'bookings': bookings,
    }
    
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'edit_profile.html', context)
