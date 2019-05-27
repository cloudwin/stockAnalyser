/********************************************************************
 * DAF.cpp: define DAF                                              *
 *                                            2018 Hui              *
 ********************************************************************/

#include "DAF.h"
#include "time.h"

// 1 for shenzhen, binary 10 for chuangye, binary 100 for shanghai
// binary 111 means three markets
static void* createInstance(int stockMarket)
{
    return (void*)(new DAF(stockMarket));
}

DAF_item getBasic()
{
    DAF_item item = {DAF_NAME_BASIC, createInstance};
    return item;
}

static long _getTime(char* date)
{
    struct tm stm;
    char strTime[64];
    strcpy(strTime, date);
    //strcat(strTime, " 0:0:0");
    //strptime(strTime, "%Y-%m-%d %H:%M:%S",&stm);
    //long t = mktime(&stm);
    int year, month, day;
    sscanf(date, "%d-%d-%d", &year, &month, &day);
    long t = year * 372 + month * 31 + day;
    return t;
}

static int _readOneTradeByBuf(char* fp, int index, dayTrade* trade)
{
    char tmp[64];
    char* f = fp;
    trade->index = index;
    memcpy(trade->dateStr, fp, 10);
    trade->dateStr[10] = 0;
    trade->date = _getTime(trade->dateStr);
    f += 10;
    float tmp1, tmp2;
    sscanf(f, ",%f,%f,%f,%f,%f,%f", &(trade->open), &(trade->high),
            &(trade->close), &(trade->low), &tmp1, &tmp2);
    trade->volume = tmp1;
    trade->amount = tmp2;
    while(*f != '\n')
        f++;
    f++;
    return f - fp;
} 

static int _fileSize(char* filename)
{
    struct stat statbuf;
    stat(filename,&statbuf);
    return statbuf.st_size;
}   

static bool _readFile(char* fileName, infoBuffer* info)
{
    FILE* fp = fopen(fileName, "r");
    if (!fp)
        return false;
    info->length = _fileSize(fileName);
    info->content = (char*)malloc(info->length);
    fread(info->content, info->length, 1, fp);
    fclose(fp);
    return true;
}

void DAF::initIndicator(void)
{
    int i;
    char tmp[128];

    init();
    _init = true;
    _tradeInfo = (infoBuffer*)malloc(sizeof(infoBuffer) * ALL_STOCK_NUM);
    if (!_tradeInfo)
    {
        printf("Fatal error: memory out!\n");
        return;
    }
    memset(_tradeInfo, 0, sizeof(infoBuffer) * ALL_STOCK_NUM);

    for(i = 0; i < ALL_STOCK_NUM; i++)
    {
        sprintf(tmp, "%s%06d.csv", DATA_DIR, i);
        _readFile(tmp, _tradeInfo + i);
    }

    if (_indicator & INDICATOR_MACD)
    {
        _macdInfo = (infoBuffer*)malloc(sizeof(infoBuffer) * ALL_STOCK_NUM);
        if (!_macdInfo)
        {
            printf("Fatal error: memory out!\n");
            return;
        }
        memset(_macdInfo, 0, sizeof(infoBuffer) * ALL_STOCK_NUM);
        for(i = 0; i < ALL_STOCK_NUM; i++)
        {
            sprintf(tmp, "%sMACD/%06d.macd", INDICATOR_DIR, i);
            _readFile(tmp, _macdInfo + i); 
        }
    }

    if (_indicator & INDICATOR_KDJ)
    {
        _kdjInfo = (infoBuffer*)malloc(sizeof(infoBuffer) * ALL_STOCK_NUM);
        if (!_kdjInfo)
        {
            printf("Fatal error: memory out!\n");
            return;
        }
        memset(_kdjInfo, 0, sizeof(infoBuffer) * ALL_STOCK_NUM);
        for(i = 0; i < ALL_STOCK_NUM; i++)
        {
            sprintf(tmp, "%sKDJ/%06d.kdj", INDICATOR_DIR, i);
            _readFile(tmp, _kdjInfo + i); 
        }
    }

    if (_indicator & INDICATOR_BOLL)
    {
        _bollInfo = (infoBuffer*)malloc(sizeof(infoBuffer) * ALL_STOCK_NUM);
        if (!_bollInfo)
        {
            printf("Fatal error: memory out!\n");
            return;
        }
        memset(_bollInfo, 0, sizeof(infoBuffer) * ALL_STOCK_NUM);
        for(i = 0; i < ALL_STOCK_NUM; i++)
        {
            sprintf(tmp, "%sBOLL/%06d.boll", INDICATOR_DIR, i);
            _readFile(tmp, _bollInfo + i); 
        }
    }
}

