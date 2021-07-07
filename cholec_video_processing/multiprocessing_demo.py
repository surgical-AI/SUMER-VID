'''
The goal is to understand how to do multiprocessing:
starting point:https://www.youtube.com/watch?v=ecKWiaHCEKs
- read a few files
- process the files
- write some output files
'''
import os

import numpy as np
from multiprocessing import Process

filenames = []
def write_dummy(n=5000):
    for i in range(n):
        name = 'text_{}'.format(i)
        with open(name, 'w') as f:
            f.write(str(list(np.random.rand(10))))
        filenames.append(name)

def read_process_write(fnames):
    for name in fnames:
        with open(name) as fh:
            nums = eval(fh.read())
            processed = process(nums)
        outname = name + '_{}'.format('out')
        with open(outname, 'w') as fh:
            fh.write(str(processed))
    return


def process(nums):
    return [i*10 for i in nums]


def doall(fnames):
    read_process_write(fnames)


if __name__ == '__main__':
    write_dummy(n=10000)
    # doall(filenames)
    import os
    processes = []
    chunk = int(len(filenames)/os.cpu_count())
    endofarray=False
    for i in range(os.cpu_count()):
        if endofarray:
            continue
        if len(filenames) - (i+1)*chunk <= chunk:
            end = len(filenames)
            endofarray=True
        else:
            end = (i+1) * chunk

        print(i*chunk, end)
        subnames = filenames[i*chunk: end]
        processes.append(Process(target=doall, args=(subnames,)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()
