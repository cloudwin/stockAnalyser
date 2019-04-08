#ifndef macd_H
#define macd_H

#include "DAF.h"

#define DAF_NAME_macd "macd"
class DAF_macd : public DAF
{
public:
    DAF_macd(int stockMarket)
    {
        strcpy(_name, DAF_NAME_macd);
        _marketMask = stockMarket;
    }

    void init();
    bool buyChecker(char* date, int index, dayTradeList* tradeList);
    bool sellChecker(char* date, int index, dayTradeList* tradeList);
};

DAF_item getmacd();
#endif
