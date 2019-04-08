#ifndef __xxxxxx___H
#define __xxxxxx___H

#include "DAF.h"

#define DAF_NAME___xxxxxx__ "__xxxxxx__"
class DAF___xxxxxx__ : public DAF
{
public:
    DAF___xxxxxx__(int stockMarket)
    {
        strcpy(_name, DAF_NAME___xxxxxx__);
        _marketMask = stockMarket;
    }

    void init();
    bool buyChecker(char* date, int index, dayTradeList* tradeList);
    bool sellChecker(char* date, int index, dayTradeList* tradeList);
};

DAF_item get__xxxxxx__();
#endif
