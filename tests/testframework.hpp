#pragma once
#include <catch2/catch_test_macros.hpp>
#include <QString>
namespace Catch {
    template<>
    struct StringMaker<QString> {
        static std::string convert( QString const& value ) {
            return value.toStdString();
        }
    };
}