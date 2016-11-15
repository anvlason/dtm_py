import os
NUM_CPUS = None  # defaults to all available

def worker(proc,name,step,h):
    command = "%s %s %f %f"%(proc,name,step,h)
#    print "%s\n"%command
    #os.system("E:\\REMAP\\tst_parallel\rs_model.py %s 64 %d"%name,h)
    if(os.system(command)!=0):
        exit(1)

def test_run(pool,name,hh):
    for h in hh:
        pool.apply_async(worker, args=(name, h))


if __name__ == "__main__":
     
     import multiprocessing as mp
     pool = mp.Pool(NUM_CPUS)
     test_run(pool,proc,name,step,heights)
     pool.close()
     pool.join()
