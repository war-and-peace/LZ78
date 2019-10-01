cmake_minimum_required(VERSION 3.0.0)
project(LZ78 VERSION 0.1.0)

include(CTest)
enable_testing()

add_executable(LZ78_compressor compressor.cpp)
add_executable(LZ78_decompressor decompressor.cpp)

target_compile_options(LZ78_compressor PRIVATE -std=c++17)
target_compile_options(LZ78_decompressor PRIVATE -std=c++17)

target_link_libraries(LZ78_compressor stdc++fs)
target_link_libraries(LZ78_decompressor stdc++fs)
set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
