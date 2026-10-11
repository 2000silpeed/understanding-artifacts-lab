// C++17 toy separate chaining. Snapshot/JSON instrumentation is extra work.
#include <iostream>
#include <string>
#include <vector>
#include <utility>
#include <sstream>
using std::string;
string quote(const string& s) {
    string r="\"";
    for (unsigned char c : s) {
        if(c=='"' || c=='\\') { r+='\\'; r+=c; }
        else if(c=='\n') r+="\\n";
        else if(c < 32) { const char* h="0123456789abcdef"; r+="\\u00"; r+=h[c>>4]; r+=h[c&15]; }
        else r+=c;
    }
    return r+'"';
}
string join(const std::vector<string>& xs) {
    string r="["; for(size_t i=0;i<xs.size();++i) {if(i)r+=",";r+=xs[i];} return r+"]";
}
struct Op {string op; int key; string value;};
struct Record {string json; string result;};
class ToyMap {
    std::vector<std::vector<std::pair<int,string>>> buckets{4};
public:
    string snapshot() const {
        std::vector<string> chains;
        for(const auto& chain:buckets) {
            std::vector<string> entries;
            for(const auto& entry:chain) entries.push_back("{\"key\":"+std::to_string(entry.first)+",\"value\":"+quote(entry.second)+"}");
            chains.push_back(join(entries));
        }
        return join(chains);
    }
    Record execute(const Op& o) {
        const string before=snapshot();
        std::vector<string> comparisons,events;
        string bucket="null",result;
        if(o.key<0) {result=quote("invalid_key");events.push_back("{\"kind\":\"reject\"}");}
        else {
            const int b=o.key%4;
            bucket=std::to_string(b);
            events.push_back("{\"kind\":\"select\",\"bucket\":"+bucket+"}");
            auto& chain=buckets[b];
            size_t found=chain.size();
            for(size_t i=0;i<chain.size();++i) {
                bool equal=chain[i].first==o.key;
                string fields="\"stored_key\":"+std::to_string(chain[i].first)+",\"query_key\":"+std::to_string(o.key)+",\"equal\":"+(equal?"true":"false");
                comparisons.push_back("{"+fields+"}");events.push_back("{\"kind\":\"compare\","+fields+"}");
                if(equal) {found=i;break;}
            }
            if(o.op=="put") {
                if(found==chain.size()) {chain.emplace_back(o.key,o.value);result=quote("inserted");}
                else {chain[found].second=o.value;result=quote("updated");}
            } else if(o.op=="get") result=found==chain.size()?"null":quote(chain[found].second);
            else if(o.op=="delete") {
                result=found==chain.size()?"false":"true";
                if(found!=chain.size()) chain.erase(chain.begin()+static_cast<long>(found));
            } else throw std::runtime_error("unknown operation");
            events.push_back("{\"kind\":\"finish\",\"result\":"+result+"}");
        }
        return {"{\"op\":"+quote(o.op)+",\"key\":"+std::to_string(o.key)+",\"value\":"+(o.op=="put"?quote(o.value):"null")+",\"before\":"+before+",\"bucket\":"+bucket+",\"comparisons\":"+join(comparisons)+",\"events\":"+join(events)+",\"result\":"+result+",\"after\":"+snapshot()+"}",result};
    }
};
int main(int argc,char** argv) {
    bool trace=false,edges=false;
    for(int i=1;i<argc;++i) {trace|=string(argv[i])=="--trace";edges|=string(argv[i])=="--edges";}
    std::vector<Op> ops=edges?std::vector<Op>{{"get",0,""},{"delete",0,""},{"put",-1,"금지"},{"get",-1,""},{"delete",-1,""},{"put",0,"영"},{"put",4,"넷"},{"put",4,"새 값"},{"delete",8,""},{"get",4,""},{"delete",0,""},{"get",0,""}}:std::vector<Op>{{"put",2,"사과"},{"put",6,"배"},{"put",3,"귤"},{"get",6,""},{"put",6,"포도"},{"delete",2,""},{"get",10,""}};
    ToyMap map;string initial=map.snapshot();std::vector<string> records,outputs;
    for(const auto& op:ops) {auto r=map.execute(op);records.push_back(r.json);outputs.push_back(r.result);}
    if(trace) std::cout<<"{\"bucket_count\":4,\"key_domain\":\"nonnegative_integer\",\"rule\":\"key%4\",\"initial\":"<<initial<<",\"records\":"<<join(records)<<"}\n";
    else std::cout<<join(outputs)<<'\n';
}
