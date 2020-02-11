def printNumber(start=1,end=100):
    
    for i in range(start,end+1):
        multi_3 = i%3==0
        multi_5 = i%5==0
        
        output_text = ""
        if multi_3 :
            output_text += "Fizz"
        if multi_5 :
            output_text += "Buzz"
        if len(output_text) == 0 :
            output_text += str(i)
            
        print (output_text, end = ' ')
        
if __name__ == '__main__':
    printNumber()

