#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>
#include <stdexcept>
using V=std::vector<double>; using M=std::vector<V>;
const double lr=.3, eps=1e-6; const int target=2;
void validate(const V& h,const M& w,int t=target){if(h.size()!=2||w.size()!=2||t<0||t>=3)throw std::invalid_argument("shape/target");for(double x:h)if(!std::isfinite(x))throw std::invalid_argument("finite");for(const auto& r:w){if(r.size()!=3)throw std::invalid_argument("shape");for(double x:r)if(!std::isfinite(x))throw std::invalid_argument("finite");}}
V logits(const V& h,const M& w){validate(h,w);V z(3);for(int j=0;j<3;j++)for(int i=0;i<2;i++)z[j]+=h[i]*w[i][j];return z;}
V softmax(const V& z){if(z.size()!=3)throw std::invalid_argument("logits");for(double x:z)if(!std::isfinite(x))throw std::invalid_argument("finite");double m=z[0];for(double x:z)if(x>m)m=x;V e;double s=0;for(double x:z){e.push_back(std::exp(x-m));s+=e.back();}for(double& x:e)x/=s;return e;}
double loss(const V& z){return -std::log(softmax(z)[target]);}
struct G{V p,g;M d;};
G grad(const V& h,const M& w,int target=2){
    validate(h,w,target);
    V p=softmax(logits(h,w)),g=p;
    g[target]-=1;
    M d(2,V(3));
    for(int i=0;i<2;i++)for(int j=0;j<3;j++)d[i][j]=h[i]*g[j];
    return {p,g,d};
}
M update(const V& h,const M& w){auto q=grad(h,w);M n=w;for(int i=0;i<2;i++)for(int j=0;j<3;j++)n[i][j]-=lr*q.d[i][j];return n;}
M fd(const V& h,const M& w){M r(2,V(3));for(int i=0;i<2;i++)for(int j=0;j<3;j++){M a=w,b=w;a[i][j]+=eps;b[i][j]-=eps;r[i][j]=(loss(logits(h,a))-loss(logits(h,b)))/(2*eps);}return r;}
std::string f(double x){std::ostringstream s;s<<std::fixed<<std::setprecision(12)<<x;return s.str();}
std::string v(const V& a){std::string s="[";for(size_t i=0;i<a.size();i++){if(i)s+=",";s+=f(a[i]);}return s+"]";}
std::string m(const M& a){std::string s="[";for(size_t i=0;i<a.size();i++){if(i)s+=";";s+=v(a[i]).substr(1,v(a[i]).size()-2);}return s+"]";}
int main(){V h{1,2},alt{1,0},zero{0,0};M w(2,V(3));auto q=grad(h,w); M n=update(h,w); auto aq=grad(alt,w); V z=logits(h,w); V zn=logits(h,n);std::cout<<"OUTPUT_WEIGHT_MATRIX_MANUAL\n"<<"h="<<v(h)<<" target_id=2 lr=0.300000000000\n"<<"z="<<v(z)<<" p="<<v(q.p)<<" loss="<<f(loss(z))<<"\n"<<"g="<<v(q.g)<<" dW="<<m(q.d)<<"\n"<<"finite_difference="<<m(fd(h,w))<<"\n"<<"W_prime="<<m(n)<<" z_prime="<<v(zn)<<"\n"<<"p_prime="<<v(softmax(zn))<<" loss_prime="<<f(loss(zn))<<"\n"<<"alternate_h="<<v(alt)<<" dW="<<m(aq.d)<<"\n"<<"edge_h="<<v(zero)<<" dW="<<m(grad(zero,w).d)<<"\n";}
