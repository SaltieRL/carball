// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _GRAPHICS
#define _GRAPHICS

#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <SDL2/SDL_ttf.h>
#include <iostream>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>

class RUComponent;
class RULabel;
class RUGraph;

class Graphics
{
	friend class RUComponent;
	friend class RUTextComponent;
	friend class RUImageComponent;
	friend class RUButton;
	friend class RULabel;
	friend class RUTextbox;

private:

	static bool running;
	static int width;
	static int height;
	static float hunterZolomon; // zoom

	static SDL_Window* window;
	static SDL_GLContext context;
	static SDL_Renderer* renderer;

	// default gui
	static RULabel* fpsLabel;

	// main
	static void display();
	static int initHelper(bool);
	static int init2D();
	static void clean2D();

	static std::vector<RUComponent*> guiElements;

public:

	static const float MAX_FRAMES_PER_SECOND = 60.0f;

	// GFX Utils
	static unsigned int RGBfromHue(double, int8_t*, int8_t*, int8_t*);

	// 2D
	static void addGradient(int, int, int);
	static int getWidth();
	static int getHeight();

	// main
	static int init(int, int);
	static void run(const std::vector<RUComponent*>&);
	static void finish();
};

#endif