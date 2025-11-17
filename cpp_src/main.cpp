#include <iostream>
#include "requests.hpp"

int main(int argc, char** argv) {
    cpr::Response r = requests::get("https://api.github.com/repos/whoshuu/cpr/contributors");
    std::cout << r.text << std::endl;
    return 0;
}
