from weathercomAPI import *

if __name__ == "__main__":
    ### *** TEST 1 ***
    # Markoupoulo, Attica
    url = 'https://weather.com/weather/hourbyhour/l/21e963c34293ccc9c399128b3c25d32afd754dec039c0376a7c974185584f29d#detailIndex4'
    
    weathercomGetTuple(url)
