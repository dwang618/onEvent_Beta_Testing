from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import logout
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import *
from .forms import EventForm, MessageForm
from django.views.decorators.http import require_POST
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'onevent/index.html', {})

def logout_view(request):
    logout(request)
    request.session.flush()  # Clear all session data
    return redirect('index')

@login_required
def dashboard(request):
    events = Event.objects.filter(user=request.user)  # Query events for the logged-in user
    friend_events = Event.objects.filter(user__in=[friend.user for friend in request.user.commonuser.friends.all()])
    friends = request.user.commonuser.friends.all()  # Fetch the user's friends

    email = request.POST.get('email')
    if email:
        if email == request.user.email:
            messages.error(request, "You cannot add yourself as a friend.")
            return redirect('dashboard')
        try:
            user = User.objects.get(email=email)
            common_user = user.commonuser
            request.user.commonuser.friends.add(common_user)
            messages.success(request, f"{common_user.user.username} has been added as a friend.")
        except ObjectDoesNotExist:
            messages.error(request, "No user with the provided email exists.")

    # Handle friend removal
    friend_id = request.POST.get('remove_friend_id')
    if friend_id:
        try:
            friend_to_remove = CommonUser.objects.get(id=friend_id)
            request.user.commonuser.friends.remove(friend_to_remove)
            messages.success(request, f"{friend_to_remove.user.username} has been removed from your friends list.")
        except ObjectDoesNotExist:
            messages.error(request, "The selected friend could not be found.")

    if request.user.groups.filter(name='PMA').exists():
        # User is in "PMA" group, fetch all uploads
        return render(request, 'onevent/admin_dashboard.html', {
            'user': request.user,
            'events': events,
            'friend_events': friend_events,
            'friends': friends,
        })
    else:
        return render(request, 'onevent/common_dashboard.html', {
            'user': request.user,
            'events': events,
            'friend_events': friend_events,
            'friends': friends,
        })


@login_required
def image_upload(request):
    events = Event.objects.filter(user=request.user)  # Fetch events the user has access to
    event_types = ["Map", "Minutes", "Budgeting", "Catering", "Contact", "Other"]

    if request.method == 'POST' and 'image_file' in request.FILES:
        image_file = request.FILES['image_file']
        title = request.POST.get('file_title', '')
        description = request.POST.get('file_description', '')
        event_id = request.POST.get('event_id')
        event_type = request.POST.get('file_type')
        # Check if event_type was selected
        if not event_type:
            messages.error(request, "File type must be selected.")
            return redirect('upload')  # Redirect back if file type is not selected


        event = None
        if event_id and event_id != 'no_event':
            try:
                # Fetch the event, ensuring the user has access to it
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                messages.error(request, "The selected event does not exist or you do not have access to it.")
                return redirect('upload')  # Redirect back to the upload page

        # Save the upload
        upload = Upload(file=image_file, title=title, description=description, event=event, user=request.user, file_type = event_type)
        upload.save()

    user = request.user
    if user.groups.filter(name='PMA').exists():
        # User is in "PMA" group, fetch all uploads
        uploaded_files = Upload.objects.all()
    else:
        # Fetch only user's uploads
        uploaded_files = Upload.objects.filter(user=user)

    return render(request, 'onevent/upload.html', {
        'uploaded_files': uploaded_files,
        'events': events,
        'event_types': event_types
    })


@login_required
def upload_details(request, upload_id):
    # Get the uploaded file by its ID
    upload = get_object_or_404(Upload, id=upload_id)
    file_url = upload.file.url.lower()

    is_image = any(file_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
    is_text = file_url.endswith('.txt')
    is_pdf = file_url.endswith('.pdf')

    return render(request, 'onevent/upload_details.html', {
        'upload': upload,
        'is_image': is_image,
        'is_text': is_text,
        'is_pdf': is_pdf,
    })

@login_required
def delete_upload(request, upload_id):
    if request.method == 'POST':
        # Get the uploaded file by its ID
        upload = get_object_or_404(Upload, id=upload_id)

        # Delete the associated file from storage (if applicable)
        upload.file.delete()  # This deletes the actual file from storage

        # Delete the object from the database
        upload.delete()

        # Redirect back to the upload page (or wherever appropriate)
        return redirect('upload')

@login_required
def event_list(request):
    events = Event.objects.filter(created_by=request.user)
    form = EventForm()
    return render(request, 'dashboard.html', {'events': events, 'form': form})

@login_required
@require_POST
def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')

        if title and description and date:
            event = Event.objects.create(
                title=title,
                description=description,
                date=date,
                user=request.user
            )
            # Include description in the response
            return JsonResponse({
                'success': True,
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event.date
            })

        return JsonResponse({'success': False, 'errors': 'Invalid data'})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = EventForm(request.POST, instance=event)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'title': event.title})
    return JsonResponse({'success': False, 'errors': form.errors})

@login_required
@require_POST
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return JsonResponse({'success': True})

@login_required
def event_details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    messages = event.messages.all().order_by('-timestamp')
    form = MessageForm()

    if request.method == 'POST':
        if 'content' in request.POST:
            # Handle new message submission
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.event = event
                message.author = request.user
                message.save()
                return redirect('event_details', event_id=event.id)
        elif 'like_message_id' in request.POST:
            # Handle like action
            message_id = request.POST.get('like_message_id')
            message = get_object_or_404(Message, pk=message_id)
            if request.user in message.likes.all():
                message.likes.remove(request.user)
            else:
                message.likes.add(request.user)
            return redirect('event_details', event_id=event.id)
        elif 'delete_message_id' in request.POST:
            # Handle delete action
            message_id = request.POST.get('delete_message_id')
            message = get_object_or_404(Message, pk=message_id)
            if request.user == message.author or request.user.groups.filter(name='PMA').exists():
                message.delete()
            return redirect('event_details', event_id=event.id)
        elif 'rsvp_id' in request.POST:
            if request.user in event.rsvps.all():
                event.rsvps.remove(request.user)
            else:
                event.rsvps.add(request.user)
            return redirect('event_details', event_id=event.id)

    # Fetch uploads associated with the event
    uploads = event.uploads.all()

    context = {
        'event': event,
        'messages': messages,
        'form': form,
        'uploads': uploads,  # Add uploads to context
    }
    return render(request, 'onevent/event_details.html', context)


@login_required
def admin_dashboard(request):

    sort_by = request.GET.get('sort_by', 'date')
    order = request.GET.get('order', 'asc')

    # Map sorting options to model fields
    sort_options = {
        'title': 'title',
        'date': 'date',
        'username': 'user__username',
    }

    sort_field = sort_options.get(sort_by, 'date')

    if order == 'desc':
        sort_field = '-' + sort_field

    events = Event.objects.all().order_by(sort_field)
    if request.method == 'POST':
        # Handle deletion
        if 'delete_event' in request.POST:
            event_id = request.POST.get('delete_event')
            event = get_object_or_404(Event, id=event_id)
            event.delete()
            messages.success(request, "Event deleted successfully.")
            return redirect('admin_dashboard')
        if 'event_id' in request.POST:
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)
            form = EventForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                messages.success(request, "Event updated successfully.")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm()

        # Handle edits (optional, more complex logic required for editing)
    return render(request, 'onevent/all_events.html', {'events': events})