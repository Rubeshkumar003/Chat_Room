import pytest
from django.test import Client
from django.urls import reverse
from channels.testing import WebsocketCommunicator
from ChatApp.consumer import ChatConsumer
from ChatApp.models import Room, Message
from asgiref.sync import sync_to_async

@pytest.mark.django_db
class TestChatApp:

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.fixture
    def room(self):
        return Room.objects.create(room_name="test_room")

    def test_message_view(self, client, room):
        url = reverse('room', kwargs={'room_name': room.room_name, 'username': 'user'})
        response = client.get(url)
        assert response.status_code == 200
        assert 'messages' in response.context
        assert 'user' in response.context
        assert 'room_name' in response.context

    @pytest.mark.asyncio
    async def test_chat_consumer(self, room):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/notification/{room.room_name}/"
        )
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({
            'message': 'Hello',
            'room_name': room.room_name,
            'sender': 'user'
        })

        response = await communicator.receive_json_from()
        assert response['message']['sender'] == 'user'
        assert response['message']['message'] == 'Hello'

        messages = await sync_to_async(Message.objects.filter)(room=room)
        assert await sync_to_async(messages.count)() == 1

        await communicator.disconnect()

    def test_room_model(self, room):
        assert str(room) == "test_room"

    def test_message_model(self, room):
        message = Message.objects.create(room=room, sender="user", message="Test message")
        assert str(message) == str(room)