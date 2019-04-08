#ifndef BUYER_H
#define BUYER_H

/***************************************************************************
 * buyer.h: define DAF(detail analysis function) item structure            *
 *                                                     2018 Hui            *
 * *************************************************************************/

#define DAF_MAX_NUM 255         //the max number of DAF supported

typedef void* (*GET_INSTANCE)(int);
typedef struct daf_item
{
    const char* name;          //the name of the DAF
    GET_INSTANCE getInstance;  //get instance function
}DAF_item;

#endif
