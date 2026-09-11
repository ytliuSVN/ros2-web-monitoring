#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "gps_publisher/csv_reader.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/nav_sat_fix.hpp"
#include "sensor_msgs/msg/nav_sat_status.hpp"

namespace gps_publisher
{

class GpsPublisherNode : public rclcpp::Node
{
public:
  GpsPublisherNode()
  : Node("gps_publisher")
  {
    publisher_ = this->create_publisher<sensor_msgs::msg::NavSatFix>(
      "/gps/fix", rclcpp::SensorDataQoS());

    const std::string csv_path = resolve_csv_path();
    points_ = read_csv(csv_path);
    if (points_.empty()) {
      throw std::runtime_error("CSV has no data points: " + csv_path);
    }

    timer_ = this->create_wall_timer(
      std::chrono::milliseconds(200),
      std::bind(&GpsPublisherNode::on_timer, this));

    RCLCPP_INFO(
      this->get_logger(),
      "Publishing %zu points from %s on /gps/fix at 5 Hz",
      points_.size(), csv_path.c_str());
  }

private:
  static std::string resolve_csv_path()
  {
    const char * env = std::getenv("GPS_CSV_PATH");
    if (env != nullptr && env[0] != '\0') {
      return std::string(env);
    }
    return "/data/path_data.csv";
  }

  void on_timer()
  {
    const GpsPoint & point = points_[index_];

    sensor_msgs::msg::NavSatFix msg;
    msg.header.stamp = this->now();
    msg.header.frame_id = "gps_link";
    msg.status.status = sensor_msgs::msg::NavSatStatus::STATUS_FIX;
    msg.status.service = sensor_msgs::msg::NavSatStatus::SERVICE_GPS;
    msg.latitude = point.latitude;
    msg.longitude = point.longitude;
    msg.altitude = 0.0;
    msg.position_covariance.fill(0.0);
    msg.position_covariance_type = sensor_msgs::msg::NavSatFix::COVARIANCE_TYPE_UNKNOWN;

    publisher_->publish(msg);
    RCLCPP_DEBUG(this->get_logger(), "seq=%u lat=%.6f lon=%.6f", seq_, msg.latitude, msg.longitude);
    ++seq_;  // ROS 2 Header 無 seq；從 0 遞增，循環重播不重置
    ++index_;
    if (index_ >= points_.size()) {
      index_ = 0;
    }
  }

  rclcpp::Publisher<sensor_msgs::msg::NavSatFix>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  std::vector<GpsPoint> points_;
  std::size_t index_{0};
  std::uint32_t seq_{0};
};

}  // namespace gps_publisher

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<gps_publisher::GpsPublisherNode>());
  rclcpp::shutdown();
  return 0;
}
