from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import User, Room, Message
from datetime import datetime

def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_password = request.POST.get('user_password') # Grab user password
        room_name = request.POST.get('room')
        room_password = request.POST.get('room_password') # Grab room password

        if not username or not user_password or not room_name or not room_password:
            messages.error(request, 'All fields are required.')
            return redirect('index')

        # --- 1. USER AUTHENTICATION ---
        user = User.objects.filter(username=username).first()
        if user:
            # User exists, check if password is correct
            # NOTE: If your models.py stores passwords as plain text, change this to: if user.password != user_password:
            if not user.check_password(user_password): 
                messages.error(request, 'Incorrect Profile Password.')
                return redirect('index')
        else:
            # User doesn't exist, create new user
            user = User(username=username)
            user.set_password(user_password)
            user.save()

        # --- 2. ROOM AUTHENTICATION ---
        room = Room.objects.filter(name=room_name).first()
        if room:
            # Room exists, check if password is correct
            # NOTE: If your models.py stores passwords as plain text, change this to: if room.password != room_password:
            if not room.check_password(room_password): 
                messages.error(request, 'Incorrect Room Password.')
                return redirect('index')
        else:
            # Room doesn't exist, create new room
            room = Room(name=room_name)
            room.set_password(room_password)
            room.save()

        # Save successful login to session
        request.session['user_id'] = user.id
        request.session['room_id'] = room.id

        Message.objects.create(user=user, room=room, content=f"{user.username} joined the room.")

        return redirect('chat')

    return render(request, 'index.html')


def chat(request):
    user_id = request.session.get('user_id')
    room_id = request.session.get('room_id')

    if not user_id or not room_id:
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    room = get_object_or_404(Room, id=room_id)

    messages_list = Message.objects.filter(room=room).order_by('timestamp')

    context = {
        'user': user,
        'room': room,
        'messages': messages_list,
    }
    return render(request, 'chat.html', context)


def send_message(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        room_id = request.session.get('room_id')

        if not user_id or not room_id:
            return JsonResponse({'error': 'Not authenticated'}, status=403)

        user = get_object_or_404(User, id=user_id)
        room = get_object_or_404(Room, id=room_id)

        content = request.POST.get('content')

        # FIXED: Changed 'sender=user' back to 'user=user'
        message = Message.objects.create(
            content=content,
            user=user,
            room=room
        )

        return JsonResponse({
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            # FIXED: Changed message.sender to message.user
            'sender': message.user.username,
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


def getMessages(request, room_id):
    try:
        room = get_object_or_404(Room, id=room_id)
        messages_list = Message.objects.filter(room=room).order_by('timestamp')
        
        messages_data = []
        for msg in messages_list:
            # Format timestamp to readable format
            timestamp = msg.timestamp.strftime('%I:%M %p')  # Format: 10:46 AM
            
            messages_data.append({
                'id': msg.id,
                # FIXED: Changed msg.sender to msg.user
                'sender': msg.user.username,
                'sender_id': msg.user.id,
                'val': msg.content,
                'date': timestamp,
            })
        
        return JsonResponse({'messages': messages_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)