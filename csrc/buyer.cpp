/********************************************************************
 * buyer.cpp: define interface for python script                    *
 *                                            2018 Hui              *
 ********************************************************************/

#include "register.g"

static void* instance = NULL;                          //only one instance can be created

extern "C"
{

// Create DAF instance
// sm:    stock market mask, bit 0 for shenzhen, bit 1 for chuangye, bit 2 for shanghai
// score: whether check score
bool createDAF(char* name, int sm, int score)
{
    int i = 0;
    for(; (i < DAF_MAX_NUM) && (_DAFList[i].name); i++)
    {
        if ((_DAFList[i].name) && (strcmp(_DAFList[i].name, name) == 0))
        {
            return (instance = _DAFList[i].getInstance(sm));
        }
    }
    return false;
}

// Decide whether we should buy stock on date
// date:   date
// return: stock index
int buy(char* date)
{
    if (!instance)
        return 0;
    return ((class DAF*)instance)->buy(date);
}

// Whether the stock should be sold
// date:   date
// return: sell date  
char* sell(char* date)
{
    if (!instance)
        return NULL;
    return ((class DAF*)instance)->sell(date);
}

// Output log into log file
// appendStr: some additional information needed to add to the file name
void logfile(char* appendStr)
{
    if (!instance)
        return;
    ((class DAF*)instance)->logfile(appendStr);
}

// Check profit
// return: new total money
long profit(long totalMoney)
{
    if (!instance)
        return totalMoney;
    return ((class DAF*)instance)->profit(totalMoney);
}

}
