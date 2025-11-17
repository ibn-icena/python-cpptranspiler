#ifndef REQUESTS_HPP
#define REQUESTS_HPP

#include <cpr/cpr.h>
#include "nlohmann/json.hpp"

namespace requests {

cpr::Response get(const std::string& url) {
    return cpr::Get(cpr::Url{url});
}

} // namespace requests

#endif // REQUESTS_HPP
