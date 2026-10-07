                                                                          
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static int compare32(const void*a,const void*b){uint32_t x=*(uint32_t*)a,y=*(uint32_t*)b;return (x>y)-(x<y);}
static uint32_t permute(uint32_t p,int r,int *pi){
    uint32_t out=0;
    for(int i=0;i<r;i++)out|=((p>>(6*i))&63)<<(6*pi[i]);
    int bit=0;
    for(int a=0;a<r;a++)for(int b=a+1;b<r;b++,bit++)if(p>>(6*r+bit)&1){
        int x=pi[a],y=pi[b];if(x>y){int z=x;x=y;y=z;}
        int k=0;for(int i=0;i<r;i++)for(int j=i+1;j<r;j++,k++)if(i==x&&j==y)out|=1U<<(6*r+k);
    }
    return out;
}
int check_density(unsigned hm,int r,const uint32_t*raw,int nr,const uint32_t*selected,int ns,uint64_t*stats){
    int n=7+r,H[10]={0},pos=0;
    for(int a=0;a<6;a++)for(int b=a+1;b<6;b++,pos++)if(hm>>pos&1){H[a]|=1<<b;H[b]|=1<<a;}
    for(int a=0;a<6;a++){H[a]|=1<<6;H[6]|=1<<a;}
    int m=__builtin_popcount(hm),pi[6][3]={{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
    int permcount=r==3?6:(r==2?2:1);
    int p2[2][3]={{0,1,2},{1,0,2}};
    unsigned char*seen=calloc(ns?ns:1,1);memset(stats,0,3*sizeof(uint64_t));
    for(int i=0;i<ns;i++)if(i&&selected[i]<=selected[i-1]){free(seen);return -1;}
    for(int i=0;i<nr;i++){
        uint32_t p=raw[i],canon=p;
        for(int j=0;j<permcount;j++){
            uint32_t q=permute(p,r,r==2?p2[j]:pi[j]);if(q<canon)canon=q;
        }
        int adj[10];memcpy(adj,H,sizeof(adj));
        for(int j=0;j<r;j++)for(int c=0;c<6;c++)if(p>>(6*j+c)&1){adj[c]|=1<<(7+j);adj[7+j]|=1<<c;}
        int bit=0;for(int a=0;a<r;a++)for(int b=a+1;b<r;b++,bit++)if(p>>(6*r+bit)&1){adj[7+a]|=1<<(7+b);adj[7+b]|=1<<(7+a);}
        int exclude=0;
        for(int x=0;x<n;x++)if(__builtin_popcount((unsigned)adj[x])==6){
            int d=0;for(int a=0;a<n;a++)if(adj[x]>>a&1)for(int b=a+1;b<n;b++)if((adj[x]>>b&1)&&(adj[a]>>b&1))d++;
            if(d>m)exclude=1;
        }
        const uint32_t*hit=bsearch(&canon,selected,ns,sizeof(uint32_t),compare32);
        if(exclude&&hit){free(seen);return -2;}
        if(!exclude&&!hit){free(seen);return -3;}
        if(hit){seen[hit-selected]=1;stats[1]++;}else stats[2]++;
        stats[0]++;
    }
    for(int i=0;i<ns;i++)if(!seen[i]){free(seen);return -4;}
    free(seen);return 1;
}
