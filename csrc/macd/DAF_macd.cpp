#include "DAF_macd.h"

//---------------------------------------------------------
static void* createInstance(int stockMarket)
{
    return (void*)(new DAF_macd(stockMarket));
}

DAF_item getmacd()
{
    DAF_item item = {DAF_NAME_macd, createInstance};
    return item;
}
//----------------------------------------------------------

void DAF_macd::init()
{
    //add your code here
    _indicator = INDICATOR_MACD;
}

bool DAF_macd::buyChecker(char* date, int index, dayTradeList* tradeList)
{
    //add your code here
    float macd[2] = {0};
    float dif[2] = {0};
    float dea[2] = {0};
    if (getMacdValueByBuf(index, date, macd, dif, dea))
    {
        if ((macd[0] < 0.0) && (macd[1] >= 0.0))
        {
            FIX_CONDITION((*tradeList));
            //if (tradeList->next.open / tradeList->trade.close < 0.905)
            //    return false;
            _score[index] = macd[1] - macd[0];
            return true;
        }
    }

    return false;
}

bool DAF_macd::sellChecker(char* date, int index, dayTradeList* tradeList)
{
    //add your code here    
    float macd[2] = {0};
    float dif[2] = {0};
    float dea[2] = {0};

    if (getMacdValueByBuf(index, date, macd, dif, dea))
    {
        if ((dif[1] < dif[0]) && 
            ((tradeList->trade.close >= _buy.trade.open) || (tradeList->trade.close / _buy.trade.open < 0.85)))
        {
            SELL_FIX_CONDITION((*tradeList));
            return true;
        }
    }

    return false;
}


