from fastapi import FastAPI
from schemas import ServiceRequest
from aiohttp import ClientSession

app = FastAPI('api_gateway')

services = {
    "service1": "https://service.first:8001",
    "service2": "https://service.second:8002",
}

@app.post('/api/gateway/')
async def forward_request(request: ServiceRequest):
    pass

async def request(service_url: str, request: dict | None):
    async with ClientSession() as session:
        session.request(method=request['method'], url = service_url, json=request['body'])