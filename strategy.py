import numpy as np
import talib

timeperiod = 50

def two_to_one_engulf_long(ohlcvs, ohlcv_data):
    r = 0
    ohlcvs_np = np.array([element[3] for element in ohlcv_data])
    ema = talib.EMA(ohlcvs_np, timeperiod=timeperiod)

    for index in range(2, len(ohlcvs)):
        first_candle = ohlcvs[index - 2]
        second_candle = ohlcvs[index - 1]
        engulf_candle = ohlcvs[index]

        if first_candle.close_price < first_candle.open_price and \
            second_candle.close_price < second_candle.open_price and \
            engulf_candle.close_price > second_candle.open_price and \
            ema[index] < engulf_candle.close_price:

            for runner_index in range(index, len(ohlcvs)):
                    candle = ohlcvs[runner_index]

                    if candle.highest >= (engulf_candle.close_price + (engulf_candle.close_price - second_candle.lowest) * 2):
                        print("Take profit")
                        r += 2
                        break 

                    if candle.lowest <= second_candle.lowest:
                        print("Stop loss")
                        r -= 1
                        break
    
    print(f'Total R: {r}')

def two_to_one_engulf_short(ohlcvs, ohlcv_data):
    r = 0
    ohlcvs_np = np.array([element[3] for element in ohlcv_data])
    ema = talib.EMA(ohlcvs_np, timeperiod=timeperiod)

    for index in range(2, len(ohlcvs)):
        first_candle = ohlcvs[index - 2]
        second_candle = ohlcvs[index - 1]
        engulf_candle = ohlcvs[index]

        if first_candle.close_price > first_candle.open_price and \
            second_candle.close_price > second_candle.open_price and \
            engulf_candle.close_price < second_candle.open_price and \
            ema[index] > engulf_candle.close_price:
           
           print(engulf_candle)

           for runner_index in range(index, len(ohlcvs)):
                    candle = ohlcvs[runner_index]

                    if candle.lowest <= (engulf_candle.close_price - ((second_candle.highest - engulf_candle.close_price) * 2)):
                        print("Take profit")
                        r += 2
                        break 

                    if candle.highest >= second_candle.highest:
                        print("Stop loss")
                        r -= 1
                        break

    print(f'Total R: {r}')        

def macd_strategy_long(ohlcvs, ohlcv_data):
    r = 0
    ohlcvs_np = np.array([element[3] for element in ohlcv_data])
    ema = talib.EMA(ohlcvs_np, timeperiod=timeperiod)
    macd, macd_signal, _ = talib.MACD(ohlcvs_np)

    in_trade = False

    for index in range(2, len(ohlcvs)):

        if macd[index] < 0 and \
            not in_trade and \
            macd[index] > macd_signal[index] and \
            ohlcvs[index].close_price > ema[index]:

            position_price = ohlcvs[index].close_price
            take_profit = position_price + (position_price - ema[index]) * 1.5
            stop_loss = ema[index]

            print(f'\nOpened at: {position_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}')

            in_trade = True

            for runner_index in range(index + 1, len(ohlcvs)):
                    candle = ohlcvs[runner_index]

                    if candle.close_price >= take_profit:
                        print(f'Take profit. Closed at: {candle.close_price}\n')
                        r += 2
                        in_trade = False
                        break 

                    if candle.close_price < stop_loss:
                        print(f'Stop loss. Closed at: {candle.close_price}\n')
                        r -= 1
                        in_trade = False
                        break
    
    print(f'Total R: {r}')

def macd_strategy_short(ohlcvs, ohlcv_data):
    r = 0
    ohlcvs_np = np.array([element[3] for element in ohlcv_data])
    ema = talib.EMA(ohlcvs_np, timeperiod=timeperiod)
    macd, macd_signal, _ = talib.MACD(ohlcvs_np)

    in_trade = False

    for index in range(2, len(ohlcvs)):

        if macd[index] > 0 and \
            not in_trade and \
            macd[index] < macd_signal[index] and \
            ohlcvs[index].close_price < ema[index]:

            position_price = ohlcvs[index].close_price
            take_profit = position_price - (ema[index] - position_price) * 1.5
            stop_loss = ema[index]

            print(f'\nOpened at: {position_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}')

            in_trade = True

            for runner_index in range(index + 1, len(ohlcvs)):
                    candle = ohlcvs[runner_index]

                    if candle.close_price <= take_profit:
                        print(f'Take profit. Closed at: {candle.close_price}\n')
                        r += 2
                        in_trade = False
                        break 

                    if candle.close_price > stop_loss:
                        print(f'Stop loss. Closed at: {candle.close_price}\n')
                        r -= 1
                        in_trade = False
                        break
    
    print(f'Total R: {r}')