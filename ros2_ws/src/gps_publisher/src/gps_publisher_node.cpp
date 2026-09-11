#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/nav_sat_fix.hpp"

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
    RCLCPP_INFO(this->get_logger(), "Advertising /gps/fix (sensor_msgs/NavSatFix)");
  }

private:
  rclcpp::Publisher<sensor_msgs::msg::NavSatFix>::SharedPtr publisher_;
};

}  // namespace gps_publisher

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<gps_publisher::GpsPublisherNode>());
  rclcpp::shutdown();
  return 0;
}
