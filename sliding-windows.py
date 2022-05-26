from http.server import HTTPServer, BaseHTTPRequestHandler
import _thread
import json
import time
import itertools
import threading


host = ('localhost', 8888)  # HTTP Server Configuration
request_limit_slider = []  # Rate limit Slider
limit = (1, 10)  # 10 requests per 1 second
precision = 5  # Windows precision
window_size = 0  # Current windows size


class AtomicCounter(object):
    def __init__(self):
        self._number_of_read = 0
        self._counter = itertools.count()
        self._read_lock = threading.Lock()

    def increment(self):
        next(self._counter)

    def value(self):
        with self._read_lock:
            value = next(self._counter) - self._number_of_read
            self._number_of_read += 1
        return value


counter = AtomicCounter()


def init_windows():
    print("Initializing the rate limit windows ...")
    global limit
    global precision
    global request_limit_slider
    global window_size
    rate_limit = limit[0] * limit[1]
    window_size = int(rate_limit / precision)
    for i in range(0, precision):
        request_limit_slider.append(window_size)
    print('initialized windows {} by {}'.format(
        request_limit_slider, window_size))


def exceeded_rate_limit():
    mutex = threading.Lock()
    mutex.acquire()
    result = False
    try:
        global request_limit_slider
        if len(request_limit_slider) == 0:
            init_windows()
        slot_size = request_limit_slider[0]
        slot_size -= 1
        if slot_size < 0:
            result = True
        else:
            result = False
        request_limit_slider[0] = slot_size
    finally:
        mutex.release()
    return result


class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter
        resp = None
        counter.increment()
        check_pass = exceeded_rate_limit()
        if check_pass == False:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            resp = {'result': 'Success'}
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            resp = {'error': 'Rate limit exceeded'}
        print("Total request counter -> {}", counter.value())
        self.wfile.write(json.dumps(resp).encode())


def http_server():
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()


def slide(request_limit_slider):
    if len(request_limit_slider) > 0:
        request_limit_slider.pop(0)
        request_limit_slider.append(window_size)


def sliding_windows():
    while True:
        mutex = threading.Lock()
        mutex.acquire()
        try:
            global request_limit_slider
            slide(request_limit_slider)
        finally:
            mutex.release()
            time.sleep(float(limit[0] / precision))


def processor():
    try:
        _thread.start_new_thread(http_server, ())
        _thread.start_new_thread(sliding_windows, ())
    except Exception as e:
        print(e)
    while 1:
        pass

# General test cases
def test_cases():
    init_windows()
    assert exceeded_rate_limit() == False
    assert exceeded_rate_limit() == False
    assert exceeded_rate_limit() == True
    assert exceeded_rate_limit() == True
    slide(request_limit_slider)
    assert exceeded_rate_limit() == False
    assert exceeded_rate_limit() == False
    assert exceeded_rate_limit() == True
    print("all test cases passed")


if __name__ == '__main__':
    test_cases()
    processor()
