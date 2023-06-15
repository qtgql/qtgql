#pragma once
#include <stdexcept>

namespace qtgql {
namespace exceptions {
class NotImplementedError : public std::logic_error {
  struct Msg {
    const char *msg = "Function not yet implemented";
  };

public:
  explicit NotImplementedError(const Msg &msg) : std::logic_error(msg.msg){};
};

class InterfaceDeserializationError : public std::logic_error {
public:
  explicit InterfaceDeserializationError(const std::string &type_name)
      : std::logic_error("type: " + type_name +
                         " Could not be resolved to any known concrete"){};
};

class EnvironmentNotFoundError : public std::logic_error {
public:
  explicit EnvironmentNotFoundError(const std::string &env_name)
      : std::logic_error("Environment: " + env_name +
                         " Could not be found, make sure you have initialized "
                         "the environment before "
                         "you interact with any qtgql API"){};
};
} // namespace exceptions
} // namespace qtgql
