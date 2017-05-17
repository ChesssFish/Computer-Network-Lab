/*
* THIS FILE IS FOR IP FORWARD TEST
*/
#include <stdio.h>
#include <memory.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <vector>
#include <map>
#include "sysInclude.h"

#define HEADER_LEN 20
#define conv_to_net_order(x) (\
(((x) & 0xff000000) >> 24) + (((x) & 0xff0000) >> 8) + (((x) & 0xff00) << 8 ) + (((x) & 0xff) << 24))
// system support
extern void fwd_LocalRcv(char *pBuffer, int length);

extern void fwd_SendtoLower(char *pBuffer, int length, unsigned int nexthop);

extern void fwd_DiscardPkt(char *pBuffer, int type);

extern unsigned int getIpv4Address( );

// implemented by students
class Route
{
	std::vector<std::map<uint32_t, uint32_t> > rtmap;
public:
	Route();
	void add(uint32_t ip, uint32_t masklen, uint32_t nexthop);
	bool nexthop(uint32_t dest, uint32_t &nexthop);
}*rt;
typedef struct _ipv4_header{
  uint8_t fb;                       //first byte,version and ihl
  uint8_t tos;                      //type of service
  uint16_t total_length;
  uint16_t id;                      //identification
  uint16_t fragment;                //flasg and offset
  uint8_t ttl;                      //time to live
  uint8_t protocol;
  uint16_t checksum;
  uint32_t src_addr;
  uint32_t des_addr;
}ipv4_header;

Route::Route()
{
	rtmap.resize(33);
}
void Route::add(uint32_t dest, uint32_t masklen, uint32_t nexthop)
{
	int leadingip = dest >> (32 - masklen) << (32 - masklen);
	rtmap[masklen][leadingip] = nexthop;
}
bool Route::nexthop(uint32_t dest, uint32_t &nexthop)
{
	for (int i = 32; i >= 0; i--) {
		int leadingip = dest >> (32 - i) << (32 - i);
		if (rtmap[i].find(leadingip) != rtmap[i].end()) {
			nexthop = rtmap[i][leadingip];
			return true;
		}
	}
	return false;
}

void stud_Route_Init()
{
	rt = new Route();
}

void stud_route_add(stud_route_msg *proute)
{
	rt->add(conv_to_net_order(proute->dest), 
		  conv_to_net_order(proute->masklen), 
		  conv_to_net_order(proute->nexthop));
}

uint16_t calc_checksum(char *pBuffer, unsigned short length)
{
  uint32_t cksum = 0;
  uint16_t *p = (uint16_t*)pBuffer;
  for(int i = 0; i < length; i += 2){
    cksum += *p++;
  }
  while(cksum >> 16){
    cksum = (cksum >> 16) + (cksum & 0xffff);
  }
  return ~cksum;
}

int stud_fwd_deal(char *pBuffer, int length)
{
  uint32_t dest = ((ipv4_header*)pBuffer)->des_addr;
  uint32_t nexthop = 0;
  dest = conv_to_net_order(dest);
  if(dest == getIpv4Address()){
    fwd_LocalRcv(pBuffer, length);
  }
  else{
    if(rt->nexthop(dest, nexthop)){
      if(!--((ipv4_header*)pBuffer)->ttl){
        fwd_DiscardPkt(pBuffer, STUD_FORWARD_TEST_TTLERROR);return 1;
      }
      else{
        ((ipv4_header*)pBuffer)->checksum = 0;
        ((ipv4_header*)pBuffer)->checksum = calc_checksum(pBuffer, HEADER_LEN);
        fwd_SendtoLower(pBuffer, length, nexthop);
      }
    }
    else{
      fwd_DiscardPkt(pBuffer,STUD_FORWARD_TEST_NOROUTE);return 1;
    }
  }
	return 0;
}
