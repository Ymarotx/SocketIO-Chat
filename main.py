import asyncio
import logging
import random

import socketio
import sqlalchemy.exc
import uvicorn
from sqlalchemy import insert, delete

from database.database import create_tables,async_session_maker
from database.models import Users

from src.models import User,Message


static_files = {'/': 'static/index.html', '/static': './static'}
sio = socketio.AsyncServer(cors_allowed_origins='*',async_mode='asgi')
app = socketio.ASGIApp(sio,static_files=static_files)
logging.basicConfig(level='INFO',
                    # filename='logs.log',
                    format='%(filename)s:%(lineno)d #%(levelname)-8s'
                           '[%(asctime)s)] - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


@sio.event
async def connect(sid,environ):
    try:
        await create_tables()
    except sqlalchemy.exc.ProgrammingError:
        pass
    logger.info(f'Connect new user {sid}')
    # Решил вспомнить работу с БД далее будем работать с session_user :)
    async with async_session_maker() as session:
        query = insert(Users).values([{'username':'None',
                                       'sid': f'{sid}'}])
        await session.execute(query)
        await session.commit()
    await sio.save_session(sid=sid,session={'room':None,
                                      'name':None,
                                      })
    assert await sio.get_session(sid=sid), f'Ошибка сохранения сессии для sid={sid}'


@sio.on('get_rooms')
async def get_rooms(sid,data):
    rooms = ['lobby', 'general', 'random']
    await sio.emit('rooms',to=sid,data={'text':f'{rooms}'})

@sio.event
async def join(sid,data):
    response = User(**data)
    session = await sio.get_session(sid=sid)
    assert session, f'Fault in get session, expected not null dict, get {session}'
    session['room'] = response.room
    session['name'] = response.name
    await sio.save_session(sid=sid,session=session)
    await sio.enter_room(sid=sid,room=session['room'])
    rooms_user = sio.rooms(sid=sid)
    assert session['room'] in rooms_user, f"User wasn't add in the room {session['room']}"
    await sio.emit('move',to=sid,data={'room':f'{session["room"]}'})

@sio.event
async def leave(sid,data):
    session = await sio.get_session(sid=sid)
    await sio.leave_room(sid=sid,room=session['room'])
    session['room'] = "None"
    await sio.save_session(sid=sid,session=session)
    await sio.emit('leave',to=sid,data={'text':'You left the room'})

@sio.event
async def send_message(sid,data):
    session = await sio.get_session(sid=sid)
    response = Message(**data)
    room = session['room']
    await sio.emit('message',room=room,data={'name':f'{response.author}','text':f'{response.text}'})


@sio.event
async def disconnect(sid):
    logger.info(f'The User with {sid} disconnect')
    async with async_session_maker() as session:
        query = delete(Users).filter(Users.sid == f'{sid}')
        await session.execute(query)
        await session.commit()


if __name__ == '__main__':
    uvicorn.run(app,host='127.0.0.1',port=8000)














