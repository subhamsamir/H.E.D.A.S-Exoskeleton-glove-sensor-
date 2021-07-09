import numpy as np
def poly_reg(coeff,val):
    return coeff[0] * pow(val,2) + coeff[1]*val + coeff[2]

def potToAngle(val):
    return val * 330 / 1023 + 345

def median_filter(xoldvalMedian,raw,size_filter):
    if len(xoldvalMedian)==size_filter:
        xoldvalMedian.pop(0)
    xoldvalMedian.append(raw)
    filteredMedian = np.median(xoldvalMedian)
    return filteredMedian
