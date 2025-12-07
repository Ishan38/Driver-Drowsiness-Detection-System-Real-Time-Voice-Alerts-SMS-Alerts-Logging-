from scipy.spatial import distance as dist

def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[10])  
    B = dist.euclidean(mouth[4], mouth[8])  

    C = dist.euclidean(mouth[0], mouth[6]) 

    mar = (A + B) / (2.0 * C)

    return mar
