from celery import shared_task
from .models import Message, Room

@shared_task
def save_message(room_name, sender, message):
    get_room_by_name = Room.objects.get(room_name=room_name)
    if not Message.objects.filter(message=message).exists():
        new_message = Message(room=get_room_by_name, sender=sender, message=message)
        new_message.save()
        return f"Saved message: {message}"

@shared_task
def notify_users(data):
    print(f"Notifying users: {data}")
    return f"Notified users about: {data}"

