#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>

namespace fs = std::filesystem;

class FileCompressor{
private:
    fs::path fp;
    void _compress();
    class Node{
    private:
        unsigned char c;
        unsigned int index;
        Node* parent;
        bool compare(unsigned int c){return (this->c == c);}
        std::vector<Node*> children;
    public:
        Node(const unsigned char c, unsigned int index, Node* parent): c(c), index(index), parent(parent){};
        unsigned char getSymbol(){return this->c;}
        unsigned int getIndex(){return this->index;}
        bool operator == (unsigned char c){
            return this->compare(c);
        }
        void addChild(Node* node){this->children.push_back(node);}
    };

    Node* tree;
public:
    FileCompressor() = default;
    FileCompressor(const fs::path& file_path): fp(file_path){};
    void compress();
    class file_name_not_set: std::exception{
        const char* what() const throw(){
            return "file name not set";
        }
    };
};

void FileCompressor::_compress(){
    std::ifstream in(this->fp, std::ios::in | std::ios::binary);
    unsigned char c;
    if(in.is_open()){
        while(in >> c){
            
        }
    }else{
        throw std::string("Cannot open the specified file");
    }
    // in.close();
}

void FileCompressor::compress(){
    if(this->fp.empty())throw FileCompressor::file_name_not_set();

}

int main(){

    return 0;
}