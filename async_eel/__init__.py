from async_eel.utils import *
from async_eel import browsers
from aiohttp.web_ws import WebSocketResponse
from aiohttp.web import BaseRequest
from aiohttp import web
from expiringdict import ExpiringDict
from typing import Optional, Callable, Dict
from logging import getLogger, ERROR
from random import random
import socket
import asyncio
import json
import re
import sys
import os


# logging
getLogger('aiohttp').setLevel(ERROR)
log = getLogger(__name__)

# inner objects
routes = web.RouteTableDef()
loop = asyncio.get_event_loop()

# inner vars
_eel_js_file = os.path.join(os.path.dirname(__file__), 'eel.js')
_eel_js = open(_eel_js_file, encoding='utf-8').read()
_websockets = list()
_call_return_futures: Dict[int, asyncio.Future] = ExpiringDict(max_len=5000, max_age_seconds=300)
_call_number = 0
_exposed_functions = dict()
_js_functions = list()
_mock_queue = list()
_mock_queue_done = set()

# All start() options must provide a default value and explanation here
_start_args = {
    'mode':             'chrome',                   # What browser is used
    'host':             'localhost',                # Hostname use for Bottle server
    'port':             8000,                       # Port used for Bottle server (use 0 for auto)
    'block':            True,                       # Whether start() blocks calling thread
    'jinja_templates':  None,                       # Folder for jinja2 templates
    'cmdline_args':     ['--disable-http-cache'],   # Extra cmdline flags to pass to browser start
    'size':             None,                       # (width, height) of main window
    'position':         None,                       # (left, top) of main window
    'geometry':         {},                         # Dictionary of size/position for all windows
    'close_callback':   None,                       # Callback for when all windows have closed
    'app_mode':  True,                              # (Chrome specific option)
    'all_interfaces': False,                        # Allow bottle server to listen for connections on all interfaces
    'disable_cache': True,                          # Sets the no-store response header when serving assets
    'auto_close': True,                             # Auto close process when websocket connection is zero
}

# == Temporary (suppressable) error message to inform users of breaking API change for v1.0.0 ===
_start_args['suppress_error'] = False
api_error_message = '''
----------------------------------------------------------------------------------
  'options' argument deprecated in v1.0.0, see https://github.com/ChrisKnott/Eel
  To suppress this error, add 'suppress_error=True' to start() call.
  This option will be removed in future versions
----------------------------------------------------------------------------------
'''
# ===============================================================================================

# Public functions


def expose(name_or_function=None):
    # Deal with '@eel.expose()' - treat as '@eel.expose'
    if name_or_function is None:
        return expose

    if isinstance(name_or_function, str):   # Called as '@eel.expose("my_name")'
        name = name_or_function

        def decorator(function):
            _expose(name, function)
            return function
        return decorator
    else:
        function = name_or_function
        _expose(function.__name__, function)
        return function


def init(path, allowed_extensions=('.js', '.html', '.txt', '.htm', '.xhtml', '.vue')):
    global root_path, _js_functions
    root_path = _get_real_path(path)

    js_functions = set()
    for root, _, files in os.walk(root_path):
        for name in files:
            if not any(name.endswith(ext) for ext in allowed_extensions):
                continue

            try:
                with open(os.path.join(root, name), encoding='utf-8') as file:
                    contents = file.read()
                    expose_calls = set()
                    finder = re.findall(r'eel\.expose\(([^\)]+)\)', contents)
                    for expose_call in finder:
                        # If name specified in 2nd argument, strip quotes and store as function name
                        if ',' in expose_call:
                            expose_call = re.sub(r'["\']', '', expose_call.split(',')[1])
                        expose_call = expose_call.strip()
                        # Verify that function name is valid
                        msg = "eel.expose() call contains '(' or '='"
                        assert re.findall(r'[\(=]', expose_call) == [], msg
                        expose_calls.add(expose_call)
                    js_functions.update(expose_calls)
            except UnicodeDecodeError:
                pass    # Malformed file probably

    _js_functions = list(js_functions)
    for js_function in _js_functions:
        _mock_js_function(js_function)


async def start(*start_urls, **kwargs):
    try:
        _start_args.update(kwargs)

        if 'options' in kwargs:
            if _start_args['suppress_error']:
                _start_args.update(kwargs['options'])
            else:
                raise RuntimeError(api_error_message)

        if _start_args['port'] == 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', 0))
            _start_args['port'] = sock.getsockname()[1]
            sock.close()

        if _start_args['jinja_templates'] is not None:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            templates_path = os.path.join(root_path, _start_args['jinja_templates'])
            _start_args['jinja_env'] = Environment(loader=FileSystemLoader(templates_path),
                                                   autoescape=select_autoescape(['html', 'xml']))

        # Launch the browser to the starting URLs
        show(*start_urls)

        if _start_args['all_interfaces'] is True:
            HOST = '0.0.0.0'
        else:
            HOST = _start_args['host']
        # start web server (non blocking)
        app = web.Application()
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=HOST, port=_start_args['port'])
        await site.start()
        log.info(f"start http server {HOST}:{_start_args['port']}")
    except Exception:
        log.debug("http server exception", exc_info=True)


def show(*start_urls):
    browsers.open(start_urls, _start_args)


def spawn(function, *args, **kwargs):
    if asyncio.iscoroutinefunction(function):
        asyncio.ensure_future(function(*args, **kwargs))
    else:
        if 0 < len(kwargs):
            raise Exception('cannot convey kwargs')
        loop.call_soon_threadsafe(function, *args)

# Bottle Routes