dayTradeList DAF::getDayTradeByBuf(int index, char* date)
{
    dayTradeList retv = {0};
    char tmp[64];
    bool firstTime = false; 
    long t = _getTime(date);
    int offset = _tradeInfo[index].offset;
    char* fp = NULL;
    int ret = 0;
    if (_tradeInfo[index].content == NULL)
        return retv;
    fp = _tradeInfo[index].content;
    if (_tradeInfo[index].offset == 0)
    {
        fp += 39;
        firstTime = true;
    }
    else
    {
        fp += _tradeInfo[index].offset;
    }

    do
    {
        if ((!firstTime) && (retv.trade.open == 0))
        {
            if (!(ret = _readOneTradeByBuf(fp, index, &(retv.pre))))
                goto FAIL;
            fp += ret;
        }
        else
        {
            memcpy(&(retv.pre), &(retv.trade), sizeof(retv.trade));
        }
        _tradeInfo[index].offset = fp - _tradeInfo[index].content;

        if (!(ret = _readOneTradeByBuf(fp, index, &(retv.trade))))
            goto FAIL;
        fp += ret;
        if (retv.trade.date >= t)
            break;
    }
    while(fp - _tradeInfo[index].content < _tradeInfo[index].length);

    if (t == retv.trade.date)
    {
        if (!(ret = _readOneTradeByBuf(fp, index, &(retv.next))))
            goto FAIL;
        fp += ret;
    }
    else
    {
        // this day has no trade.
        _tradeInfo[index].offset = offset;
        goto FAIL;
    }
    return retv;
FAIL:
    memset(&retv, 0, sizeof(retv));
    return retv;
}

// the values are returned in macd
// macd[0] for last day's MACD value
// macd[1] for today's MACD value
// dif[] for DIF[last, today]
// dea[] for DEA[last, today]
bool DAF::getMacdValueByBuf(int index, char* date, float* macd, float* dif, float* dea)
{
    char tmp[64] = {0};
    char c;
    long t = _getTime(date);
    if (_macdInfo[index].content == NULL)
        return false;
    char* fp = _macdInfo[index].content;
    char* f = fp;
    macd[0] = 0.0;
    dif[0] = 0.0;
    dea[0] = 0.0;
    if (_macdInfo[index].offset == 0)
    {
        fp += 30;
    }
    else
    {
        fp += _macdInfo[index].offset;
    }
    float ema12, ema26;
    while(fp - _macdInfo[index].content < _macdInfo[index].length)
    {
        memset(tmp, 0, sizeof(tmp));
        int tmpOffset = fp - _macdInfo[index].content;
        memcpy(tmp, fp, 10);
        fp += 10;
        long tt = _getTime(tmp);
        if (tt == t)
        {
            sscanf(fp, ",%f,%f,%f,%f,%f\n", dif + 1, dea + 1, macd + 1, &ema12, &ema26);
            DEBUG_OUTPUT("get macd\n");
            return true;
        }
        else if (tt > t)
        {
            goto END;
        }
        _macdInfo[index].offset = tmpOffset;
        sscanf(fp, ",%f,%f,%f,%f,%f\n", dif, dea, macd, &ema12, &ema26);
        while(*fp != '\n')
            fp++;
        fp++;
    }
END:
    return false;
}

