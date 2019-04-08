#include "DAF_kdj.h"

//---------------------------------------------------------
static void* createInstance(int stockMarket)
{
    return (void*)(new DAF_kdj(stockMarket));
}

DAF_item getkdj()
{
    DAF_item item = {DAF_NAME_kdj, createInstance};
    return item;
}
//----------------------------------------------------------

void DAF_kdj::init()
{
    //add your code here
    _indicator = INDICATOR_KDJ;
}

bool DAF_kdj::buyChecker(char* date, int index, dayTradeList* tradeList)
{
    //add your code here
#define KDJ_NUM 3
    float K[KDJ_NUM] = {0};
    float D[KDJ_NUM] = {0};
    float J[KDJ_NUM] = {0};
    int i;
    if (getKDJValueByBuf(index, date, K, D, J, KDJ_NUM))
    {
        for(i = 0; i < KDJ_NUM - 1; i++)
        {
            if (J[i] < -2)
                break;
        }
        if (i != KDJ_NUM - 1)
        {
            if (J[KDJ_NUM - 1] > K[KDJ_NUM - 1] && J[KDJ_NUM - 1] > 0)
            {
                _score[index] = J[KDJ_NUM - 1] - K[KDJ_NUM - 1];
                return true;
            }
        }
    }
    return false;
}

bool DAF_kdj::sellChecker(char* date, int index, dayTradeList* tradeList)
{
    //add your code here
    float K[KDJ_NUM] = {0};
    float D[KDJ_NUM] = {0};
    float J[KDJ_NUM] = {0};
    if (getKDJValueByBuf(index, date, K, D, J, KDJ_NUM))
    {
        if ((J[KDJ_NUM - 1] < K[KDJ_NUM - 1]) &&
            ((tradeList->trade.close >= _buy.trade.open) || (tradeList->trade.close / _buy.trade.open < 0.85)))
            return true;
    }
    return false;
}


