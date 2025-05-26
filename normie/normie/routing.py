"""
WebSocket routing configuration for normie project.
"""

from django.urls import path
from normieapp import consumers

websocket_urlpatterns = [
    # Add WebSocket URL patterns here
    # Example: path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
] 