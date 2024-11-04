def func(b,**kargs):
    paramas={
        'w':b,
        
    }
    paramas.update(kargs)
    return paramas

print(func(1,a=2,v=3))