@routes.get('/eel.js')
async def _eel(request: BaseRequest):
    start_geometry = {'default': {'size': _start_args['size'],
                                  'position': _start_args['position']},
                      'pages':   _start_args['geometry']}

    page = _eel_js.replace('/** _py_functions **/',
                           '_py_functions: %s,' % list(_exposed_functions.keys()))
    page = page.replace('/** _start_geometry **/',
                        '_start_geometry: %s,' % _safe_json(start_geometry))

    response = web.Response(text=page, content_type='application/javascript')
    _set_response_headers(response)
    return response


@routes.get('/eel')
async def _websocket(request: BaseRequest):

    ws = await websocket_protocol_check(request)

    for js_function in _js_functions:
        _import_js_function(js_function)

    page = request.query.get('page')
    if page not in _mock_queue_done:
        for call in _mock_queue:
            await _repeated_send(ws, _safe_json(call))
        _mock_queue_done.add(page)

    _websockets.append((page, ws))

    while True:
        try:
            message = await ws.receive_json(timeout=0.1)
            await _process_message(message, ws)
        except (asyncio.TimeoutError, TypeError):
            if ws.closed:
                break
        except Exception:
            log.debug("WebSocket exception", exc_info=True)
            break
    # closed
    if not ws.closed:
        await ws.close()
    _websockets.remove((page, ws))
    _websocket_close(page)


@routes.get('/{path:.*}')
async def _static(request: BaseRequest):
    response = None
    try:
        path = request.path[1:]
        if 'jinja_env' in _start_args and 'jinja_templates' in _start_args:
            template_prefix = _start_args['jinja_templates'] + '/'
            if path.startswith(template_prefix):
                n = len(template_prefix)
                template = _start_args['jinja_env'].get_template(path[n:])
                response = web.Response(body=template.render(), content_type='text/html')
        else:
            file_path = os.path.join(root_path, path)
            if not os.path.isfile(file_path):
                return web.Response(text=f"not found {path}", status=404)
            log.debug(f"static access to '{path}'")
            response = web.FileResponse(path=file_path)
    except Exception as e:
        log.debug("http page exception", exc_info=True)
        response = web.Response(text=str(e), status=500)

    _set_response_headers(response)
    return response


# Private functions


def _safe_json(obj):
    return json.dumps(obj, default=lambda o: None)


async def _repeated_send(ws: WebSocketResponse, msg):
    for attempt in range(100):
        try:
            await ws.send_str(msg)
            break
        except Exception:
            await asyncio.sleep(0.001)


async def _process_message(message, ws: WebSocketResponse):
    if 'call' in message:
        function = _exposed_functions[message['name']]
        if asyncio.iscoroutinefunction(function):
            return_val = await function(*message['args'])
        else:
            return_val = function(*message['args'])
        await _repeated_send(ws, _safe_json({
            'return': message['call'],
            'value': return_val,
        }))
    elif 'return' in message:
        call_id = message['return']
        if call_id in _call_return_futures:
            future = _call_return_futures[call_id]
            if not future.done():
                future.set_result(message['value'])
    else:
        log.warning('Invalid message received: ', message)


def _get_real_path(path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, path)
    else:
        return os.path.abspath(path)


def _mock_js_function(f):
    """add globals awaitable function"""
    assert isinstance(f, str)
    globals()[f] = lambda *args: _mock_call(f, args)
    # exec('%s = lambda *args: _mock_call("%s", args)' % (f, f), globals())


def _import_js_function(f):
    """add globals awaitable function"""
    assert isinstance(f, str)
    globals()[f] = lambda *args: _js_call(f, args)
    # exec('%s = lambda *args: _js_call("%s", args)' % (f, f), globals())


def _call_object(name, args):
    global _call_number
    _call_number += 1
    call_id = _call_number + random()
    return {'call': call_id, 'name': name, 'args': args}


def _mock_call(name, args):
    call_object = _call_object(name, args)
    _mock_queue.append(call_object)
    return _call_return(call_object['call'])


def _js_call(name, args):
    call_object = _call_object(name, args)
    data = _safe_json(call_object)
    for _, ws in _websockets:
        asyncio.ensure_future(_repeated_send(ws, data))
    return _call_return(call_object['call'])


def _call_return(call_id):
    future = asyncio.Future()
    _call_return_futures[call_id] = future

    async def wait_for_result(callback):
        """wait for result and exc callback"""
        try:
            await asyncio.wait_for(future, timeout=10.0)
            args = future.result()
            if asyncio.iscoroutinefunction(callback):
                await callback(args)
            else:
                callback(args)
        except asyncio.TimeoutError:
            log.debug("timeout on wait_for_result")
        except Exception:
            log.debug("_call_return exception", exc_info=True)

    async def return_func(callback=None):
        """return data or task object"""
        try:
            if callback is None:
                await asyncio.wait_for(future, timeout=10.0)
                return future.result()
            else:
                return asyncio.ensure_future(wait_for_result(callback))
        except asyncio.TimeoutError:
            log.debug("timeout on return_func")
        except Exception:
            log.debug("return_func exception", exc_info=True)
    return return_func


def _expose(name, function):
    msg = 'Already exposed function with name "%s"' % name
    assert name not in _exposed_functions, msg
    _exposed_functions[name] = function


def _websocket_close(page):
    close_callback: Optional[Callable] = _start_args.get('close_callback')

    if close_callback is not None:
        web_sockets = [ws for _, ws in _websockets]
        close_callback(page, web_sockets)
    else:
        # Default behaviour - wait 1s, then quit if all sockets are closed
        if _start_args['auto_close'] and len(_websockets) == 0:
            loop.call_later(1.0, loop.stop)


def _set_response_headers(response):
    if _start_args['disable_cache']:
        # https://stackoverflow.com/a/24748094/280852
        response.headers.add('Cache-Control', 'no-store')


__all__ = [
    "expose",
    "init",
    "start",
    "show",
    "spawn",
]
