import  time

def time_performance(func):
    start_time = time.time()

    def wrap(self,request, *args, **kwargs):
        return func(self,request, *args, **kwargs)

    print("Time taken :", time.time() - start_time)
    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap



