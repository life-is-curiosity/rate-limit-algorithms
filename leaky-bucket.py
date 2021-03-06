import threading
import itertools
import queue
import uuid
import time

limit = 20  # Number of requests
duration = 60  # 60s
bucket = queue.Queue(limit)  # Thread-safe bucket queue


class ThreadSafeCounter:
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


counter = ThreadSafeCounter()  # Thread-safe counter


class LeakyBucket(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_lock = threading.Lock()
        self.generate_tokens()

    def generate_tokens(self):
        global bucket
        if bucket.full():
            # bucket is full, do nothing
            pass
        else:
            self.thread_lock.acquire()
            size = bucket.qsize()
            add_numbers_of_tokens = limit - size
            current_added = 0
            for n in range(0, add_numbers_of_tokens):
                bucket.put(uuid.uuid4())
                counter.increment()
                current_added += 1
            print("total {} token added ".format(counter.value()))
            self.thread_lock.release()

    def run(self):
        global bucket
        global duration
        while True:
            print("Fill token to bucket")
            self.generate_tokens()
            time.sleep(duration)


class TokenConsumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global bucket
        while True:
            if bucket.empty():
                pass
            else:
                token = bucket.get()
                print(
                    "get token {}, bucket size {}".format(
                        token, bucket.qsize()
                    ),
                    end="\n",
                )
            time.sleep(1)


leaky_bucket = LeakyBucket()
consumers = [TokenConsumer(), TokenConsumer(), TokenConsumer()]
leaky_bucket.start()
for consumer in consumers:
    consumer.start()
for consumer in consumers:
    consumer.join()
leaky_bucket.join()
