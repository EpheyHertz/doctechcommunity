from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth.forms import SetPasswordForm
from .utils import upload_image_to_backblaze

# Create your views here.



from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator as account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.query_utils import Q




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse



@login_required
def follow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user != request.user:
        if request.user in target_user.followers.all():
            target_user.followers.remove(request.user)
        else:
            target_user.followers.add(request.user)
            # Send follow notification email
            send_follow_email(request,request.user, target_user)
    return redirect(reverse('user-profile', args=[user_id]))


@login_required
def like_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if the user has already liked the room
    if request.user in room.likes.all():
        # If already liked, remove the like
        room.likes.remove(request.user)
    else:
        # Otherwise, add the like and remove from dislikes if needed
        room.likes.add(request.user)
        room.dislikes.remove(request.user)
        
        # Send like notification email
        send_like_email(request, request.user, room.host, 'room', room.id)

    return redirect(reverse('room', args=[room_id]))

@login_required
def dislike_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if the user has already disliked the room
    if request.user in room.dislikes.all():
        # If already disliked, remove the dislike
        room.dislikes.remove(request.user)
    else:
        # Otherwise, add the dislike and remove from likes if needed
        room.dislikes.add(request.user)
        room.likes.remove(request.user)

    return redirect(reverse('room', args=[room_id]))

@login_required
def like_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if the user has already liked the message
    if request.user in message.likes.all():
        # If already liked, remove the like
        message.likes.remove(request.user)
    else:
        # Otherwise, add the like and remove from dislikes if needed
        message.likes.add(request.user)
        message.dislikes.remove(request.user)
        
        # Send like notification email
        send_like_email(request, request.user, message.user, 'message', message.room.id)

    return redirect(reverse('room', args=[message.room.id]))

@login_required
def dislike_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if the user has already disliked the message
    if request.user in message.dislikes.all():
        # If already disliked, remove the dislike
        message.dislikes.remove(request.user)
    else:
        # Otherwise, add the dislike and remove from likes if needed
        message.dislikes.add(request.user)
        message.likes.remove(request.user)

    return redirect(reverse('room', args=[message.room.id]))

def send_like_email(request,from_user, to_user, like_type,like_id):
    subject = f"Your {like_type} received a like!"
    current_site = get_current_site(request)
    # Render HTML content
    html_content = render_to_string('like_notification.html', {
        'from_user': from_user.username,
        'to_user': to_user.username,
        'like_id':like_id,
        'like_type': like_type,
        'site_url':current_site.domain,
        'site_name': 'DocTech Community'
    })

    # Prepare plain text version (if necessary, or just a simple message)
    text_content = f"Hi {to_user.username}, your {like_type} received a like from {from_user.username} on DocTech Community!"

    # Create EmailMultiAlternatives object
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # Plain text content
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_user.email]
    )

    # Attach HTML content
    email.attach_alternative(html_content, "text/html")

    # Send email
    email.send()

def send_follow_email(request,from_user, to_user):
    subject = f"{from_user.username} is now following you!"
    current_site = get_current_site(request)
    # Render HTML content
    html_content = render_to_string('follow_notification.html', {
        'from_user': from_user.username,
        'to_user': to_user.username,
        'user_id':to_user.id,
        'site_url':current_site.domain,
        'site_name': 'Doctech Community'
    })

    # Prepare plain text version
    text_content = f"Hi {to_user.username}, {from_user.username} is now following you on DocTech Community!"

    # Create EmailMultiAlternatives object
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # Plain text content
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_user.email]
    )

    # Attach HTML content
    email.attach_alternative(html_content, "text/html")

    # Send email
    email.send()


def handler404(request, exception, template_name="404.html"):
    response = render(request, template_name, status=404)
    return response

def handler500(request, template_name="500.html"):
    response = render(request, template_name, status=500)
    return response

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        # Check if the username or email already exists
        username = request.POST.get('username').lower()
        email_address = request.POST.get('email').lower()

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email_address).exists():
            messages.error(request, 'Email is already registered')
        else:
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.email = email_address  # Ensure email is lowercased
                user.is_active = False  # Set the user as inactive until email is verified

                try:
                    user.save()  # Save the user before sending the email

                    # Send email verification
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your DocTech Community account'
                    
                    # Prepare the context for email template
                    context = {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                    }

                    # Render the HTML version of the email
                    html_message = render_to_string('email_verification_template.html', context)

                    # Create an email with both plain text and HTML
                    email = EmailMultiAlternatives(
                        subject=mail_subject,
                        body='Hi There,',  # Plain text version
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email],
                    )
                    email.attach_alternative(html_message, "text/html")  # Attach HTML version
                    email.send()

                    messages.success(request, 'Please check your email to activate your account.')
                    return redirect('login')

                except Exception as e:
                    # import traceback
                    # traceback.print_exc()  # Log the error
                    messages.error(request, 'Email could not be sent. Please try again later.')
            else:
                # print(form.errors)  # Debug form errors
                messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})

# def activate(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):
#         user.is_active = True
#         user.save()
#         messages.success(request, 'Your account has been activated. You can now log in.')
#         return render(request, 'base/activation_successful.html', {'user': user})
#     else:
#         messages.error(request, 'Activation link is invalid or expired!')
#         return render(request, 'base/activation_failed.html')



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Send activation success email
        current_site = get_current_site(request)
        mail_subject = 'Your DocTech Community account has been activated'
        
        # Prepare the context for email template
        context = {
            'user': user,
            'domain': current_site.domain,
            'login_url': f"http://{current_site.domain}/login",  # Link to login page
        }

        # Render the HTML version of the email
        html_message = render_to_string('account_activated.html', context)

        # Create an email with both plain text and HTML
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body='Your account has been successfully activated. You can now log in.',  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")  # Attach HTML version
        email.send()

        messages.success(request, 'Your account has been activated. You can now log in.')
        return render(request, 'base/activation_successful.html', {'user': user})
    else:
        messages.error(request, 'Activation link is invalid or expired!')
        return render(request, 'base/activation_failed.html')

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')




def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})




@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Handle the avatar upload
            avatar = form.cleaned_data.get('avatar')  # Get the uploaded avatar image from the form
            # print(avatar)
            if avatar:
                avatar_url = upload_image_to_backblaze(avatar)  # Upload the image to Backblaze
                user.avatar_url = avatar_url  # Save the returned avatar URL to the user model
                # print(avatar_url)
            form.save()  # Save the user profile with other form data
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
