import numpy as np
a_list = [1,2,4]
if any(elem in a_list for elem in [4, 5, 6, 7]):
    print("haha")
else:
    print("No")