import secrets
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import QuestRoomForm
from .models import QuestRoom, Message, RoomCode

ROOM_INVITE_CODE_LENGTH = 7


def home(request):
    if request.user.is_authenticated:
        return redirect('rooms:view_rooms')
    return render(request, 'rooms/home.html')


@login_required
def view_rooms(request):
    rooms = request.user.rooms.all()
    return render(request, 'rooms/user_rooms.html', {'rooms': rooms})


@login_required
def create_room(request):
    form = QuestRoomForm()
    if request.method == 'POST':
        form = QuestRoomForm(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data['name']
            if QuestRoom.objects.filter(name=room_name, created_by=request.user).exists():
                form.add_error('name', 'Room with this name already exists')
                return render(request, 'rooms/create_room.html', {'form': form})

            room = form.save(commit=False)
            room.created_by = request.user
            room.expires_at = timezone.now() + timezone.timedelta(days=room.expire_days)
            room.save()
            room.members.add(request.user)
            room.admins.add(request.user)
            return redirect('rooms:view_rooms')
    return render(request, 'rooms/create_room.html', {'form': form})


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(QuestRoom, pk=room_id)
    latest_messages = Message.latest_messages.get_latest_messages(room_id)
    return render (
        request, 
        'rooms/room_detail.html', {
            'room': room,
            'latest_messages': latest_messages,
        }
    )


@login_required
def generate_room_code(request, room_id):
    if request.user in get_object_or_404(QuestRoom, pk=room_id).admins.all():
        upper_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        random_str = ''.join(secrets.choice(upper_chars) for _ in range(ROOM_INVITE_CODE_LENGTH))
        code = (random_str + str(room_id))[-ROOM_INVITE_CODE_LENGTH:]
        room_code = RoomCode.objects.create(room_id=room_id, code=code, generated_by=request.user)
        room_code.save()
        return JsonResponse({'code': code})
