import time

import requests

URL = 'http://127.0.0.1:8000/'


def test_assets():
    """
    Тест проверяет что сервер отдаёт index.html и все необходимые статические файлы подгружаются
    """
    response = requests.get(URL)
    assert response.status_code == 200, "Не удалось загрузить страницу index.html"

    page_content = response.content.decode('utf-8')
    assert '<script src="/static/lariska.js"></script>' in page_content
    assert '<script src="/static/script.js"></script>' in page_content
    assert '<link rel="stylesheet" type="text/css" href="/static/style.css"/>' in page_content

    # check that all static files are loaded
    response_lariska = requests.get(URL + 'static/lariska.js')
    assert response_lariska.status_code == 200, "Не удалось подгрузить lariska.js"

    response_script = requests.get(URL + 'static/script.js')
    assert response_script.status_code == 200, "Не удалось подгрузить script.js"

    response_style = requests.get(URL + 'static/style.css')
    assert response_style.status_code == 200, "Не удалось подгрузить style.css"


def test_all(client,events):

    client.connect(URL)
    assert client.connected, 'Client not connected to server'

    client.emit('get_rooms',{})
    time.sleep(0.1)

    rooms = events.get('rooms')
    assert rooms, "Don't get event 'rooms' on event 'get_rooms' "
    assert rooms['text'] == ['lobby','general','random']

    client.emit('join',{'room':'general','name':'Valerunchik', 'messages':'Hello'})
    time.sleep(0.1)

    move = events.get('move')
    assert move, "Don't get event 'move' on event 'join' "
    assert move['room'] == 'general', f'Room user incorrect. Waiting room name general, get room name {move["room"]}'

    client.emit('send_message',{'text':'Hello','author':'Valerunchik'})
    time.sleep(0.1)

    message = events.get('message')
    assert message, '''Don't get event 'message' on event 'send_message' '''
    assert message['name'] == 'Valerunchik', f'Name user incorrect. Waiting user Valerunchik, get user {message["name"]}'
    assert message['text'] == 'Hello', f'''Text user incorrect. Waiting text 'Hello', get text {message['text']} '''

    client.emit('leave')
    time.sleep(0.1)

    leave = events.get('sio_leave')
    assert leave, '''Don't get event 'sio_leave' on event 'leave' '''
    assert leave['text'] == 'You left the room', f'''Waiting 'You left the room', get {leave['text']} '''

