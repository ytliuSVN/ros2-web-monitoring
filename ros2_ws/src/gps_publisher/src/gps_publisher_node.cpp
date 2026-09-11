#include <chrono>
#include <cstdint>
#include <functional>
#include <memory>
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
    ok_ = setup();
  }

  bool ok() const
  {
    return ok_;
  }

private:
  bool setup()
  {
    this->declare_parameter<std::string>("csv_path", "/data/path_data.csv");
    this->declare_parameter<double>("publish_rate_hz", 5.0);
    this->declare_parameter<std::string>("frame_id", "gps_link");
    this->declare_parameter<bool>("loop", true);

    const std::string csv_path = this->get_parameter("csv_path").as_string();
    const double publish_rate_hz = this->get_parameter("publish_rate_hz").as_double();
    frame_id_ = this->get_parameter("frame_id").as_string();
    loop_ = this->get_parameter("loop").as_bool();

    if (publish_rate_hz <= 0.0) {
      RCLCPP_FATAL(this->get_logger(), "publish_rate_hz must be > 0 (got %.3f)", publish_rate_hz);
      return false;
    }

    try {
      points_ = read_csv(csv_path);
    } catch (const std::exception & e) {
      RCLCPP_FATAL(this->get_logger(), "%s", e.what());
      return false;
    }

    if (points_.empty()) {
      RCLCPP_FATAL(this->get_logger(), "CSV has no data points: %s", csv_path.c_str());
      return false;
    }

    publisher_ = this->create_publisher<sensor_msgs::msg::NavSatFix>(
      "/gps/fix", rclcpp::SensorDataQoS());

    const auto period = std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::duration<double>(1.0 / publish_rate_hz));
    timer_ = this->create_wall_timer(period, std::bind(&GpsPublisherNode::on_timer, this));

    RCLCPP_INFO(
      this->get_logger(),
      "Publishing %zu points from %s on /gps/fix at %.3f Hz (frame_id=%s loop=%s)",
      points_.size(), csv_path.c_str(), publish_rate_hz, frame_id_.c_str(),
      loop_ ? "true" : "false");
    return true;
  }

  void on_timer()
  {
    if (index_ >= points_.size()) {
      if (!loop_) {
        RCLCPP_INFO(this->get_logger(), "Reached end of CSV; loop is false, stopping");
        timer_->cancel();
        return;
      }
      index_ = 0;
    }

    const GpsPoint & point = points_[index_];

    sensor_msgs::msg::NavSatFix msg;
    msg.header.stamp = this->now();
    msg.header.frame_id = frame_id_;
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
  }

  bool ok_{false};
  rclcpp::Publisher<sensor_msgs::msg::NavSatFix>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  std::vector<GpsPoint> points_;
  std::string frame_id_;
  bool loop_{true};
  std::size_t index_{0};
  std::uint32_t seq_{0};
};

}  // namespace gps_publisher

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  const auto node = std::make_shared<gps_publisher::GpsPublisherNode>();
  if (!node->ok()) {
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
