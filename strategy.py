import numpy as np
import talib
import datetime

timeperiod = 50
rr = 1.5
atr_multiplier = 1.5

def two_to_one_engulf_long(ohlcvs, ohlcv_data):
    r = 0

    num_stops = 0
    num_take_profits = 0
    num_positions = 0

    highs = np.array([element[2] for element in ohlcv_data])
    lows = np.array([element[3] for element in ohlcv_data])
    closes = np.array([element[4] for element in ohlcv_data])
    ema = talib.EMA(closes, timeperiod=timeperiod)
    atr = talib.ATR(highs, lows, closes)

    for index in range(2, len(ohlcvs)):
        first_candle = ohlcvs[index - 2]
        second_candle = ohlcvs[index - 1]
        engulf_candle = ohlcvs[index]

        if first_candle.close_price < first_candle.open_price and \
                second_candle.close_price < second_candle.open_price and \
                engulf_candle.close_price > second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < atr[index] * atr_multiplier and \
                ema[index] < engulf_candle.close_price:
            num_positions += 1

            open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

            position_price = engulf_candle.close_price
            whichever_is_lowest = second_candle.lowest if second_candle.highest < engulf_candle.highest else engulf_candle.lowest
            stop_loss = whichever_is_lowest
            take_profit = position_price + (position_price - stop_loss) * rr
            print(f'\n[LONG][{open_time}] Opened at: {position_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {ema[index]} ATR: {atr[index]}')

            for runner_index in range(index + 1, len(ohlcvs)):
                candle = ohlcvs[runner_index]

                if candle.highest >= take_profit:
                    close_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                    print(f'[{close_time}] Take profit')
                    r += rr
                    num_take_profits += 1
                    break

                if candle.lowest <= stop_loss:
                    close_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                    print(f'[{close_time}] Stop loss')
                    r -= 1
                    num_stops += 1
                    break

    return r, num_stops, num_take_profits, num_positions


def two_to_one_engulf_short(ohlcvs, ohlcv_data):
    r = 0
    num_stops = 0
    num_take_profits = 0
    num_positions = 0

    highs = np.array([element[2] for element in ohlcv_data])
    lows = np.array([element[3] for element in ohlcv_data])
    closes = np.array([element[4] for element in ohlcv_data])

    ema = talib.EMA(closes, timeperiod=timeperiod)
    atr = talib.ATR(highs, lows, closes)

    for index in range(2, len(ohlcvs)):
        first_candle = ohlcvs[index - 2]
        second_candle = ohlcvs[index - 1]
        engulf_candle = ohlcvs[index]

        if first_candle.close_price > first_candle.open_price and \
                second_candle.close_price > second_candle.open_price and \
                engulf_candle.close_price < second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < atr[index] * atr_multiplier and \
                ema[index] > engulf_candle.close_price:
            num_positions += 1
            open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

            position_price = engulf_candle.close_price
            whichever_is_highest = second_candle.highest if second_candle.highest > engulf_candle.highest else engulf_candle.highest
            stop_loss = whichever_is_highest
            take_profit = position_price - (stop_loss - position_price) * rr
            print(f'\n[SHORT][{open_time}] Opened at: {position_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {ema[index]} ATR: {atr[index]}')

            for runner_index in range(index + 1, len(ohlcvs)):
                candle = ohlcvs[runner_index]

                if candle.lowest <= take_profit:
                    close_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                    print(f'[{close_time}] Take profit')
                    r += rr
                    num_take_profits += 1
                    break

                if candle.highest >= stop_loss:
                    close_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                    print(f'[{close_time}] Stop loss')
                    r -= 1
                    num_stops += 1
                    break

    return r, num_stops, num_take_profits, num_positions

def macd_strategy_long(ohlcvs, ohlcv_data):
    r_history = []
    ohlcvs_np = np.array([element[4] for element in ohlcv_data])
    ema = talib.EMA(ohlcvs_np, timeperiod=timeperiod)
    macd, macd_signal, _ = talib.MACD(ohlcvs_np)

    for index in range(2, len(ohlcvs)):
        if macd[index] < 0 and \
                macd[index] > macd_signal[index] and \
                ohlcvs[index].close_price > ema[index]:

            position_price = ohlcvs[index].close_price
            take_profit = position_price + (position_price - ema[index]) * rr
            stop_loss = ema[index]

            print(
                f'\nOpened at: {position_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}')

            for runner_index in range(index + 1, len(ohlcvs)):
                candle = ohlcvs[runner_index]

                if candle.close_price >= take_profit:
                    print(f'Take profit. Closed at: {candle.close_price}\n')
                    r_history.append(1.5)
                    break

                if candle.close_price < stop_loss:
                    print(f'Stop loss. Closed at: {candle.close_price}\n')
                    r_history.append(-1)
                    break

    print(np.cumsum(np.array(r_history)))
    print(f'Total R: {sum(r_history)}')


def macd_strategy_short(ohlcvs, ohlcv_data):
    r_history = []
    ohlcvs_np = np.array([element[4] for element in ohlcv_data])
    ema = talib.EMA(ohlcvs_np, timeperiod=timeperiod)
    macd, macd_signal, _ = talib.MACD(ohlcvs_np)

    for index in range(2, len(ohlcvs)):

        if macd[index] > 0 and \
                macd[index] < macd_signal[index] and \
                ohlcvs[index].close_price < ema[index]:

            position_price = ohlcvs[index].close_price
            take_profit = position_price - (ema[index] - position_price) * rr
            stop_loss = ema[index]

            print(
                f'\nOpened at: {position_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}')

            in_trade = True

            for runner_index in range(index + 1, len(ohlcvs)):
                candle = ohlcvs[runner_index]

                if candle.close_price <= take_profit:
                    print(f'Take profit. Closed at: {candle.close_price}\n')
                    r_history.append(1.5)
                    break

                if candle.close_price > stop_loss:
                    print(f'Stop loss. Closed at: {candle.close_price}\n')
                    r_history.append(-1)
                    break

    print(np.cumsum(np.array(r_history)))
    print(f'Total R: {sum(r_history)}')
