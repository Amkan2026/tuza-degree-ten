#include <stdint.h>
#include <string.h>
static int adj[12],memo[1<<12];
static int matching(int mask){
 if(!mask)return 0;
 if(memo[mask]>=0)return memo[mask];
 int a=__builtin_ctz((unsigned)mask),rest=mask&~(1<<a),best=matching(rest),N=adj[a]&rest;
 while(N){int b=__builtin_ctz((unsigned)N);N&=N-1;int z=1+matching(rest&~(1<<b));if(z>best)best=z;}
 return memo[mask]=best;
}
int wke(int n,uint64_t emask){
 memset(adj,0,sizeof(adj));int pos=0;
 for(int a=0;a<n;a++)for(int b=a+1;b<n;b++,pos++)if((emask>>pos)&1){adj[a]|=1<<b;adj[b]|=1<<a;}
 memset(memo,-1,sizeof(memo));memo[0]=0;int full=(1<<n)-1;
 for(int q=0;q<=full;q++){
  int k=__builtin_popcount((unsigned)q);if(k>n/2)continue;
  int out=full^q,used=0,forced=0,ok=1;
  for(int a=0;a<n;a++)if((out>>a)&1){int N=adj[a]&out;if(__builtin_popcount((unsigned)N)>1){ok=0;break;}if(N){used|=1<<a;forced++;}}
  if(!ok)continue;forced/=2;
  if(forced+matching(full^used)>=k)return 1;
 }
 return 0;
}
static int edgepos(int n,int a,int b){if(a>b){int z=a;a=b;b=z;}return a*(2*n-a-1)/2+(b-a-1);}
static uint64_t recover(int n,int mask){
 if(!mask)return 0;int a=__builtin_ctz((unsigned)mask),rest=mask&~(1<<a),best=matching(mask);
 if(matching(rest)==best)return recover(n,rest);
 int N=adj[a]&rest;while(N){int b=__builtin_ctz((unsigned)N);N&=N-1;if(1+matching(rest&~(1<<b))==best)return (1ULL<<edgepos(n,a,b))|recover(n,rest&~(1<<b));}
 return 0;
}
int wke_certificate(int n,uint64_t emask,int *qout,uint64_t *mout){
 memset(adj,0,sizeof(adj));int pos=0;
 for(int a=0;a<n;a++)for(int b=a+1;b<n;b++,pos++)if((emask>>pos)&1){adj[a]|=1<<b;adj[b]|=1<<a;}
 memset(memo,-1,sizeof(memo));memo[0]=0;int full=(1<<n)-1;
 for(int q=0;q<=full;q++){
  int k=__builtin_popcount((unsigned)q);if(k>n/2)continue;
  int out=full^q,used=0,forced=0,ok=1;uint64_t M=0;
  for(int a=0;a<n;a++)if((out>>a)&1){int N=adj[a]&out;if(__builtin_popcount((unsigned)N)>1){ok=0;break;}if(N){used|=1<<a;forced++;int b=__builtin_ctz((unsigned)N);M|=1ULL<<edgepos(n,a,b);}}
  if(!ok)continue;forced/=2;
  if(forced+matching(full^used)>=k){*qout=q;*mout=M|recover(n,full^used);return 1;}
 }
 return 0;
}