// get K,D,J values
// K[] for K[last, today]
// D[] for D[last, today]
// J[] for J[last, today]
// return the actual number of the obtained data
int DAF::getKDJValueByBuf(int index, char* date, float* K, float* D, float* J, int num)
{
    char tmp[64] = {0};
    char c;
    long t = _getTime(date);
    int tmpOffset[20];
        
    if (_kdjInfo[index].content == NULL)
        return 0;
    char* fp = _kdjInfo[index].content;
    K[0] = 0.0;
    D[0] = 0.0;
    J[0] = 0.0;
    if (_kdjInfo[index].offset == 0)
    {
        fp += 11;
    }
    else
    {
        fp += _kdjInfo[index].offset;
    }

    float *tk = K, *td = D, *tj = J;
    while( fp - _kdjInfo[index].content < _kdjInfo[index].length)
    {
        memset(tmp, 0, sizeof(tmp));
        tmpOffset[tk - K] = fp - _kdjInfo[index].content;
        memcpy(tmp, fp, 10);
        fp += 10;
        long tt = _getTime(tmp);

        if (tt == t)
        {
            sscanf(fp, ",%f,%f,%f\n", tk, td, tj);
            DEBUG_OUTPUT("get KDJ\n");
            _kdjInfo[index].offset = tmpOffset[0];
            return tk - K + 1;
        }
        else if (tt > t)
        {
            goto END;
        }

        if (tk - K == num - 1)
        {
            int i = 1;
            for(;i < num; i++)
            {
                tmpOffset[i - 1] = tmpOffset[i];
                K[i - 1] = K[i];
                D[i - 1] = D[i];
                J[i - 1] = J[i];
            }
            sscanf(fp, ",%f,%f,%f\n", K + num - 2, D + num - 2, J + num - 2);
            while(*fp != '\n')
                fp++;
            fp++;
        }
        else
        {
            sscanf(fp, ",%f,%f,%f\n", tk, td, tj);
            while(*fp != '\n')
                fp++;
            fp++;
            tk++;
            td++;
            tj++;
        }
    }
END:
    return 0;
}

// get BOLL,UB,LB values
// BOLL[] for BOLL[last, today]
// UB[] for UB[last, today]
// LB[] for LB[last, today]
// return the actual number of the obtained data
int DAF::getBOLLValueByBuf(int index, char* date, float* BOLL, float* UB, float* LB, int num)
{
    char tmp[64] = {0};
    char c;
    long t = _getTime(date);
    int tmpOffset[20];
        
    if (_bollInfo[index].content == NULL)
        return 0;
    char* fp = _bollInfo[index].content;
    BOLL[0] = 0.0;
    UB[0] = 0.0;
    LB[0] = 0.0;
    if (_bollInfo[index].offset == 0)
    {
        fp += 16;
    }
    else
    {
        fp += _bollInfo[index].offset;
    }

    float *tb = BOLL, *tub = UB, *tlb = LB;
    while( fp - _bollInfo[index].content < _bollInfo[index].length)
    {
        memset(tmp, 0, sizeof(tmp));
        tmpOffset[tb - BOLL] = fp - _bollInfo[index].content;
        memcpy(tmp, fp, 10);
        fp += 10;
        long tt = _getTime(tmp);

        if (tt == t)
        {
            sscanf(fp, ",%f,%f,%f\n", tb, tub, tlb);
            DEBUG_OUTPUT("get BOLL\n");
            _bollInfo[index].offset = tmpOffset[0];
            return tb - BOLL + 1;
        }
        else if (tt > t)
        {
            goto END;
        }

        if (tb - BOLL == num - 1)
        {
            int i = 1;
            for(;i < num; i++)
            {
                tmpOffset[i - 1] = tmpOffset[i];
                BOLL[i - 1] = BOLL[i];
                UB[i - 1] = UB[i];
                LB[i - 1] = LB[i];
            }
            sscanf(fp, ",%f,%f,%f\n", BOLL + num - 2, UB + num - 2, LB + num -2);
            while(*fp != '\n')
                fp++;
            fp++;
        }
        else
        {
            sscanf(fp, ",%f,%f,%f\n", tb, tub, tlb);
            while(*fp != '\n')
                fp++;
            fp++;
            tb++;
            tub++;
            tlb++;
        }
    }
END:
    return 0;
}

void DAF::logfile(char* appendStr)
{
    char tmp[128];
    sprintf(tmp, "%s%s%s.log", LOG_DIR, _name, appendStr);
    FILE* fp = fopen(tmp, "w");
    if (!fp)
    {
        printf("Can't open %s\n", tmp);
        return;
    }
    fprintf(fp, "%s", _logString);
    fclose(fp);
    return;
}

