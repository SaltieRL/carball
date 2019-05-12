#Subdirectories
include_directories(${CMAKE_SOURCE_DIR})
add_subdirectory("Frontend/GUI/RUGraph")
add_subdirectory("Frontend/GUI/Text")
add_subdirectory("Frontend/GUI")
add_subdirectory("Frontend/GFXUtilities")

set(MAIN_src_files
	main.cpp
	main.h
	graphics.cpp
	graphics.h
	csv.cpp
	csv.h
)
add_executable(${PROJECT_NAME} ${MAIN_src_files})

#Link libraries
target_link_libraries(${PROJECT_NAME}
	GraphGUI TextC GUI GU)#custom libs
