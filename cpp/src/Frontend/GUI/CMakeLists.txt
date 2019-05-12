#opengl lib
set(OpenGL_GL_PREFERENCE "GLVND")
find_package(OpenGL REQUIRED)
include_directories(${OPENGL_INCLUDE_DIRS})

#sdl2 lib
include(FindPkgConfig)
pkg_search_module(SDL2 REQUIRED sdl2 sdl2_ttf)
include_directories(${SDL2_INCLUDE_DIR})

set(GUI_src_files
	RUComponent.cpp
	RUComponent.h
	RUImageComponent.cpp
	RUImageComponent.h
)
add_library(GUI ${GUI_src_files})

target_link_libraries(GUI ${OPENGL_LIBRARIES} ${SDL2_LIBRARIES} SDL2_ttf)
