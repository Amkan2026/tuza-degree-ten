                                                                         
                                                                        
                                                                         
                                                                           
                                                                       
   
#include <algorithm>
#include <array>
#include <vector>
#include <set>
#include <cstdio>
#include <cstdint>
#include <ctime>
using namespace std;
static int ce[10][2],ci[5][5];static vector<array<int,5>>cp;static unsigned adj[9];static int n;static uint8_t dp[512];static vector<unsigned>qs;
static bool wke(){unsigned full=(1u<<n)-1;fill(dp,dp+(1u<<n),0);for(unsigned s=1;s<=full;s++){unsigned bit=s&-s;int v=__builtin_ctz(bit);unsigned rest=s^bit,bs=adj[v]&rest;dp[s]=dp[rest];while(bs){unsigned b=bs&-bs;bs^=b;dp[s]=max((int)dp[s],1+dp[rest^b]);}}for(unsigned q:qs){unsigned out=full^q,used=0;int twice=0;bool good=true;for(int a=0;a<n;a++)if(out>>a&1){unsigned nb=adj[a]&out;if(nb&&(nb&(nb-1))){good=false;break;}if(nb){used|=(1u<<a)|nb;twice++;}}if(good&&twice/2+dp[full^used]>=__builtin_popcount(q))return true;}return false;}
static bool conn(){unsigned s=1,old=0;while(s!=old){old=s;for(int a=0;a<n;a++)if(s>>a&1)s|=adj[a];}return s==(1u<<n)-1;}
static void edge(int a,int b){adj[a]|=1u<<b;adj[b]|=1u<<a;}
int main(){int k=0;for(int a=0;a<5;a++)for(int b=a+1;b<5;b++){ce[k][0]=a;ce[k][1]=b;ci[a][b]=ci[b][a]=k++;}array<int,5>p={0,1,2,3,4};do{cp.push_back(p);}while(next_permutation(p.begin(),p.end()));set<int>cores;for(int h=0;h<1024;h++){int best=h;for(auto&p:cp){int z=0;for(int j=0;j<10;j++)if(h>>j&1)z|=1<<ci[p[ce[j][0]]][p[ce[j][1]]];best=min(best,z);}cores.insert(best);}if(cores.size()!=34)return 2;
 clock_t start=clock();for(n=7;n<=9;n++){int r=n-6;vector<pair<int,int>>side;for(int a=6;a<n;a++)for(int c=1;c<=5;c++)side.push_back({c,a});for(int a=6;a<n;a++)for(int b=a+1;b<n;b++)side.push_back({a,b});int bits=side.size();vector<int>pa;for(int a=6;a<n;a++)pa.push_back(a);vector<vector<int>>maps;do{vector<int>m(n);for(int a=0;a<n;a++)m[a]=a;for(int a=6;a<n;a++)m[a]=pa[a-6];maps.push_back(m);}while(next_permutation(pa.begin(),pa.end()));int si[9][9];for(int j=0;j<bits;j++)si[side[j].first][side[j].second]=si[side[j].second][side[j].first]=j;vector<unsigned>canonical(1u<<bits);for(unsigned m=0;m<(1u<<bits);m++){unsigned best=m;for(auto&p:maps){unsigned z=0;for(int j=0;j<bits;j++)if(m>>j&1)z|=1u<<si[p[side[j].first]][p[side[j].second]];best=min(best,z);}canonical[m]=best;}
 qs.clear();for(int k=n/2;k>=0;k--)for(unsigned q=0;q<(1u<<n);q++)if(__builtin_popcount(q)==k)qs.push_back(q);
 uint64_t goodn=0,typen=0;for(int h:cores){vector<bool>seen(1u<<bits,false);uint64_t gc=0;for(unsigned m=0;m<(1u<<bits);m++){fill(adj,adj+n,0);for(int c=1;c<=5;c++)edge(0,c);for(int j=0;j<10;j++)if(h>>j&1)edge(1+ce[j][0],1+ce[j][1]);for(int j=0;j<bits;j++)if(m>>j&1)edge(side[j].first,side[j].second);bool degrees=true;for(int a=0;a<n;a++)if(__builtin_popcount(adj[a])>5){degrees=false;break;}if(!degrees||!conn()||wke())continue;gc++;seen[canonical[m]]=true;}
 int count=0;for(unsigned m=0;m<(1u<<bits);m++)if(seen[m]){count++;printf("%d %d %u\n",n,h,m);}goodn+=gc;typen+=count;fprintf(stderr,"n%d core%d labelled%llu canonical%d\n",n,h,(unsigned long long)gc,count);}
 fprintf(stderr,"TOTAL n%d labelled%llu canonical%llu\n",n,(unsigned long long)goodn,(unsigned long long)typen);
 }fprintf(stderr,"cpu_seconds %.3f\n",(double)(clock()-start)/CLOCKS_PER_SEC);
}
