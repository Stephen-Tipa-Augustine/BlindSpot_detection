import queue
import threading


class ThreadManager:

    def __init__(self):
        self.thread_list = list()
        self.que = queue.Queue()

    def add_thread(self, t):
        self.thread_list.append(t)

    def join_threads(self):
        for t in self.thread_list:
            t.join()

    def check_for_return_value(self):
        while not self.que.empty():
            return self.que.get()


def foo(bar):
    print('hello {0}'.format(bar))
    return bar


if __name__ == '__main__':
    obj = ThreadManager()
    t1 = threading.Thread(target=lambda q, arg1: q.put(foo(arg1)), args=(obj.que, 'Stephen'))
    t2 = threading.Thread(target=lambda q, arg1: q.put(foo(arg1)), args=(obj.que, 'Tipa'))
    t3 = threading.Thread(target=lambda q, arg1: q.put(foo(arg1)), args=(obj.que, 'Augustine'))
    t1.start()
    t2.start()
    t3.start()
    obj.add_thread(t1)
    obj.add_thread(t2)
    obj.add_thread(t3)
    obj.join_threads()

    # while True:
    print('returned value is: ', obj.check_for_return_value())
    print('returned value is: ', obj.check_for_return_value())
    print('returned value is: ', obj.check_for_return_value())
