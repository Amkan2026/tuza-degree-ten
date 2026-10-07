#include <stdint.h>
#include <stdio.h>
#include "tuza_degree9_link_wke.c"

                                                                              
                                                                        
int side_patterns(unsigned hmask,int r,uint32_t *out,uint64_t *stats){
 int n=7+r,deg[6]={0},H[6]={0},he[15][3],nh=0,pos=0;
 uint64_t base=0,cm[3][64],im[8];
 for(int a=0;a<6;a++)for(int b=a+1;b<6;b++,pos++)if(hmask>>pos&1){
  H[a]|=1<<b;H[b]|=1<<a;deg[a]++;deg[b]++;
  base|=1ULL<<edgepos(n,a,b);
  he[nh][0]=a;he[nh][1]=b;nh++;
 }
 for(int a=0;a<6;a++)base|=1ULL<<edgepos(n,a,6);
 for(int i=0;i<nh;i++)he[i][2]=4-__builtin_popcount((unsigned)(H[he[i][0]]&H[he[i][1]]));
 for(int j=0;j<r;j++)for(int d=0;d<64;d++){
  cm[j][d]=0;for(int a=0;a<6;a++)if(d>>a&1)cm[j][d]|=1ULL<<edgepos(n,a,7+j);
 }
 int nb=r*(r-1)/2;
 for(int q=0;q<(1<<nb);q++){
  im[q]=0;int bit=0;
  for(int a=0;a<r;a++)for(int b=a+1;b<r;b++,bit++)if(q>>bit&1)im[q]|=1ULL<<edgepos(n,7+a,7+b);
 }
 int count=0;uint32_t end=1U<<(6*r+nb);
 stats[0]=end;stats[1]=stats[2]=stats[3]=0;
 for(uint32_t p=0;p<end;p++){
  int D[3]={0},P[3]={0},q=p>>(6*r),bit=0,ok=1;
  for(int a=0;a<r;a++)for(int b=a+1;b<r;b++,bit++)if(q>>bit&1){P[a]|=1<<b;P[b]|=1<<a;}
  int reached=0;
  for(int j=0;j<r;j++){
   D[j]=p>>(6*j)&63;
   if(__builtin_popcount((unsigned)D[j])+__builtin_popcount((unsigned)P[j])>6){ok=0;break;}
   if(D[j])reached|=1<<j;
  }
  if(!ok)continue;
  int before;
  do{before=reached;for(int j=0;j<r;j++)if(reached>>j&1)reached|=P[j];}while(before!=reached);
  if(reached!=(1<<r)-1)continue;
  stats[1]++;
  for(int a=0;a<6&&ok;a++){
   int d=deg[a];for(int j=0;j<r;j++)d+=D[j]>>a&1;
   if(d>5)ok=0;
  }
  for(int i=0;i<nh&&ok;i++){
   int z=0,a=he[i][0],b=he[i][1];
   for(int j=0;j<r;j++)z+=((D[j]>>a&1)&&(D[j]>>b&1));
   if(z>he[i][2])ok=0;
  }
  if(!ok)continue;
  stats[2]++;
  uint64_t E=base|im[q];for(int j=0;j<r;j++)E|=cm[j][D[j]];
  if(!wke(n,E)){out[count++]=p;stats[3]++;}
 }
 return count;
}
