from multiprocessing import Process, Value, Array


def writer(num, arr):
    num.value = 10
    for i in range(len(arr)):
        arr[i] = i


def reader(num, arr):
    print(f"Number: {num.value}")
    print(f"Array: {arr[:]}")


if __name__ == "__main__":
    num = Value('d', 0.0)
    arr = Array('i', range(5))

    p1 = Process(target=writer, args=(num, arr))
    p2 = Process(target=reader, args=(num, arr))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
