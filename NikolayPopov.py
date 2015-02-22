# -*- coding: utf-8 -*-

from csv import reader, writer, Error as CsvError
from sys import exit, argv

Sell_L, Buy_L = [], []  # lists of tuples (num, volume, price)
Sell_M, Buy_M = [], []  # list of tuples (num, volume)
deals_list = []


def read_csv(file_name, delimiter=';'):
    """
    fills global variables
    :param file_name:   path to file
    :param delimiter:   csv delimiter
    :return:            None
    """
    global Sell_M, Sell_L, Buy_M, Buy_L
    try:
        file = open(file_name)
    except FileNotFoundError:
        file = "File Not Found"
        exit(file)

    read = reader(file, delimiter=delimiter)

    add_sell_l, add_sell_m, add_buy_m, add_buy_l = Sell_L.append, Sell_M.append, Buy_M.append, Buy_L.append

    try:
        for row in read:
            try:
                if row[1] == 'S':
                    if row[2] == 'L':
                        add_sell_l((int(row[0]), int(row[3]), int(row[4])))
                    elif row[2] == 'M':
                        add_sell_m((int(row[0]), int(row[3])))
                if row[1] == 'B':
                    if row[2] == 'L':
                        add_buy_l((int(row[0]), int(row[3]), int(row[4])))
                    elif row[2] == 'M':
                        add_buy_m((int(row[0]), int(row[3])))
            except ValueError:
                continue
            except IndexError:
                continue
    except CsvError as e:
        exit('file {}, line {}: {}'.format(file_name, read.line_num, e))
    finally:
        file.close()


def make_deal(buy, sell):
    """
    find optimal price, make deals and fill in global var deals_list
    :param buy: sorted list of buy bids
    :param sell: sorted list of sell bids
    :return: cost, optimal price
    """
    global deals_list

    add_deal = deals_list.append

    index_start_limit_sell, index_start_limit_buy = len(Sell_M) - 1, len(Buy_M) - 1

    len_sell, len_buy = len(sell), len(buy)

    maximum = (0, 0, 0)

    index_buy, index_sell, volume = 0, 0, 0

    current_sell_volume, current_buy_volume = sell[index_sell][1], buy[index_buy][1]

    market_price = Buy_L[0][2]

    while len_sell > index_sell and len_buy > index_buy:

        if (index_sell > index_start_limit_sell) and \
                (sell[index_sell][2] > market_price or (index_buy > index_start_limit_buy and buy[index_buy][2] < sell[index_sell][2])):
            break
        elif index_buy > index_start_limit_buy and buy[index_buy][2] < market_price:
            market_price = buy[index_buy][2]
            continue
        else:
            deal_volume = min(current_buy_volume, current_sell_volume)
            volume += deal_volume
            add_deal((buy[index_buy][0], sell[index_sell][0], deal_volume))
            if current_buy_volume < current_sell_volume:
                current_sell_volume -= current_buy_volume
                index_buy += 1
                if index_buy < len_buy:
                    current_buy_volume = buy[index_buy][1]
            elif current_buy_volume > current_sell_volume:
                current_buy_volume -= current_sell_volume
                index_sell += 1
                if index_sell < len_sell:
                    current_sell_volume = sell[index_sell][1]
            else:
                index_sell += 1
                index_buy += 1
                current_sell_volume, current_buy_volume = sell[index_sell][1], buy[index_buy][1]
        if volume*market_price > maximum[0]:
            maximum = (volume*market_price, market_price, len(deals_list))
    deals_list = deals_list[:maximum[2]]
    return maximum[0], maximum[1]


if __name__ == "__main__":

    # for command line call
    if len(argv) >= 2:
        filename = argv[1]
    else:
        filename = 'MoEx_exmpl_filled.csv'
    if len(argv) >= 3:
        output_file = argv[2]
    else:
        output_file = 'result.csv'
    if len(argv) >= 4:
        delim = argv[3]
    else:
        delim = ';'
    #########################################################

    read_csv(filename, delim)

    Sell_L.sort(key=lambda x: x[2])
    Buy_L.sort(key=lambda x: x[2], reverse=True)

    if len(Sell_L) == 0 or len(Buy_L) == 0 or (Sell_L[0][2] > Buy_L[0][2]):
        with open(output_file, 'w') as f:
            f.write('FAILED')
    else:
        cost, price = make_deal(Buy_M+Buy_L, Sell_M+Sell_L)
        with open(output_file, 'w') as f:
            write = writer(f, delimiter=delim)
            write.writerow(('OK', price, cost))
            write.writerows((i[0], i[1], i[2], i[2]*price) for i in deals_list)
