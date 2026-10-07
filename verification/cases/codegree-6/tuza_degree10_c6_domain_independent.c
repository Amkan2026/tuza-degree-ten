                                                                         
                                                                     
                                                                        
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n,adj[10],value[1024],choice[1024],va[21],vb[21],nv;
static uint32_t matching_edges;
static int full;

static int maximum_matching(int W){
    if(!W)return 0;
    if(value[W]>=0)return value[W];
    int v=-1,small=11;
    for(int z=0;z<n;z++)if(W>>z&1){
        int d=__builtin_popcount((unsigned)(adj[z]&W));
        if(d<small){small=d;v=z;}
    }
    int rest=W^(1<<v),best=maximum_matching(rest),take=-1;
    int N=adj[v]&rest;
    while(N){int w=__builtin_ctz((unsigned)N);N&=N-1;
        int candidate=1+maximum_matching(rest^(1<<w));
        if(candidate>best){best=candidate;take=w;}
    }
    choice[W]=take<0 ? -(v+1) : (v*10+take+1);
    return value[W]=best;
}

static uint64_t edgebit(int a,int b){
    if(a>b){int t=a;a=b;b=t;}
    return 1ULL<<(a*(2*n-a-1)/2+b-a-1);
}
static uint64_t recover(int W){
    if(!W)return 0;
    maximum_matching(W);int k=choice[W];
    if(k<0)return recover(W^(1<<(-k-1)));
    int v=(k-1)/10,w=(k-1)%10;
    return edgebit(v,w)|recover(W^(1<<v)^(1<<w));
}

static int literal_witness(int *Q,uint64_t *M){
    memset(value,-1,sizeof(value));value[0]=0;
                                                                             
    for(int q=full;q>=0;q--){
        int k=__builtin_popcount((unsigned)q);
        if(k>n/2)continue;
        int out=full^q,forced_vertices=0,forced_size=0,bad=0;
        uint64_t forced_edges=0;
        for(int a=0;a<n;a++)if(out>>a&1){
            int N=adj[a]&out;
            if(N&(N-1)){bad=1;break;}
            if(N){int b=__builtin_ctz((unsigned)N);
                forced_vertices|=(1<<a)|(1<<b);
                if(a<b){forced_edges|=edgebit(a,b);forced_size++;}
            }
        }
        if(bad)continue;
        int W=full^forced_vertices;
        if(forced_size+maximum_matching(W)<k)continue;
        *Q=q;*M=forced_edges|recover(W);return 1;
    }
    return 0;
}

int verify_domain(unsigned hm,int r,const uint32_t *retained,int nr,const char *file,uint64_t *stats){
    n=7+r;full=(1<<n)-1;nv=6*r+r*(r-1)/2;
    uint32_t end=1U<<nv;
    unsigned char *inside=calloc(end,1),*covered=calloc(end,1);
    int H[6]={0},deg[6]={0},pos=0,base[10]={0};
    for(int a=0;a<6;a++)for(int b=a+1;b<6;b++,pos++)if(hm>>pos&1){H[a]|=1<<b;H[b]|=1<<a;deg[a]++;deg[b]++;}
    for(int a=0;a<6;a++){base[a]=H[a]|(1<<6);base[6]|=1<<a;}
    pos=0;
    for(int j=0;j<r;j++)for(int c=0;c<6;c++){va[pos]=c;vb[pos++]=7+j;}
    for(int j=0;j<r;j++)for(int k=j+1;k<r;k++){va[pos]=7+j;vb[pos++]=7+k;}
    for(int i=0;i<nr;i++){
        if(retained[i]>=end||inside[retained[i]]){free(inside);free(covered);return -1;}
        inside[retained[i]]=1;
    }
    FILE *f=fopen(file,"w");if(!f){free(inside);free(covered);return -2;}
    memset(stats,0,6*sizeof(uint64_t));stats[0]=end;
    for(uint32_t p=0;p<end;p++){
        memcpy(adj,base,sizeof(base));
        for(int i=0;i<nv;i++)if(p>>i&1){int a=va[i],b=vb[i];adj[a]|=1<<b;adj[b]|=1<<a;}
        int legal=1;
        for(int a=0;a<n;a++)if(__builtin_popcount((unsigned)adj[a])>6){legal=0;break;}
                                                                                
        int seen=1<<6,old;
        do{old=seen;for(int a=0;a<n;a++)if(seen>>a&1)seen|=adj[a];}while(seen!=old);
        if(seen!=full)legal=0;
        for(int a=0;a<6&&legal;a++)for(int b=a+1;b<6;b++)if(H[a]>>b&1){
            if(__builtin_popcount((unsigned)(adj[a]&adj[b]))>5){legal=0;break;}
        }
                                                                       
                                                                      
                                                                         
        if(!legal){if(inside[p]){fclose(f);free(inside);free(covered);return -3;}continue;}
        stats[1]++;
        if(inside[p]){stats[2]++;continue;}
        stats[3]++;
        if(covered[p])continue;
        int Q;uint64_t M;
        if(!literal_witness(&Q,&M)){
            fprintf(stderr,"omitted non-WKE core=%u r=%d p=%u\n",hm,r,p);
            fclose(f);free(inside);free(covered);return -4;
        }
        uint32_t lo=0,forbidden=0;
        int used=0,msize=0;
        for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(M&edgebit(a,b)){
            if(!(adj[a]>>b&1)||(used&((1<<a)|(1<<b)))){fclose(f);return -5;}
            used|=(1<<a)|(1<<b);msize++;
        }
        if(__builtin_popcount((unsigned)Q)>msize){fclose(f);return -6;}
        for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if((adj[a]>>b&1)&&!(Q>>a&1)&&!(Q>>b&1)&&!(M&edgebit(a,b))){fclose(f);return -7;}
        for(int i=0;i<nv;i++){
            int a=va[i],b=vb[i];uint64_t e=edgebit(a,b);
            if(M&e)lo|=1U<<i;
            if(!(Q>>a&1)&&!(Q>>b&1)&&!(M&e))forbidden|=1U<<i;
        }
        if((lo&forbidden)||(p&lo)!=lo||(p&forbidden)){fclose(f);return -8;}
        uint32_t freebits=(end-1)^(lo|forbidden),s=freebits;
        do{covered[lo|s]=1;if(!s)break;s=(s-1)&freebits;}while(1);
        fprintf(f,"%u %u %d %llu\n",lo,forbidden,Q,(unsigned long long)M);
        stats[4]++;
    }
    fclose(f);
    if(stats[2]!=(uint64_t)nr){free(inside);free(covered);return -9;}
    free(inside);free(covered);return 1;
}
