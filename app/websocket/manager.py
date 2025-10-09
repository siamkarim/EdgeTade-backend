"""
WebSocket Manager using Socket.IO
"""
import socketio
import asyncio
from typing import Dict, List
from loguru import logger

from app.core.config import settings
from app.services.price_feed import price_feed_service

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.CORS_ORIGINS if not settings.DEBUG else '*',
    logger=settings.DEBUG,
    engineio_logger=settings.DEBUG,
)

# Create ASGI app
socket_app = socketio.ASGIApp(sio)

# Connected clients
connected_clients: Dict[str, Dict] = {}


@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    connected_clients[sid] = {
        "subscriptions": [],
        "account_ids": [],
    }
    await sio.emit('connection_established', {'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    if sid in connected_clients:
        del connected_clients[sid]


@sio.event
async def subscribe_prices(sid, data):
    """Subscribe to price updates for specific symbols"""
    symbols = data.get('symbols', [])
    
    if sid in connected_clients:
        connected_clients[sid]['subscriptions'] = symbols
        logger.info(f"Client {sid} subscribed to: {symbols}")
        await sio.emit('subscribed', {'symbols': symbols}, room=sid)


@sio.event
async def subscribe_account(sid, data):
    """Subscribe to account updates"""
    account_id = data.get('account_id')
    
    if sid in connected_clients and account_id:
        if account_id not in connected_clients[sid]['account_ids']:
            connected_clients[sid]['account_ids'].append(account_id)
        logger.info(f"Client {sid} subscribed to account: {account_id}")
        await sio.emit('account_subscribed', {'account_id': account_id}, room=sid)


@sio.event
async def unsubscribe_account(sid, data):
    """Unsubscribe from account updates"""
    account_id = data.get('account_id')
    
    if sid in connected_clients and account_id:
        if account_id in connected_clients[sid]['account_ids']:
            connected_clients[sid]['account_ids'].remove(account_id)
        logger.info(f"Client {sid} unsubscribed from account: {account_id}")


async def broadcast_price_updates():
    """Broadcast price updates to subscribed clients"""
    while True:
        try:
            # Update all prices
            for symbol in price_feed_service.base_prices.keys():
                price = await price_feed_service.get_price(symbol)
                
                # Send to subscribed clients
                for sid, client_data in connected_clients.items():
                    if symbol in client_data['subscriptions']:
                        await sio.emit('price_update', {
                            'symbol': symbol,
                            'bid': price['bid'],
                            'ask': price['ask'],
                            'timestamp': str(price['timestamp']),
                        }, room=sid)
            
            # Wait before next update
            await asyncio.sleep(settings.PRICE_UPDATE_INTERVAL_MS / 1000)
            
        except Exception as e:
            logger.error(f"Error broadcasting prices: {e}")
            await asyncio.sleep(1)


async def send_order_update(account_id: int, order_data: Dict):
    """Send order status update to subscribed clients"""
    for sid, client_data in connected_clients.items():
        if account_id in client_data['account_ids']:
            await sio.emit('order_update', order_data, room=sid)


async def send_account_update(account_id: int, account_data: Dict):
    """Send account balance/equity update to subscribed clients"""
    for sid, client_data in connected_clients.items():
        if account_id in client_data['account_ids']:
            await sio.emit('account_update', account_data, room=sid)


async def send_margin_call_alert(account_id: int, margin_level: float):
    """Send margin call alert"""
    alert_data = {
        'type': 'margin_call',
        'account_id': account_id,
        'margin_level': margin_level,
        'message': f'⚠️ Margin Call! Your margin level is {margin_level:.2f}%',
    }
    
    for sid, client_data in connected_clients.items():
        if account_id in client_data['account_ids']:
            await sio.emit('alert', alert_data, room=sid)


async def send_liquidation_alert(account_id: int):
    """Send auto-liquidation alert"""
    alert_data = {
        'type': 'auto_liquidation',
        'account_id': account_id,
        'message': '🚨 Auto-Liquidation Triggered! All positions are being closed.',
    }
    
    for sid, client_data in connected_clients.items():
        if account_id in client_data['account_ids']:
            await sio.emit('alert', alert_data, room=sid)


# Start background task when the app starts
async def start_background_tasks():
    """Start background tasks"""
    asyncio.create_task(broadcast_price_updates())
    asyncio.create_task(price_feed_service.simulate_price_updates(
        settings.PRICE_UPDATE_INTERVAL_MS
    ))
    logger.info("WebSocket background tasks started")

