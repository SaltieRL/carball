if(NOT (${CMAKE_BINARY_DIR} STREQUAL "${CMAKE_SOURCE_DIR}/build"))
	message(FATAL_ERROR "Must be in \"build\" directory")
endif()

#Init
cmake_minimum_required(VERSION 3.5.1)
set(CMAKE_CXX_STANDARD 98)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

#Project
project(Circles)
set(G_VERSION_MAJOR 0)
set(G_VERSION_MINOR 1)

#Subdirectories
include_directories(${CMAKE_SOURCE_DIR})
add_subdirectory(src)

#make run
add_custom_target(run
	COMMAND ${PROJECT_NAME}
	DEPENDS ${PROJECT_NAME}
	WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

#make debug
add_custom_target(debug
	COMMAND gdb ./build/${PROJECT_NAME}
	DEPENDS ${PROJECT_NAME}
	WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

#make mem
	add_custom_target(mem
	COMMAND valgrind --leak-check=full --track-origins=yes --show-reachable=yes ./build/${PROJECT_NAME}
	DEPENDS ${PROJECT_NAME}
	WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

#make profile
	add_custom_target(profile
	COMMAND valgrind --tool=callgrind ./build/${PROJECT_NAME}
	DEPENDS ${PROJECT_NAME}
	WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)
