#ifndef STRING_UTILS_HPP
#define STRING_UTILS_HPP

#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <cctype>

namespace string_utils {

// Split string by delimiter
std::vector<std::string> split(const std::string& str, const std::string& delimiter = " ") {
    std::vector<std::string> result;
    if (delimiter.empty()) {
        // Split by whitespace
        std::istringstream iss(str);
        std::string token;
        while (iss >> token) {
            result.push_back(token);
        }
    } else {
        size_t start = 0;
        size_t end = str.find(delimiter);
        while (end != std::string::npos) {
            result.push_back(str.substr(start, end - start));
            start = end + delimiter.length();
            end = str.find(delimiter, start);
        }
        result.push_back(str.substr(start));
    }
    return result;
}

// Trim whitespace from left
std::string lstrip(const std::string& str) {
    size_t start = 0;
    while (start < str.length() && std::isspace(static_cast<unsigned char>(str[start]))) {
        start++;
    }
    return str.substr(start);
}

// Trim whitespace from right
std::string rstrip(const std::string& str) {
    size_t end = str.length();
    while (end > 0 && std::isspace(static_cast<unsigned char>(str[end - 1]))) {
        end--;
    }
    return str.substr(0, end);
}

// Trim whitespace from both sides
std::string strip(const std::string& str) {
    return lstrip(rstrip(str));
}

// Join vector of strings with delimiter
std::string join(const std::string& delimiter, const std::vector<std::string>& items) {
    if (items.empty()) return "";
    std::ostringstream oss;
    oss << items[0];
    for (size_t i = 1; i < items.size(); i++) {
        oss << delimiter << items[i];
    }
    return oss.str();
}

// Replace all occurrences of old_str with new_str
std::string replace(const std::string& str, const std::string& old_str, const std::string& new_str) {
    std::string result = str;
    size_t pos = 0;
    while ((pos = result.find(old_str, pos)) != std::string::npos) {
        result.replace(pos, old_str.length(), new_str);
        pos += new_str.length();
    }
    return result;
}

// Check if string starts with prefix
bool startswith(const std::string& str, const std::string& prefix) {
    if (prefix.length() > str.length()) return false;
    return str.substr(0, prefix.length()) == prefix;
}

// Check if string ends with suffix
bool endswith(const std::string& str, const std::string& suffix) {
    if (suffix.length() > str.length()) return false;
    return str.substr(str.length() - suffix.length()) == suffix;
}

}  // namespace string_utils

#endif  // STRING_UTILS_HPP
