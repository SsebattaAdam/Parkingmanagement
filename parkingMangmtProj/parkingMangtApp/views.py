from decimal import Decimal
import json
import re
from django.core.mail import send_mail
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib import messages

from io import BytesIO
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from django.contrib.auth.decorators import login_required
from .models import Cart, ExpenditureItem, ParkingTicket, UserPermission
from psutil import users
from parkingMangtApp.models import Business
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

from .models import AccountBalance, ActivityLog, Client, Expenditure, ExpenditureCategory, ParkingRate, ParkingSlot, ParkingTicket, Branch, ParkingSlot, Branch, Business
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum  # Import Sum here
from django.contrib.auth.decorators import login_required
from .models import Branch, Expenditure, ExpenditureCategory, AccountBalance
from parkingMangtApp import models
from django.contrib.auth import get_user_model
User = get_user_model()

def admin_required(user):
    return user.role == 'ADMIN'
def admin_or_staff_required(user):
    return user.role in ['ADMIN', 'STAFF']
def clients_table(request):
    # Retrieve all clients
    all_clients = Client.objects.select_related('branch').all()

    # Retrieve all branches and their respective clients
    branches_with_clients = Branch.objects.prefetch_related('clients').all()

    return render(request, 'tables/client_tables.html', {
        'all_clients': all_clients,
        'branches_with_clients': branches_with_clients,
    })

def index(request):
    branches_count = Branch.objects.count()
    clients_count = Client.objects.count()
    total_slots_count = ParkingSlot.objects.count()
    available_slots_count = ParkingSlot.objects.filter(is_available=True).count()

    context = {
        'branches_count': branches_count,
        'clients_count': clients_count,
        'total_slots_count': total_slots_count,
        'available_slots_count': available_slots_count,
    }
    return render(request, 'index.html', context)
def branchpage(request):
    return render(request, 'Branches.html')
def registerpage(request):
    return render(request, 'auth/register.html')
def loginpage(request):
    return render(request, 'auth/login.html')
def businesspage(request):
    return render(request, 'business.html')


def branch_tables(request):
    branches = Branch.objects.all()
    return render(request, 'tables/branch_tables.html', {'branches': branches})
def business_tables(request):
    businesses = Business.objects.all()
    return render(request, 'tables/business_tables.html', {'businesses': businesses})
def user_tables(request):
    users = User.objects.all()
    return render(request, 'tables/user_tables.html', {'users': users})
    
@login_required
def user_permission(request):
    User = get_user_model()  # Ensure we are using the custom user model

    # Ensure only users with the ADMIN role can access this page
    if request.user.role != User.Role.ADMIN.value:
        return redirect('index')  # Redirect non-ADMIN users

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        permission, created = UserPermission.objects.get_or_create(user=user)
        permission.can_view_reports = 'can_view_reports' in request.POST
        permission.can_manage_branches = 'can_manage_branches' in request.POST
        permission.can_issue_tickets = 'can_issue_tickets' in request.POST
        permission.can_register_clients = 'can_register_clients' in request.POST
        permission.save()
        return redirect('user_permission')

    # Filter users to include only those with the specified roles
    users = User.objects.filter(
        role__in=[
            User.Role.ADMIN.value, 
            User.Role.USER.value, 
            User.Role.MANAGER.value
        ]
    )

    return render(request, 'tables/userpermission.html', {'users': users})


@login_required
def branches_view(request):
    branches = Branch.objects.all()
    return render(request, 'branches/branches.html', {'branches': branches})
