#ifndef GPS_PUBLISHER_CSV_READER_HPP_
#define GPS_PUBLISHER_CSV_READER_HPP_

#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace gps_publisher {

struct GpsPoint {
  double latitude{};
  double longitude{};
};

inline void rtrim_cr(std::string & line)
{
  if (!line.empty() && line.back() == '\r') {
    line.pop_back();
  }
}

inline std::string trim(const std::string & s)
{
  const auto begin = s.find_first_not_of(" \t");
  if (begin == std::string::npos) {
    return {};
  }
  const auto end = s.find_last_not_of(" \t");
  return s.substr(begin, end - begin + 1);
}

inline double parse_coord(const std::string & token, std::size_t line_number)
{
  if (token.empty()) {
    throw std::runtime_error("CSV format error at line " + std::to_string(line_number) +
      ": empty coordinate");
  }

  std::size_t idx = 0;
  const double value = std::stod(token, &idx);
  if (idx != token.size()) {
    throw std::runtime_error("CSV format error at line " + std::to_string(line_number) +
      ": '" + token + "'");
  }
  return value;
}

/// 解析 latitude,longitude CSV。首行必須精確為 `latitude,longitude`；空行略過。
/// 檔案打不開或格式錯誤時丟出 std::runtime_error（節點在 2.7 轉成 RCLCPP_FATAL）。
inline std::vector<GpsPoint> read_csv(const std::string & path)
{
  std::ifstream in(path);
  if (!in) {
    throw std::runtime_error("Failed to open CSV: " + path);
  }

  std::vector<GpsPoint> points;
  std::string line;
  std::size_t line_number = 0;
  bool header_seen = false;

  while (std::getline(in, line)) {
    ++line_number;
    rtrim_cr(line);
    if (trim(line).empty()) {
      continue;
    }

    if (!header_seen) {
      if (line != "latitude,longitude") {
        throw std::runtime_error(
          "CSV header must be 'latitude,longitude' (line " +
          std::to_string(line_number) + ")");
      }
      header_seen = true;
      continue;
    }

    const auto comma = line.find(',');
    if (comma == std::string::npos || line.find(',', comma + 1) != std::string::npos) {
      throw std::runtime_error(
        "CSV format error at line " + std::to_string(line_number) + ": " + line);
    }

    try {
      const double lat = parse_coord(trim(line.substr(0, comma)), line_number);
      const double lon = parse_coord(trim(line.substr(comma + 1)), line_number);
      points.push_back(GpsPoint{lat, lon});
    } catch (const std::runtime_error &) {
      throw;
    } catch (const std::exception &) {
      throw std::runtime_error(
        "CSV format error at line " + std::to_string(line_number) + ": " + line);
    }
  }

  if (!header_seen) {
    throw std::runtime_error("CSV is empty or missing header: " + path);
  }

  return points;
}

}  // namespace gps_publisher

#endif  // GPS_PUBLISHER_CSV_READER_HPP_
