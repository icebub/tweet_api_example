def isLeafYear(year=2000):    
    if type(year) != int :  
        return False
    
    if year%400 == 0 :
        return True
    
    if year%100 == 0 :
        return False
    
    if year%4 == 0 :
        return True
    
    return False
    
if __name__ == '__main__':
    testSet = [1600,2000,1500,2004,2008,2010,2011,2012,2020]
    for year in testSet :
        print (year,"->",isLeafYear(year))