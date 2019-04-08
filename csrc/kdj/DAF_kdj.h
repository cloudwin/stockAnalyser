#ifndef kdj_H
#define kdj_H

#include "DAF.h"

#define DAF_NAME_kdj "kdj"
class DAF_kdj : public DAF
{
public:
    DAF_kdj(int stockMarket)
    {
        strcpy(_name, DAF_NAME_kdj);
        _marketMask = stockMarket;
    }

    void init();
    bool buyChecker(char* date, int index, dayTradeList* tradeList);
    bool sellChecker(char* date, int index, dayTradeList* tradeList);
};

DAF_item getkdj();
#endif
