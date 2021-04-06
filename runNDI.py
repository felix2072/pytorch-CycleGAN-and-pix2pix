import time


def print_fps(_frame_counter, _start_time, _seconds_to_wait):
    _frame_counter += 1
    if (time.time() - _start_time) > _seconds_to_wait:
        print("Average FPS: ", _frame_counter / (time.time() - _start_time))
        _frame_counter = 0
        _start_time = time.time()
    return _frame_counter, _start_time


start_time = time.time()
seconds_to_wait = 1
frame_counter = 0

while True:
    time.sleep(.01)
    counter_and_time = print_fps(frame_counter, start_time, seconds_to_wait)
    frame_counter = counter_and_time[0]
    start_time = counter_and_time[1]