@login_required
def branch_detail_view(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    rates = ParkingRate.objects.filter(branch=branch)
    # Get counts for the branch
    total_tickets = ParkingTicket.objects.filter(branch=branch).count()
    total_slots = ParkingSlot.objects.filter(branch=branch).count()
    total_available_slots = ParkingSlot.objects.filter(branch=branch, is_available=True).count()
    total_clients = Client.objects.filter(branch=branch).count()
    # total_payments = Payment.objects.filter(branch=branch).count()
    
    # Get tickets for the branch
    tickets = ParkingTicket.objects.filter(branch=branch)

    context = {
        'rates': rates,
        'branch': branch,
        'total_tickets': total_tickets,
        'total_slots': total_slots,
        'total_available_slots': total_available_slots,
        'total_clients': total_clients,
        # 'total_payments': total_payments,
        'tickets': tickets,  # Include tickets in the context
    }
    return render(request, 'branches/branch_detail.html', context)

@login_required
def branch_detail22(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    rates = ParkingRate.objects.filter(branch=branch)
    # Get counts for the branch
    total_tickets = ParkingTicket.objects.filter(branch=branch).count()
    total_slots = ParkingSlot.objects.filter(branch=branch).count()
    total_available_slots = ParkingSlot.objects.filter(branch=branch, is_available=True).count()
    total_clients = Client.objects.filter(branch=branch).count()
    # total_payments = Payment.objects.filter(branch=branch).count()
    
    # Get tickets for the branch
    tickets = ParkingTicket.objects.filter(branch=branch)

    context = {
        'rates': rates,
        'branch': branch,
        'total_tickets': total_tickets,
        'total_slots': total_slots,
        'total_available_slots': total_available_slots,
        'total_clients': total_clients,
        # 'total_payments': total_payments,
        'tickets': tickets,  # Include tickets in the context
    }
    return render(request, 'SpecificBranch/branch_detail2.html', context)

@login_required
def parking_slot_from_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    slots = ParkingSlot.objects.filter(branch=branch)
    return render(request, 'SpecificBranch/add_parking_slots.html', {'slots': slots, 'branch': branch})
@login_required
def parking_rates_form(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    rate = ParkingRate.objects.filter(branch=branch)
    return render(request, 'SpecificBranch/add_parking_rates.html', {'rate': rate, 'branch': branch})

@login_required
def Client_display_From(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    rate = ParkingRate.objects.filter(branch=branch)
    return render(request, 'SpecificBranch/add_clients.html', {'rate': rate, 'branch': branch})




@login_required
def branc_ticket_table_view(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    rates = ParkingRate.objects.filter(branch=branch)
    # Get counts for the branch
    total_tickets = ParkingTicket.objects.filter(branch=branch).count()
    total_slots = ParkingSlot.objects.filter(branch=branch).count()
    total_available_slots = ParkingSlot.objects.filter(branch=branch, is_available=True).count()
    total_clients = Client.objects.filter(branch=branch).count()
    # total_payments = Payment.objects.filter(branch=branch).count()

    
    
    # Get tickets for the branch
    tickets = ParkingTicket.objects.filter(branch=branch)

    context = {
        'rates': rates,
        'branch': branch,
        'total_tickets': total_tickets,
        'total_slots': total_slots,
        'total_available_slots': total_available_slots,
        'total_clients': total_clients,
        # 'total_payments': total_payments,
        'tickets': tickets,  # Include tickets in the context
    }
    return render(request, 'SpecificBranch/ticket_table.html', context)

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # This automatically sets the role to the default
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("loginpage")  # Redirect to your login page
        else:
            messages.error(request, "Registration failed. Please fix the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "auth/register.html", {"form": form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use 'email' as username
        password = request.POST.get('password')  # Get password from form

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Log the user in
            print(f"User Role: {user.role}")  # Log user role for debugging

            # Role-based redirection
            if Branch.objects.filter(manager=user).exists(): 
                return redirect('branch_listpermanager')  # Redirect to admin dashboard
            elif user.role == 'ADMIN':
                return redirect('index')  # Redirect to staff dashboard
            elif user.role == 'USER':
                return redirect('user_dashboard')  # Redirect to user dashboard
            elif Branch.objects.filter(manager=user).exists():
                return redirect('branch_listpermanager')  # Redirect managers to their branches
            else:
                messages.error(request, "Your role is not defined. Please contact the administrator.")
                return redirect('loginpage')  # Redirect to login page for undefined roles
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('loginpage')  # Redirect to login page if authentication fails

    return render(request, 'auth/login.html')  # Render the login page


@login_required
def create_business(request):
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        contact_details = request.POST.get('contact_details')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        website_url = request.POST.get('website_url')
        registration_number = request.POST.get('registration_number')
        tax_id = request.POST.get('tax_id')
        is_active = bool(request.POST.get('is_active', False))

        # Save data to the database with user tracking
        try:
            Business.objects.create(
                business_name=business_name,
                contact_details=contact_details,
                email=email,
                phone_number=phone_number,
                website_url=website_url,
                registration_number=registration_number,
                tax_id=tax_id,
                is_active=is_active,
                created_by=request.user,  # Track the user who created the business
            )
            messages.success(request, "Business created successfully!")
            return redirect('business-create')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'business.html')

 
    return render(request, 'business.html')
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Business, Branch, UserPermission, ParkingSlot

User = get_user_model()  # Get the custom User model

@login_required
def create_branch(request):
    if request.method == 'POST':
        branch_name = request.POST.get('branch_name')
        location = request.POST.get('location')
        contact_number = request.POST.get('contact_number')
        is_active = request.POST.get('is_active') == 'on'
        is_main_branch = request.POST.get('is_main_branch') == 'on'
        manager_first_name = request.POST.get('manager_first_name')
        manager_last_name = request.POST.get('manager_last_name')
        manager_email = request.POST.get('manager_email')
        parking_slot_identifier = request.POST.get('parking_slot_identifier', 'B')  # Default to 'B'
        number_of_slots = int(request.POST.get('number_of_slots', 50))  # Default to 50

        try:
            business = Business.objects.first()
            if not business:
                messages.error(request, "No business is registered yet.")
                return redirect('branchpage')

            if is_main_branch and Branch.objects.filter(business=business, is_main_branch=True).exists():
                messages.error(request, "This business already has a main branch.")
                return redirect('branchpage')

            with transaction.atomic():
                # Create the branch
                branch = Branch.objects.create(
                    business=business,
                    branch_name=branch_name,
                    location=location,
                    contact_number=contact_number,
                    is_active=is_active,
                    is_main_branch=is_main_branch,
                    created_by=request.user,
                    parking_slot_identifier=parking_slot_identifier,
                    number_of_slots=number_of_slots
                )

                # Use the `create_manager` method from Branch model
                username, password = branch.create_manager(manager_first_name, manager_last_name, manager_email)

                # Assign default permissions for the manager
                UserPermission.objects.create(
                    user=branch.manager,
                    can_manage_branches=True,
                    can_issue_tickets=True
                )

                # Create parking slots for the branch
                branch.create_parking_slots()

            # Send email with credentials
            subject = "Your Manager Account Credentials"
            message = (
                f"Hello {manager_first_name},\n\n"
                f"You have been assigned as the manager for {branch_name}.\n"
                f"Here are your login credentials:\n"
                f"Username: {username}\n"
                f"Password: {password}\n\n"
                f"Please log in and change your password as soon as possible.\n\n"
                f"Best regards,\nYour Company"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [manager_email], fail_silently=False)

            messages.success(request, f"Branch created successfully! Manager credentials sent to {manager_email}")
            return redirect('branch-create')

        except Exception as e:
            messages.error(request, f"An error occurred while creating the branch: {str(e)}")
            return redirect('branchpage')

    return render(request, 'Branches.html')

from django.utils.timezone import now
from .models import ActivityLog

def log_activity(user, branch, activity_type, details):
    ActivityLog.objects.create(
        user=user,
        branch=branch,
        activity_type=activity_type,
        details=details,
        timestamp=now()
    )



@login_required
def add_parking_slot(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        slot_number = request.POST.get('slot_number')
        is_available = request.POST.get('is_available') == 'on'

        if not slot_number:
            messages.error(request, "Parking slot number is required.")
            return redirect('branch_detail22', branch_id=branch.id)

        if branch.parking_slots.count() >= 25:
            messages.error(request, "This branch already has 25 parking slots.")
            return redirect('branch_detail22', branch_id=branch.id)

        if branch.parking_slots.filter(slot_number=slot_number).exists():
            messages.error(request, f"Slot number '{slot_number}' already exists in this branch.")
            return redirect('branch_detail22', branch_id=branch.id)

        ParkingSlot.objects.create(
            branch=branch,
            slot_number=slot_number,
            is_available=is_available,
            created_by=request.user
        )

        # Log the activity
        log_activity(request.user, branch, 'user_activity', f"Added parking slot {slot_number}.")

        messages.success(request, "Parking slot added successfully.")
        return redirect('branch_detail22', branch_id=branch.id)

    messages.error(request, "Invalid request method.")
    return redirect('branch_detail22', branch_id=branch.id)


def view_parking_slots(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    parking_slots = ParkingSlot.objects.filter(branch=branch)  # Get all slots for this branch

    context = {
        'branch': branch,
        'parking_slots': parking_slots
    }
    return render(request, 'SpecificBranch/view_parkingslots.html', context)

def clients_by_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    clients = Client.objects.filter(branch=branch)  # Get all clients for this branch

    return render(request, 'SpecificBranch/clientstablespecific.html', {'branch': branch, 'clients': clients})



@login_required
@transaction.atomic
def register_client(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        vehicle_number_plate = request.POST.get('vehicle_number', '').upper().strip()

        # Updated regex pattern:
        # - Starts and ends with a capital letter
        # - Contains at least one number
        # - Allows Uganda government plates (UG, etc.)
        plate_pattern = re.compile(r"^[A-Z]+ [0-9]+[A-Z]?$")

        if not vehicle_number_plate:
            messages.error(request, "Vehicle number plate is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        # Validate plate format
        if not plate_pattern.match(vehicle_number_plate):
            messages.error(request, "Invalid vehicle number plate format! Ensure it starts and ends with a capital letter and contains numbers.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        # Ensure unique number plate
        if Client.objects.filter(vehicle_number_plate=vehicle_number_plate).exists():
            messages.error(request, "This vehicle is already registered.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        # Find an available parking slot
        parking_slot = ParkingSlot.objects.filter(branch=branch, is_available=True).first()
        if not parking_slot:
            messages.warning(request, "No parking slots are available. Please add a parking slot before registering a client.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        # Register the client
        client = Client.objects.create(
            branch=branch,
            vehicle_number_plate=vehicle_number_plate,
            registered_by=request.user,
        )

        # Mark parking slot as occupied
        parking_slot.is_available = False
        parking_slot.save()

        # Issue parking ticket
        ParkingTicket.objects.create(
            client=client,
            parking_slot=parking_slot,
            branch=branch,
        )

        # Log the activity
        log_activity(request.user, branch, 'user_activity', f"Registered client with vehicle {vehicle_number_plate}.")

        messages.success(request, f"Client registered, and parking ticket issued for Slot {parking_slot.slot_number}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@transaction.atomic
def activate_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    branch = client.branch

    # Ensure the client has a ticket and is cleared
    if not hasattr(client, 'ticket') or not client.ticket.exit_time:
        messages.error(request, "This client is not cleared and cannot be activated.")
        return redirect('clients_by_branch', branch_id=branch.id)

    # Find an available parking slot (reusing the logic from register_client)
    parking_slot = ParkingSlot.objects.filter(branch=branch, is_available=True).first()
    if not parking_slot:
        messages.warning(request, "No parking slots are available. Please add a parking slot before activating a client.")
        return redirect('clients_by_branch', branch_id=branch.id)

    # Reset the client's parking details
    ticket = client.ticket
    ticket.entry_time = timezone.now()
    ticket.exit_time = None
    ticket.duration = None
    ticket.fee_to_pay = None
    ticket.parking_slot = parking_slot
    ticket.save()

    # Mark the new parking slot as occupied
    parking_slot.is_available = False
    parking_slot.save()

    # Log the activity
    log_activity(request.user, branch, 'user_activity', f"Activated client with vehicle {client.vehicle_number_plate}.")

    messages.success(request, f"Client activated and assigned to Slot {parking_slot.slot_number}.")
    return redirect('clients_by_branch', branch_id=branch.id)

@login_required
@transaction.atomic
def generate_ticket(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        contact_number = request.POST.get('contact_number')
        vehicle_number = request.POST.get('vehicle_number')
        parking_slot_id = request.POST.get('parking_slot')

        if not all([client_name, contact_number, vehicle_number, parking_slot_id]):
            messages.error(request, "All fields are required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        parking_slot = get_object_or_404(ParkingSlot, id=parking_slot_id, branch=branch, is_available=True)

        client, created = Client.objects.get_or_create(
            vehicle_number_plate=vehicle_number,
            defaults={'name': client_name, 'contact_info': contact_number, 'branch': branch}
        )

        ticket = ParkingTicket.objects.create(
            client=client,
            branch=branch,
            parking_slot=parking_slot,
        )

        parking_slot.is_available = False
        parking_slot.save()

        # Log the activity
        log_activity(request.user, branch, 'user_activity', f"Generated parking ticket for {client_name} ({vehicle_number}).")

        messages.success(request, f"Ticket generated for {client_name} at Slot {parking_slot.slot_number}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from io import BytesIO
from django.shortcuts import get_object_or_404
from .models import ParkingTicket


@login_required
def download_ticket(request, ticket_id):
    ticket = get_object_or_404(ParkingTicket, id=ticket_id)

    # Create a buffer for the PDF
    buffer = BytesIO()

    # Create the PDF object
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Define the content of the PDF
    content = []

    # Header
    header = Paragraph("PARKING RECEIPT", styles['Title'])
    content.append(header)
    content.append(Spacer(1, 12))

    # Ticket Information
    ticket_info = [
        ["Ticket #", ticket.id],
        ["Date", ticket.entry_time.strftime('%m/%d/%Y')],
        ["Time", ticket.entry_time.strftime('%H:%M')],
        ["Location", ticket.branch.location],
        ["Branch", ticket.branch.branch_name],
        ["Amount", f"{ticket.fee_to_pay} UGX"],
        ["Manager", ticket.branch.manager],
    ]
    ticket_table = Table(ticket_info, colWidths=[150, 300])
    ticket_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(ticket_table)
    content.append(Spacer(1, 12))

    # Vehicle Information
    vehicle_info = [
        ["Plate Number", ticket.client.vehicle_number_plate],
        ["State", "UG"],
    ]
    vehicle_table = Table(vehicle_info, colWidths=[150, 300])
    vehicle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(vehicle_table)
    content.append(Spacer(1, 12))

    # Payment Information
    payment_info = [
        ["Total Amount", f"{ticket.fee_to_pay} UGX"],
        ["Payment Status", f"{ticket.payment_status} UGX"],
    ]
    payment_table = Table(payment_info, colWidths=[150, 300])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(payment_table)
    content.append(Spacer(1, 12))

    # Footer
    footer = Paragraph("Thank you for using our parking services!", styles['Italic'])
    content.append(footer)

    # Build the PDF
    pdf.build(content)

    # Get the value of the buffer and return it as a response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    return response

def add_parking_rate(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        rate_type = request.POST.get('rate_type')
        rate_value = request.POST.get('rate_value')

        # Create and save the new rate for the branch
        ParkingRate.objects.create(
            branch=branch,
            rate_type=rate_type,
            rate_value=rate_value
        )

        # Redirect back to the branch detail page after saving the rate
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@transaction.atomic
def clear_tickets(request):
    if request.method == "POST":
        try:
            # Parse the request body
            data = json.loads(request.body.decode('utf-8'))
            print("Received Data:", data)  # Log incoming data

            # Validate required fields
            ticket_id = data.get('ticket_id')
            branch_id = data.get('branch_id')

            if not ticket_id or not branch_id:
                print("Error: Missing ticket_id or branch_id")
                return JsonResponse({"error": "Missing ticket_id or branch_id"}, status=400)

            # Fetch ticket and branch
            try:
                ticket = ParkingTicket.objects.get(id=ticket_id)
                branch = Branch.objects.get(id=branch_id)
            except ParkingTicket.DoesNotExist:
                print(f"Error: Ticket with ID {ticket_id} not found")
                return JsonResponse({"error": f"Ticket with ID {ticket_id} not found"}, status=404)
            except Branch.DoesNotExist:
                print(f"Error: Branch with ID {branch_id} not found")
                return JsonResponse({"error": f"Branch with ID {branch_id} not found"}, status=404)

            # Check if the ticket is already cleared
            if ticket.exit_time:
                print("Error: Ticket already cleared")
                return JsonResponse({"error": "This ticket has already been cleared."}, status=400)

            # Set exit time and calculate payment
            ticket.exit_time = timezone.now()
            ticket.duration = (ticket.exit_time - ticket.entry_time).total_seconds() / 60  # Duration in minutes
            ticket.fee_to_pay = ticket.calculate_fee()  # Ensure this method exists in your model
            ticket.payment_status = 'Pending'
            ticket.save()

            # Mark parking slot as available
            ticket.parking_slot.is_available = True
            ticket.parking_slot.save()

            # Log the activity
            log_activity(request.user, branch, 'user_activity', f"Cleared ticket for {ticket.client.vehicle_number_plate}.")

            # Prepare response data
            response_data = {
                "message": "Ticket cleared successfully",
                "ticket_id": ticket.id,
                "branch_id": branch.id,
                "exit_time": ticket.exit_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": ticket.duration,
                "fee_to_pay": ticket.fee_to_pay,
                "payment_status": ticket.payment_status
            }

            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            print("Error: Invalid JSON data")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
@transaction.atomic
def clear_ticket(request, ticket_id, branch_id):
    ticket = get_object_or_404(ParkingTicket, id=ticket_id)
    branch = get_object_or_404(Branch, id=branch_id)

    if ticket.exit_time:
        messages.error(request, "This ticket has already been cleared.")
        return redirect('branch_detail22', branch_id=ticket.branch.id)

    # Set the exit time and calculate the fee
    ticket.exit_time = timezone.now()
    ticket.payment_status = 'Pending'  # Reset payment status
    ticket.duration = (ticket.exit_time - ticket.entry_time).total_seconds() / 60  # Duration in minutes
    ticket.fee_to_pay = ticket.calculate_fee()  # Calculate the fee
    ticket.save()

    # Mark the parking slot as available
    ticket.parking_slot.is_available = True
    ticket.parking_slot.save()

    # Log the activity
    log_activity(request.user, ticket.branch, 'user_activity', f"Cleared ticket for {ticket.client.vehicle_number_plate}.")

    # Redirect to the payment confirmation page
    return redirect('confirm_payment', ticket_id=ticket.id, branch_id=ticket.branch.id)
@login_required
@transaction.atomic
def confirm_payment(request, ticket_id, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)  # Use a different variable name
    ticket = get_object_or_404(ParkingTicket, id=ticket_id)

    if ticket.branch.id != branch.id:
        messages.error(request, "Invalid branch for this ticket.")
        return redirect('branch_detail22', branch_id=branch.id)  # Use branch.id

    if ticket.payment_status == 'Paid':
        messages.error(request, "This ticket has already been paid.")
        return redirect('branch_detail22', branch_id=branch.id)  # Use branch.id

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # Update ticket payment details
        ticket.payment_status = 'Paid'
        ticket.payment_method = payment_method
        ticket.save()

        # Update account balance
        account_balance = AccountBalance.objects.get(branch=ticket.branch)
        if payment_method == 'cash':
            account_balance.cash += ticket.fee_to_pay
        elif payment_method == 'bank':
            account_balance.bank += ticket.fee_to_pay
        elif payment_method == 'mobile_money':
            account_balance.mobile_money += ticket.fee_to_pay
        account_balance.save()

        # Log the activity
        log_activity(request.user, ticket.branch, 'user_activity', f"Processed payment for {ticket.client.vehicle_number_plate} via {payment_method}.")

        messages.success(request, f"Payment of {ticket.fee_to_pay} received via {payment_method}.")
        return redirect('branch_detail22', branch_id=branch.id)  # Use branch.id

    return render(request, 'SpecificBranch/confirm_payment.html', {'ticket': ticket, 'branch': branch})

@login_required
def delete_client(request, client_id):
    # Retrieve the client
    client = get_object_or_404(Client, id=client_id)
    
    # Check if the client has any uncleared tickets
    uncleared_ticket = ParkingTicket.objects.filter(client=client, exit_time__isnull=True).first()
    
    if uncleared_ticket:
        messages.error(
            request, 
            f"Client with vehicle number {client.vehicle_number_plate} cannot be deleted because their parking ticket (ID: {uncleared_ticket.id}) is still uncleared."
        )
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  # Redirect back
    
    # Release the parking slot, if applicable
    cleared_ticket = ParkingTicket.objects.filter(client=client).first()
    if cleared_ticket and cleared_ticket.parking_slot:
        parking_slot = cleared_ticket.parking_slot
        parking_slot.is_available = True
        parking_slot.save()

    # Delete the client and their related tickets
    ParkingTicket.objects.filter(client=client).delete()
    client.delete()

    messages.success(request, f"Client with vehicle number {client.vehicle_number_plate} and their tickets have been deleted successfully.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  

def delete_business(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    business.delete()
    messages.success(request, "Business deleted successfully.")
    return redirect('business-tables')




@login_required
def branch_list(request):
    """Show only branches managed by the logged-in manager."""
    branches = Branch.objects.filter(manager=request.user)  # Only fetch branches where the manager matches the logged-in user

    return render(request, 'branches/specificmanager.html', {'branches': branches})


@login_required
def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    # Delete the manager if assigned
    if branch.manager:
        manager = branch.manager
        branch.manager = None  # Remove the manager from the branch
        branch.save()
        manager.delete()  # Delete the manager user account

    # Delete the branch
    branch.delete()
    messages.success(request, "Branch and manager details deleted successfully.")
    return redirect('branch-tables')  

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.user == user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user-tables')  # Change 'user-list' to your actual URL name
    
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('user-tables')


@login_required
def branch_recent_expenses(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    expenditures = Expenditure.objects.filter(branch=branch).order_by('-date')
    categories = ExpenditureCategory.objects.all()
    
    # Get or create account balance for the branch
    balances, created = AccountBalance.objects.get_or_create(branch=branch)

    # Calculate total expenditure for the branch
    total_expenditures = expenditures.aggregate(total=Sum('amount'))['total'] or 0

    # Calculate remaining balance
    remaining_balance = balances.cash + balances.bank + balances.mobile_money

    # Fetch cart items for the logged-in user
    cart_items = Cart.objects.filter(user=request.user, branch=branch)
    
    # Calculate the total cost from the cart
    total_cart_cost = sum(item.total_cost() for item in cart_items)

    # Available payment methods
    payment_methods = ['cash', 'bank', 'mobile_money']

    context = {
        'branch': branch,
        'expenditures': expenditures,
        'categories': categories,
        'balances': balances,
        'total_expenditures': total_expenditures,
        'remaining_balance': remaining_balance,
        'cart_items': cart_items,  # Pass cart items
        'total_cart_cost': total_cart_cost,  # Pass total cost of cart
        'payment_methods': payment_methods,  # Pass payment methods
    }
    return render(request, 'SpecificBranch/recent_expensetabel.html', context)

from django.shortcuts import redirect
from django.contrib import messages

def add_category(request, branch_id):
    if request.method == 'POST':
        category_name = request.POST.get('category_name', '').strip()
        items = request.POST.getlist('items[]')

        if not category_name:
            messages.error(request, "Category name is required.")
            return redirect(request.META.get('HTTP_REFERER', 'branch_expenditures'))  # Redirect back

        # Check if the category already exists
        category, created = ExpenditureCategory.objects.get_or_create(
            name=category_name, 
            defaults={'created_by': request.user}
        )

        if not created:  # If category already exists
            messages.error(request, "Category already exists!")
            return redirect(request.META.get('HTTP_REFERER', 'branch_expenditures'))  # Redirect back

        # Add items to the category
        for item_name in items:
            if item_name.strip():
                ExpenditureItem.objects.create(category=category, item_name=item_name.strip(), created_by=request.user)

        messages.success(request, "Category added successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'branch_expenditures'))  # Redirect back

    messages.error(request, "Invalid request.")
    return redirect(request.META.get('HTTP_REFERER', 'branch_expenditures'))  # Redirect back



@login_required
def add_expenditures(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    cart_items = Cart.objects.filter(user=request.user, branch=branch)

    if request.method == 'POST':
        with transaction.atomic():
            for cart_item in cart_items:
                expenditure = Expenditure.objects.create(
                    branch=branch,
                    category=cart_item.category,
                    item_name=cart_item.item_name,
                    quantity=cart_item.quantity,
                    price_per_item=cart_item.price_per_item,
                    amount=cart_item.total_cost(),
                    payment_method=cart_item.payment_method,
                    created_by=request.user
                )

                # Update account balance
                account_balance = AccountBalance.objects.get(branch=branch)
                if cart_item.payment_method == 'cash':
                    account_balance.cash -= expenditure.amount
                elif cart_item.payment_method == 'bank':
                    account_balance.bank -= expenditure.amount
                elif cart_item.payment_method == 'mobile_money':
                    account_balance.mobile_money -= expenditure.amount
                account_balance.save()

            # Clear the cart
            cart_items.delete()

        messages.success(request, "Expenditures added successfully.")
        return redirect('branch_expenditures', branch_id=branch.id)

    return redirect('branch_expenditures', branch_id=branch.id)

@login_required
def branch_expenditures(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    expenditures = Expenditure.objects.filter(branch=branch).order_by('-date')
    categories = ExpenditureCategory.objects.all()
    items = ExpenditureItem.objects.filter(category__in=categories)
    
    # Get or create account balance for the branch
    balances, created = AccountBalance.objects.get_or_create(branch=branch)

    # Calculate total expenditure for the branch
    total_expenditures = expenditures.aggregate(total=Sum('amount'))['total'] or 0

    # Calculate remaining balance
    remaining_balance = balances.cash + balances.bank + balances.mobile_money

    # Fetch cart items for the logged-in user
    cart_items = Cart.objects.filter(user=request.user, branch=branch)
    
    # Calculate the total cost from the cart
    total_cart_cost = sum(item.total_cost() for item in cart_items)

    # Available payment methods
    payment_methods = ['cash', 'bank', 'mobile_money']

    context = {
        'branch': branch,
        'expenditures': expenditures,
        'categories': categories,
        'items': items,
        'balances': balances,
        'total_expenditures': total_expenditures,
        'remaining_balance': remaining_balance,
        'cart_items': cart_items,
        'total_cart_cost': total_cart_cost,
        'payment_methods': payment_methods,
    }
    return render(request, 'SpecificBranch/branch_expenditures.html', context)

@login_required
def edit_expenditure(request, expenditure_id):
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)
    
    
    if request.method == 'POST':
        expenditure.category = get_object_or_404(ExpenditureCategory, id=request.POST['category'])
        expenditure.amount = request.POST['amount']
        expenditure.payment_method = request.POST['payment_method']
        if 'proof_of_payment' in request.FILES:
            expenditure.proof_of_payment = request.FILES['proof_of_payment']
        expenditure.save()
        messages.success(request, "Expenditure updated successfully.")
        return redirect('branch_expenditures', branch_id=expenditure.branch.id)
    
    
    
    return render(request, 'SpecificBranch/edit_expenditure.html', {'expenditure': expenditure})

@login_required
def add_to_cart(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        category_id = request.POST.get('category')
        item_name = request.POST.get('item_name', '').strip()  # Ensure it's not None
        quantity = int(request.POST.get('quantity', 1))
        price_per_item = Decimal(request.POST.get('price_per_item', 0))

        if not item_name:  # Validate item_name
            messages.error(request, "Item name is required.")
            return redirect('branch_expenditures', branch_id=branch.id)

        if category_id == "new":
            category_name = request.POST.get('new_category', '').strip()
            if category_name:
                category, created = ExpenditureCategory.objects.get_or_create(
                    name=category_name,
                    defaults={'created_by': request.user}
                )
            else:
                messages.error(request, "New category name is required.")
                return redirect('branch_expenditures', branch_id=branch.id)
        else:
            category = get_object_or_404(ExpenditureCategory, id=category_id)

        # Check if item already exists in cart, update quantity if it does
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            branch=branch,
            category=category,
            item_name=item_name,  # Now item_name is guaranteed to be valid
            defaults={'quantity': quantity, 'price_per_item': price_per_item}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, "Item added to cart.")
        return redirect('branch_expenditures', branch_id=branch.id)

    return redirect('branch_expenditures', branch_id=branch_id)


@login_required
def view_cart(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    cart_items = Cart.objects.filter(user=request.user, branch=branch)

    # Calculate the exact total cost based on item quantities
    total_cost = sum(item.total_cost() for item in cart_items)

    payment_methods = ['cash', 'bank', 'mobile_money']  

    return render(request, 'SpecificBranch/cart.html', {
        'branch': branch,
        'cart_items': cart_items,
        'total_cost': total_cost,
        'payment_methods': payment_methods,
    })


@login_required
def checkout_cart(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    cart_items = Cart.objects.filter(user=request.user, branch=branch)

    if not cart_items:
        messages.error(request, "Cart is empty.")
        return redirect('view_cart', branch_id=branch_id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method not in ['cash', 'bank', 'mobile_money']:
            messages.error(request, "Invalid payment method.")
            return redirect('branch_expenditures', branch_id=branch_id)

        total_cost = sum(item.total_cost() for item in cart_items)

        # Deduct from account balance
        balances = AccountBalance.objects.get(branch=branch)

        if payment_method == 'cash' and balances.cash >= total_cost:
            balances.cash -= total_cost
        elif payment_method == 'bank' and balances.bank >= total_cost:
            balances.bank -= total_cost
        elif payment_method == 'mobile_money' and balances.mobile_money >= total_cost:
            balances.mobile_money -= total_cost
        else:
            messages.error(request, "Insufficient balance.")
            return redirect('branch_expenditures', branch_id=branch_id)

        balances.save()

        # Move items from cart to expenditures
        for item in cart_items:
            Expenditure.objects.create(
                branch=branch,
                category=item.category,
                item_name=item.item_name,
                quantity=item.quantity,
                price_per_item=item.price_per_item,
                amount=item.total_cost(),
                payment_method=payment_method,
                created_by=request.user
            )

        cart_items.delete()
        messages.success(request, "Checkout successful.")
        return redirect('branch_expenditures', branch_id=branch_id)

    return redirect('branch_expenditures', branch_id=branch_id)

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    branch_id = cart_item.branch.id
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('branch_expenditures', branch_id=branch_id)


@login_required
def delete_expenditure(request, expenditure_id):
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)
    branch_id = expenditure.branch.id
    
    # Update account balance before deletion
    account_balance = AccountBalance.objects.get(branch=expenditure.branch)
    if expenditure.payment_method == 'cash':
        account_balance.cash += expenditure.amount
    elif expenditure.payment_method == 'bank':
        account_balance.bank += expenditure.amount
    elif expenditure.payment_method == 'mobile_money':
        account_balance.mobile_money += expenditure.amount
    account_balance.save()

    expenditure.delete()
    messages.success(request, "Expenditure deleted successfully.")
    return redirect('branch_expenditures', branch_id=branch_id)

@login_required
def add_category_ajax(request):
    if request.method == 'POST':
        category_name = request.POST.get('name')
        if category_name:
            category, created = ExpenditureCategory.objects.get_or_create(name=category_name, created_by=request.user)
            return JsonResponse({'success': True, 'category': {'id': category.id, 'name': category.name}})
        return JsonResponse({'success': False, 'error': 'Category name is required.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})





def update_balances(request, branch_id):
    if request.method == 'POST':
        branch = get_object_or_404(Branch, id=branch_id)
        account_balance, created = AccountBalance.objects.get_or_create(branch=branch)
        account_balance.cash = request.POST.get('cash', 0)
        account_balance.bank = request.POST.get('bank', 0)
        account_balance.mobile_money = request.POST.get('mobile_money', 0)
        account_balance.save()
        messages.success(request, 'Balances updated successfully.')
    return redirect('branch_expenditures', branch_id=branch_id)

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.http import HttpResponse
import csv
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from .models import ActivityLog, Branch
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
@login_required
def branch_activity_report(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    
    # Get the logged-in user
    user = request.user  

    # Check if the user has permission to view reports
    try:
        user_permission = UserPermission.objects.get(user=user)
        if not user_permission.can_view_reports:
            return redirect(request.META.get('HTTP_REFERER', request.path)) # Redirect if user lacks permission
    except UserPermission.DoesNotExist:
        return redirect(request.META.get('HTTP_REFERER', request.path))  # Redirect if permission record does not exist

    activities = ActivityLog.objects.filter(branch=branch).order_by('-timestamp')

    # Get the custom user model
    User = get_user_model()
    users = User.objects.all()  # Fetch users correctly

    # Filtering
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    user_id = request.GET.get("user")

    if start_date:
        activities = activities.filter(timestamp__date__gte=start_date)
    if end_date:
        activities = activities.filter(timestamp__date__lte=end_date)
    if user_id:
        activities = activities.filter(user_id=user_id)

    # Pagination
    paginator = Paginator(activities, 10)
    page_number = request.GET.get("page")
    activities_page = paginator.get_page(page_number)

    context = {
        "branch": branch,
        "activities": activities_page,
        "users": users,  
    }
    return render(request, "SpecificBranch/branch_activity_report.html", context)

# Export CSV (Branch Specific)
@login_required
def export_branch_csv(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    activities = ActivityLog.objects.filter(branch=branch)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{branch.branch_name}_activity_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "User", "Activity", "Details"])

    for activity in activities:
        writer.writerow([activity.timestamp, activity.user, activity.activity_type, activity.details])

    return response


from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.contrib.auth.decorators import login_required
from .models import Branch, ActivityLog
from django.utils.dateparse import parse_date
import logging

logger = logging.getLogger(__name__)

@login_required
def export_branch_pdf(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    activities = ActivityLog.objects.filter(branch=branch)

    # Handle date range filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        # Log the dates and queryset for debugging
        logger.info(f"Start Date: {start_date}, End Date: {end_date}")
        logger.info(f"Activities before filtering: {activities.count()}")

        activities = activities.filter(timestamp__date__range=[start_date, end_date])

        logger.info(f"Activities after filtering: {activities.count()}")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{branch.branch_name}_activity_report.pdf"'

    # Create the PDF object
    pdf = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Add title
    title = Paragraph(f"Activity Report for {branch.branch_name}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Handle empty queryset
    if not activities.exists():
        no_data_message = Paragraph("No activities found within the specified date range.", styles['BodyText'])
        elements.append(no_data_message)
    else:
        # Prepare table data
        data = [["Date", "Time", "User", "Activity Details"]]

        for activity in activities:
            date_part = activity.timestamp.strftime("%Y-%m-%d")  # Extract date only
            time_part = activity.timestamp.strftime("%H:%M")  # Extract hours & minutes

            user_text = Paragraph(str(activity.user), styles['BodyText'])  # Ensure user text wraps properly
            activity_details = Paragraph(activity.details, styles['BodyText'])  # Ensure details wrap properly

            # Append row
            data.append([date_part, time_part, user_text, activity_details])

            # Add a page break after each row if it's too long
            if len(activity.details) > 100 or len(str(activity.user)) > 50:  # Adjust threshold as needed
                elements.append(Table(data, colWidths=[1.5 * inch, 1.2 * inch, 1.8 * inch, 3.5 * inch]))
                elements.append(PageBreak())
                data = [["Date", "Time", "User", "Activity Details"]]  # Reset table header for new page

        # Add remaining data as a table
        if len(data) > 1:  # Ensure the table is not empty
            table = Table(data, colWidths=[1.5 * inch, 1.2 * inch, 1.8 * inch, 3.5 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),  # Green header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F5F5F5")),  # Light gray rows
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table)

    # Build the PDF
    pdf.build(elements)
    return response