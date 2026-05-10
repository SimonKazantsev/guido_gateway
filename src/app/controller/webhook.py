from app.kafka.client import KafkaClient
from app.controller.abstract import AbstractController
from fastapi import Request

class WebhookController(AbstractController):
    async def handle(self, request: Request):
        print('yay')