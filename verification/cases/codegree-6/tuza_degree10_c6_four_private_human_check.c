#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
                                                                  
static unsigned A[10],D[4],P[4],r,n,Q,ne,mm[5][2],bc[4][2],bk,best[4][2],cnt;
static unsigned V(unsigned i){return 6+i;}
static unsigned first(unsigned a){if(!a)abort();return __builtin_ctz(a);}
static void edge(unsigned a,unsigned b){mm[ne][0]=a;mm[ne++][1]=b;}
static void bm(unsigned i,unsigned used){if(i==r){if(cnt>bk){bk=cnt;for(unsigned j=0;j<cnt;j++){bc[j][0]=best[j][0];bc[j][1]=best[j][1];}}return;}bm(i+1,used);for(unsigned c=0;c<4;c++)if((D[i]>>c&1)&&!(used>>c&1)){best[cnt][0]=V(i);best[cnt++][1]=c;bm(i+1,used|1u<<c);cnt--;}}
static unsigned cover(unsigned subset){for(unsigned size=0;size<=4;size++)for(unsigned k=0;k<(1u<<(4+r));k++)if(__builtin_popcount(k)==size){int ok=1;for(unsigned i=0;i<r;i++)if(subset>>i&1)for(unsigned c=0;c<4;c++)if(D[i]>>c&1)if(!(k>>c&1)&&!(k>>(4+i)&1))ok=0;if(ok){unsigned q=k&15;for(unsigned i=0;i<r;i++)if(k>>(4+i)&1)q|=1u<<V(i);return q;}}abort();}
static void hubs(void){unsigned used=0;for(unsigned i=0;i<ne;i++)used|=(1u<<mm[i][0])|(1u<<mm[i][1]);unsigned h=4;for(unsigned c=0;c<4&&h<6;c++)if(!(used>>c&1))edge(h++,c);if(h!=6)abort();}
static int literal(int kind){unsigned used=0,M[10]={0},contacts=0;for(unsigned i=0;i<ne;i++){unsigned a=mm[i][0],b=mm[i][1];if(!(A[a]>>b&1)||(used>>a&1)||(used>>b&1))return 0;used|=(1u<<a)|(1u<<b);M[a]|=1u<<b;M[b]|=1u<<a;if(a<4||b<4)contacts++;}if(__builtin_popcount(Q)>ne+(kind==2))return 0;if(kind==2&&(contacts>2||ne<2))return 0;for(unsigned a=0;a<n;a++)for(unsigned b=a+1;b<n;b++)if(A[a]>>b&1){if(kind==2&&(a==4||a==5||b==4||b==5))continue;if(!(M[a]>>b&1)&&!(Q>>a&1)&&!(Q>>b&1))return 0;}return 1;}
static int witness(void){ne=Q=bk=cnt=0;bm(0,0);unsigned pe=0;for(unsigned i=0;i<r;i++)pe+=__builtin_popcount(P[i]);pe/=2;
 if(!pe){if(bk>=3){Q=15;edge(4,5);for(unsigned j=0;j<bk;j++)edge(bc[j][0],bc[j][1]);}else{Q=(1u<<4)|(1u<<5)|cover((1u<<r)-1);for(unsigned j=0;j<bk;j++)edge(bc[j][0],bc[j][1]);hubs();}return 1;}
 if(r==2){Q=(1u<<4)|(1u<<5);if(bk==2){Q|=(1u<<6)|(1u<<7);for(unsigned j=0;j<bk;j++)edge(bc[j][0],bc[j][1]);}else{if(bk!=1)abort();Q|=cover(3);edge(6,7);}hubs();return 1;}
 if(r==3){for(unsigned a=0;a<3;a++)for(unsigned b=a+1;b<3;b++)if(P[a]>>b&1){unsigned c=3-a-b;if(D[c]){edge(V(a),V(b));edge(V(c),first(D[c]));Q=(1u<<6)|(1u<<7)|(1u<<8);return 2;}}unsigned b=0;while(b<3&&__builtin_popcount(P[b])!=2)b++;if(b==3||pe!=2)abort();Q=(1u<<4)|(1u<<5)|(1u<<V(b));edge(V(b),V(first(P[b])));hubs();return 1;}
 if(r!=4)abort();
                                                         
 for(unsigned a=0;a<4;a++)for(unsigned b=a+1;b<4;b++)if(P[a]>>b&1){unsigned rem=15^(1u<<a)^(1u<<b),c=first(rem),d=first(rem^(1u<<c));for(unsigned x=0;x<4;x++)if(D[c]>>x&1)for(unsigned y=0;y<4;y++)if(y!=x&&(D[d]>>y&1)){edge(V(a),V(b));edge(V(c),x);edge(V(d),y);Q=960;return 2;}}
                                  
 for(unsigned a=0;a<4;a++)for(unsigned b=a+1;b<4;b++)if(P[a]>>b&1){unsigned rem=15^(1u<<a)^(1u<<b),c=first(rem),d=first(rem^(1u<<c));if(P[c]>>d&1){unsigned k=cover(rem);if(__builtin_popcount(k)>1)abort();Q=(1u<<V(a))|(1u<<V(b))|k;edge(V(a),V(b));edge(V(c),V(d));return 2;}}
                                                                       
 unsigned b=0;while(b<4&&__builtin_popcount(P[b])!=pe)b++;
 if(b<4){unsigned leaves=P[b],iso=15^(1u<<b)^leaves;
  if(pe==1){unsigned a=first(leaves),d=first(iso),e=first(iso^(1u<<d)),c=first(D[d]);if(D[d]!=(1u<<c)||D[e]!=(1u<<c))abort();Q=(1u<<V(b))|(1u<<V(a))|(1u<<c);edge(V(b),V(a));edge(V(d),c);return 2;}
  if(pe==2){unsigned d=first(iso),a=first(leaves),touch=0;for(unsigned i=0;i<4;i++)if(leaves>>i&1)touch|=D[i];if(!touch){Q=(1u<<V(b))|(1u<<V(d));edge(V(b),V(a));edge(V(d),first(D[d]));return 2;}unsigned c=first(D[d]);if(D[d]!=(1u<<c))abort();Q=(1u<<V(b))|(1u<<c);edge(V(b),V(a));edge(V(d),c);return 2;}
  if(pe!=3)abort();unsigned k=cover(leaves);if(!k){Q=(1u<<4)|(1u<<5)|(1u<<V(b));edge(V(b),V(first(leaves)));hubs();return 1;}if(__builtin_popcount(k)>1)abort();unsigned a=0;while(a<4&&(!(leaves>>a&1)||!D[a]))a++;if(a==4)abort();unsigned other=first(leaves^(1u<<a));Q=(1u<<V(b))|k;edge(V(b),V(other));edge(V(a),first(D[a]));return 2;
 }
 if(pe!=3)abort();unsigned d=0;while(d<4&&P[d])d++;if(d==4||!D[d])abort();unsigned tri=15^(1u<<d),a=first(tri),b1=first(tri^(1u<<a)),touch=0;for(unsigned i=0;i<4;i++)if(tri>>i&1)touch|=D[i];Q=(1u<<V(a))|(1u<<V(b1));if(touch){unsigned c=first(D[d]);if(D[d]!=(1u<<c))abort();Q|=1u<<c;}else Q|=1u<<V(d);edge(V(a),V(b1));edge(V(d),first(D[d]));return 2;
}
int main(void){unsigned long long all=0,conn=0,wke=0,priv=0;for(r=0;r<=4;r++){n=6+r;unsigned bits=4*r+r*(r-1)/2;for(unsigned p=0;p<(1u<<bits);p++){all++;for(unsigned i=0;i<10;i++)A[i]=0;A[4]=15|(1u<<5);A[5]=15|(1u<<4);for(unsigned c=0;c<4;c++)A[c]=(1u<<4)|(1u<<5);for(unsigned i=0;i<r;i++){D[i]=p>>(4*i)&15;P[i]=0;A[V(i)]=D[i];for(unsigned c=0;c<4;c++)if(D[i]>>c&1)A[c]|=1u<<V(i);}unsigned bit=4*r;for(unsigned i=0;i<r;i++)for(unsigned j=i+1;j<r;j++,bit++)if(p>>bit&1){P[i]|=1u<<j;P[j]|=1u<<i;A[V(i)]|=1u<<V(j);A[V(j)]|=1u<<V(i);}unsigned seen=1,old;do{old=seen;for(unsigned i=0;i<n;i++)if(seen>>i&1)seen|=A[i];}while(old!=seen);if(seen!=(1u<<n)-1)continue;conn++;int kind=witness();if(!literal(kind)){fprintf(stderr,"INVALID r%u p%u kind%d Q%u ne%u\n",r,p,kind,Q,ne);return 2;}if(kind==1)wke++;else priv++;}}fprintf(stderr,"all%llu connected%llu literal_WKE%llu literal_private%llu\n",all,conn,wke,priv);return 0;}