//2018-01-08(buy) 20102566(money) 13.650000(buy price)
//13.720000(sell price) 1465201(amount) 2018-01-04(sell) 000409(index)
long DAF::profit(long money)
{
    char tmp[256];
    if ( (_hold !=0) || (_sell.next.open == 0) )
    {
        printf("\nNot sold yet, force sell!\n");
        if (_current.trade.index == _hold)
            memcpy(&_sell, &_current, sizeof(_current));
        else
        {
            printf("Actually not bought any stock yet!\n");
            return money;
        }
        _hold = 0;
    }
    //long amount = (long)(money / (_buy.next.open * 100)) * 100;
    float feeChange = 0;
    if (_buy.trade.index >= 600000)
    {
        feeChange = FEE_CHANGE;
    }
    long amount = (long)(money / (100 * _buy.next.open + 100 * _buy.next.open * FEE_STOCK_COMPANY + feeChange)) * 100;
    long newMoney = money + (_sell.next.open - _buy.next.open) * amount;
    float feeBuy = 0, feeSell = 0;
    //float f = 0;
    feeBuy = amount * _buy.next.open * FEE_STOCK_COMPANY;
    //f = f > 5 ? f : 5;
    //fee += f;
    if (_buy.trade.index >= 600000)
    {
        feeBuy += (FEE_CHANGE * (amount / 100));
    }

    feeSell = amount * _sell.next.open * FEE_STOCK_COMPANY;
    feeSell += (FEE_PRINT * amount * _sell.next.open);
    newMoney -= (feeSell + feeBuy);
    _fee += (feeBuy + feeSell);
    printf("Buy [%06d] on %s: price = %f, number = %ld\nSell on %s: price = %f\n",
            _buy.trade.index, _buy.next.dateStr, _buy.next.open, amount,
            _sell.next.dateStr, _sell.next.open);
    sprintf(tmp, "%s %ld %f %f %ld %s %06d, %f\n", _sell.next.dateStr, newMoney,
            _buy.next.open, _sell.next.open, amount, _buy.next.dateStr, _buy.trade.index, _fee);
    strcat(_logString, tmp);
    return newMoney;
}

static dayTradeList s_trade[ALL_STOCK_NUM] = {0};
int DAF::buy(char* date)
{
    int i;
    int sm0, sm1;
    if (!_init)
        initIndicator();
    printf("Checking %s...\n", date);
    CHECK_MARKET_MASK(_marketMask, sm0, sm1);

    int target = 0;
    omp_set_num_threads(8);
    bool gotten = false;
    for (i = sm0; i < sm1; i ++)
    {
        #pragma omp parallel for
        for (int j = _indexList[i][0]; j <= _indexList[i][1]; j++)
        {
            s_trade[j] = getDayTradeByBuf(j, date);
            if (buyChecker(date, j, s_trade + j))
                gotten = true;
        }

        if (!gotten)
            continue;
        else
            gotten = false;
    }

    int maxScore = 0;
    for (i = sm0; i < sm1; i++)
    {
        for (int j = _indexList[i][0]; j <= _indexList[i][1]; j++)
        {
            if (!_score[j])
                continue;
            if (_score[j] > _score[target])
            {
                target = j;
            }
            _score[target] = 0;
        }

    }

    if (target != 0)
    {
        _hold = target;
        memcpy(&_buy, s_trade + target, sizeof(dayTradeList));
        printf("Got one: %06d\n", _hold);
        _score[target] = 0;
        return _hold;
    }
    return 0;
}

char* DAF::sell(char* date)
{
    dayTradeList tl = getDayTradeByBuf(_hold, date);
    if (tl.trade.open)
    {
        memcpy(&_current, &tl, sizeof(tl));
        if (sellChecker(date, _hold, &tl))
        {
            memcpy(&_sell, &tl, sizeof(tl));
            _hold = 0;
            strcpy(_dateStr, _sell.next.dateStr);
            return _dateStr;
        }
    }
    return NULL;
}
