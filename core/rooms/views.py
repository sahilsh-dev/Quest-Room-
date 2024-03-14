from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import QuestRoomForm
from .models import QuestRoom


def home(request):
    if request.user.is_authenticated:
        return redirect('rooms:view_rooms')
    return render(request, 'rooms/home.html')


@login_required
def view_rooms(request):
    rooms = request.user.rooms.all()
    return render(request, 'rooms/rooms.html', {'rooms': rooms})


@login_required
def create_room(request):
    form = QuestRoomForm()
    if request.method == 'POST':
        form = QuestRoomForm(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data['name']
            if QuestRoom.objects.filter(name=room_name, head=request.user).exists():
                form.add_error('name', 'Room with this name already exists')
                return render(request, 'rooms/create_room.html', {'form': form})

            room = form.save(commit=False)
            room.head = request.user
            room.expires_at = timezone.now() + timezone.timedelta(days=room.expire_days)
            room.save()
            return redirect('rooms:view_rooms')
    return render(request, 'rooms/create_room.html', {'form': form})
