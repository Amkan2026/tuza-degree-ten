#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <set>
#include <vector>
#include <ctime>
using Graph=std::array<unsigned,10>;
using Perm=std::array<int,5>;
using APerm=std::array<int,4>;
std::vector<Perm>cp;
std::vector<APerm>ap;
std::vector<int>to_min[1024];
int core_min[1024];
std::set<unsigned>all_sides[1024],density_sides[1024];
int cindex[5][5],aindex[4][4];
unsigned ctable[120][32],atop[24][64];
unsigned canonical_private(unsigned m){
 unsigned ans=~0u;
 for(int p=0;p<24;p++){
  unsigned t=atop[p][m>>20]<<20;
  for(int a=0;a<4;a++)t|=((m>>(5*a))&31)<<(5*ap[p][a]);
  ans=std::min(ans,t);
 }
 return ans;
}
                                                                          
                                                                   
bool small_cover(const Graph&g,unsigned remain,int budget){
 if(budget<0)return false;
 int v=-1,best=0;
 for(int i=0;i<10;i++)if(remain>>i&1){int d=__builtin_popcount(g[i]&remain);if(d>best){best=d;v=i;}}
 if(v<0)return true;
 if(!budget)return false;
 unsigned ns=g[v]&remain;
 int w=__builtin_ctz(ns);
 return small_cover(g,remain&~(1u<<v),budget-1)||small_cover(g,remain&~(1u<<w),budget-1);
}
bool search_matching(const Graph&g,Graph&rest,unsigned avail,int target,int chosen){
 if(chosen==target)return small_cover(rest,1023,target);
 if(chosen+__builtin_popcount(avail)/2<target)return false;
 if(!avail)return false;
 int v=__builtin_ctz(avail);unsigned tail=avail&~(1u<<v),ns=g[v]&tail;
 while(ns){int w=__builtin_ctz(ns);ns&=ns-1;
  rest[v]&=~(1u<<w);rest[w]&=~(1u<<v);
  bool ok=search_matching(g,rest,tail&~(1u<<w),target,chosen+1);
  rest[v]|=1u<<w;rest[w]|=1u<<v;
  if(ok)return true;
 }
 return search_matching(g,rest,tail,target,chosen);
}
bool wke(const Graph&g){Graph rest=g;for(int k=5;k>=0;k--)if(search_matching(g,rest,1023,k,0))return true;return false;}
void print_sides(const char*name,std::set<unsigned>*s){
 printf("\"%s\":{",name);bool f=true;
 for(int h=0;h<1024;h++)if(!s[h].empty()){
  printf("%s\"%d\":[",f?"":",",h);f=false;bool first=true;
  for(unsigned v:s[h]){printf("%s%u",first?"":",",v);first=false;}printf("]");
 }printf("}");
}
int main(){clock_t start=clock();
 int ci=0,ai=0;for(int a=0;a<5;a++)for(int b=a+1;b<5;b++)cindex[a][b]=cindex[b][a]=ci++;
 for(int a=0;a<4;a++)for(int b=a+1;b<4;b++)aindex[a][b]=aindex[b][a]=ai++;
 Perm p={0,1,2,3,4};do{cp.push_back(p);}while(std::next_permutation(p.begin(),p.end()));
 APerm q={0,1,2,3};do{ap.push_back(q);}while(std::next_permutation(q.begin(),q.end()));
 for(int j=0;j<120;j++)for(unsigned m=0;m<32;m++){ctable[j][m]=0;for(int c=0;c<5;c++)if(m>>c&1)ctable[j][m]|=1u<<cp[j][c];}
 for(int j=0;j<24;j++)for(unsigned m=0;m<64;m++){atop[j][m]=0;for(int a=0;a<4;a++)for(int b=a+1;b<4;b++)if(m>>aindex[a][b]&1)atop[j][m]|=1u<<aindex[ap[j][a]][ap[j][b]];}
 for(int h=0;h<1024;h++){
  core_min[h]=1024;
  for(int j=0;j<120;j++){
   unsigned image=0;for(int a=0;a<5;a++)for(int b=a+1;b<5;b++)if(h>>cindex[a][b]&1)image|=1u<<cindex[cp[j][a]][cp[j][b]];
   if((int)image<core_min[h]){core_min[h]=image;to_min[h].clear();}
   if((int)image==core_min[h])to_min[h].push_back(j);
  }
 }
 char line[100];unsigned long graphs=0,outside=0,ports=0,selected_ports=0;long long max_wke_ms=0;
 while(fgets(line,sizeof(line),stdin)){
  if(line[0]-63!=10)return 2;
  Graph g={};int pos=0;
  for(int b=1;b<10;b++)for(int a=0;a<b;a++,pos++)if((line[1+pos/6]-63)>>(5-pos%6)&1){g[a]|=1u<<b;g[b]|=1u<<a;}
  graphs++;
  if(wke(g))continue;
  outside++;
  int densities[10]={},maxdensity=0;
  for(int r=0;r<10;r++)if(__builtin_popcount(g[r])==5){
   for(int a=0;a<10;a++)if(g[r]>>a&1)for(int b=a+1;b<10;b++)if((g[r]>>b&1)&&(g[a]>>b&1))densities[r]++;
   maxdensity=std::max(maxdensity,densities[r]);
  }
  for(int r=0;r<10;r++)if(__builtin_popcount(g[r])==5){
   ports++;std::array<int,5>C;std::array<int,4>A;int nc=0,na=0;
   for(int a=0;a<10;a++)if(a!=r){if(g[r]>>a&1)C[nc++]=a;else A[na++]=a;}
   assert(nc==5&&na==4);
   int h=0;unsigned s=0;
   for(int a=0;a<5;a++)for(int b=a+1;b<5;b++)if(g[C[a]]>>C[b]&1)h|=1u<<cindex[a][b];
   for(int a=0;a<4;a++)for(int b=0;b<5;b++)if(g[A[a]]>>C[b]&1)s|=1u<<(5*a+b);
   for(int a=0;a<4;a++)for(int b=a+1;b<4;b++)if(g[A[a]]>>A[b]&1)s|=1u<<(20+aindex[a][b]);
   bool selected=densities[r]==maxdensity;if(selected)selected_ports++;
   for(int j:to_min[h]){
    unsigned image=s&~((1u<<20)-1);
    for(int a=0;a<4;a++)image|=ctable[j][(s>>(5*a))&31]<<(5*a);
    image=canonical_private(image);
    all_sides[core_min[h]].insert(image);
    if(selected)density_sides[core_min[h]].insert(image);
   }
  }
  if(outside%5000==0)fprintf(stderr,"graphs %lu nonWKE %lu ports %lu cpu %.1f\n",graphs,outside,ports,(double)(clock()-start)/CLOCKS_PER_SEC);
 }
 size_t nf=0,nd=0;for(int h=0;h<1024;h++){nf+=all_sides[h].size();nd+=density_sides[h].size();}
 printf("{\"all_connected_maxdegree5_links\":%lu,\"nonWKE_links\":%lu,\"rooted_ports\":%lu,\"density_selected_ports\":%lu,\"total_full_sides\":%zu,\"total_density_sides\":%zu,\"cpu_seconds\":%.3f,",graphs,outside,ports,selected_ports,nf,nd,(double)(clock()-start)/CLOCKS_PER_SEC);
 print_sides("full_sides",all_sides);printf(",");print_sides("density_sides",density_sides);printf("}\n");
 fprintf(stderr,"FINISHED graphs %lu nonWKE %lu ports %lu sides %zu density %zu cpu %.1f\n",graphs,outside,ports,nf,nd,(double)(clock()-start)/CLOCKS_PER_SEC);
}
