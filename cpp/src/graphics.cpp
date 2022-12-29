// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "graphics.h"
#include "Frontend/GUI/RUComponent.h"
#include "Frontend/GUI/Text/RULabel.h"

bool Graphics::running = true;
int Graphics::width = 0;
int Graphics::height = 0;
float Graphics::hunterZolomon = 1.0f;

SDL_Window* Graphics::window = NULL;
SDL_GLContext Graphics::context;
SDL_Renderer* Graphics::renderer = NULL;

std::vector<RUComponent*> Graphics::guiElements;
RULabel* Graphics::fpsLabel = NULL;

int Graphics::init(int newWidth, int newHeight)
{
	width = newWidth;
	height = newHeight;

	return initHelper(false);
}

int Graphics::initHelper(bool fullscreenMode)
{
	// Initialize SDL
	int sdlStatus = SDL_Init(SDL_INIT_VIDEO);
	if (sdlStatus < 0)
	{
		printf("[GFX] Intialization error: %s\n", SDL_GetError());
		finish();
		return -1;
	}

	// Create a new window
	SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
	if (fullscreenMode)
	{
		window =
			SDL_CreateWindow("Circles", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, getWidth(),
							 getHeight(), SDL_WINDOW_OPENGL | SDL_WINDOW_FULLSCREEN_DESKTOP);

		// get the width and height
		SDL_DisplayMode DM;
		int errorNo = SDL_GetDesktopDisplayMode(0, &DM);
		if (errorNo < 0)
			return -5;
		width = DM.w;
		height = DM.h;
	}
	else
		window =
			SDL_CreateWindow("Circles", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, getWidth(),
							 getHeight(), SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE);

	if (!window)
	{
		printf("[GFX] Window error: %s\n", SDL_GetError());
		finish();
		return -2;
	}

	int errorNo = init2D();
	if (errorNo < 0)
		return errorNo;

	return 0;
}

int Graphics::init2D()
{
	// Create a new renderer; -1 loads the default video driver we need
	renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
	if (!renderer)
	{
		printf("[GFX] Renderer error: %s\n", SDL_GetError());
		finish();
		return -3;
	}
	else
		SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);

	// Init ttf
	if (TTF_Init() == -1)
	{
		printf("[GFX] TTF Init error: %s\n", SDL_GetError());
		finish();
		return -4;
	}

	return 0;
}

void Graphics::run(const std::vector<RUComponent*>& newGuiElements)
{
	//Pass in the panel gui elements
	guiElements.insert(guiElements.end(), newGuiElements.begin(), newGuiElements.end());

	// Set the FPS Component
	fpsLabel = new RULabel();
	fpsLabel->setWidth(200);
	fpsLabel->setHeight(40);
	fpsLabel->setX(width - fpsLabel->getWidth() - 6);
	fpsLabel->setY(0);
	fpsLabel->setText("");
	SDL_Color newTextColor={0xFF, 0x00, 0x00, 0xFF};
	fpsLabel->setTextColor(newTextColor);
	fpsLabel->setFontSize(40);
	fpsLabel->setVisible(true);
	guiElements.push_back(fpsLabel);

	// the display loop
	display();
	finish();
}

void Graphics::display()
{
	running = true;
	int32_t frames = 0;
	bool rotate = false;
	int32_t now = 0;
	int32_t then = SDL_GetTicks();
	then = SDL_GetTicks();

	// for mouse
	int mouseX = 0;
	int mouseY = 0;

	// for key presses
	bool CTRLPressed = false;
	bool qPressed = false;

	// draw/event loop
	while (running)
	{
		++frames;

		//=================EVENTS=================
		SDL_Event event;
		while (SDL_PollEvent(&event))
		{
			// close the window
			if (event.type == SDL_QUIT)
				running=false;

			SDL_Keycode keyPressed = 0x00;
			Uint16 keyModPressed = 0x00;
			if ((event.type == SDL_KEYUP) || (event.type == SDL_KEYDOWN))
			{
				// set the key event vars
				keyPressed = event.key.keysym.sym;
				keyModPressed = event.key.keysym.mod;

				// if((keyModPressed & KMOD_CTRL) || (keyModPressed & KMOD_LCTRL) || (keyModPressed
				// & KMOD_RCTRL))
				if ((keyPressed == SDLK_LCTRL) || (keyPressed == SDLK_RCTRL))
				{
					if (event.type == SDL_KEYUP) // Key release
						CTRLPressed = false;
					else if (event.type == SDL_KEYDOWN) // Key press
						CTRLPressed = true;
				}
				else if (keyPressed == SDLK_q)
				{
					if (event.type == SDL_KEYUP) // Key release
						qPressed = false;
					else if (event.type == SDL_KEYDOWN) // Key press
						qPressed = true;
				}

				// which command
				if (CTRLPressed)
				{
					if (qPressed)
						running=false;
				}

				// quit the gui window
				if (keyPressed == SDLK_ESCAPE)
					running=false;
			}
			else if (event.type == SDL_MOUSEBUTTONDOWN)
			{
				mouseX=event.button.x;
				mouseY=event.button.y;

				// gui elements
				for(int i=0;i<guiElements.size();++i)
				{
					RUComponent* cElement=guiElements[i];
					if (cElement)
						cElement->onMouseDownHelper(mouseX, mouseY);
				}
			}
			else if (event.type == SDL_MOUSEBUTTONUP)
			{
				mouseX=event.button.x;
				mouseY=event.button.y;

				// gui elements
				for(int i=0;i<guiElements.size();++i)
				{
					RUComponent* cElement=guiElements[i];
					if (cElement)
						cElement->onMouseUpHelper(mouseX, mouseY);
				}
			}
		}

		//=================Render=================

		// fps
		now = SDL_GetTicks();
		float cFrames = ((float)frames * 1000.0f) / ((float)(now - then));
		if (fpsLabel)
		{
			if(isinf(cFrames))
				fpsLabel->setText("Loading...");
			else
			{
				char fpsBuffer[26];
				bzero(&fpsBuffer, 26);
				sprintf(fpsBuffer, "%2.1f fps", cFrames);
				fpsLabel->setText(fpsBuffer);
			}
		}

		// Cap the frame rate
		if ((cFrames - MAX_FRAMES_PER_SECOND > 0) && (cFrames > MAX_FRAMES_PER_SECOND))
			SDL_Delay((cFrames - MAX_FRAMES_PER_SECOND));

		// gui elements
		std::pair<int, int> parentOffset(0, 0);
		for(int i=0;i<guiElements.size();++i)
		{
			RUComponent* cElement=guiElements[i];
			if (cElement)
				cElement->updateBackgroundHelper(parentOffset, renderer);
		}

		// Update the screen
		if (renderer)
			SDL_RenderPresent(renderer);
	}
}


unsigned int Graphics::RGBfromHue(double hue, int8_t* r, int8_t* g, int8_t* b)
{
	int h = int(hue * 256 * 6);
	int x = h % 0x100;

	(*r) = 0;
	(*g) = 0;
	(*b) = 0;
	switch (h / 256)
	{
	case 0:
		(*r) = 0xFF;
		(*g) = x;
		break;
	case 1:
		(*g) = 0xFF;
		(*r) = 0xFF - x;
		break;
	case 2:
		(*g) = 0xFF;
		(*b) = x;
		break;
	case 3:
		(*b) = 0xFF;
		(*g) = 0xFF - x;
		break;
	case 4:
		(*b) = 0xFF;
		(*r) = x;
		break;
	case 5:
		(*r) = 0xFF;
		(*b) = 0xFF - x;
		break;
	}

	return (*r) + ((*g) << 8) + ((*b) << 16);
}

void Graphics::addGradient(int x, int y, int size)
{
	// check the renderer
	if (!renderer)
	{
		printf("[GFX] Renderer error: %s\n", SDL_GetError());
		return;
	}

	// get it?
	SDL_Texture* tempture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA8888,
											  SDL_TEXTUREACCESS_TARGET, width, height);
	if (!tempture)
	{
		printf("[GFX] Texture error: %s\n", SDL_GetError());
		return;
	}
	else
	{
		SDL_SetRenderTarget(renderer, tempture);
		SDL_SetTextureBlendMode(tempture, SDL_BLENDMODE_BLEND);
		for (int i = (-(size / 2)); i < size / 2; ++i)
		{
			for (int j = (-(size / 2)); j < size / 2; ++j)
			{
				// calculate the hue
				double hue = ((double)((i * i) + (j * j))) / ((double)(size * size));

				// get the color
				int8_t redMask = 0;
				int8_t greenMask = 0;
				int8_t blueMask = 0;
				unsigned int colorMask = RGBfromHue(hue, &redMask, &greenMask, &blueMask);

				// set the color and draw the point
				SDL_SetRenderDrawColor(renderer, redMask, greenMask, blueMask, SDL_ALPHA_OPAQUE);
				SDL_RenderDrawPoint(renderer, x + i, y + j);
			}
		}

		// add it
		// texture.push_back(tempture);
	}
}

int Graphics::getWidth()
{
	return width;
}

int Graphics::getHeight()
{
	return height;
}

// UPDATE FUNCTION
void Graphics::clean2D()
{
	if (renderer)
	{
		SDL_DestroyRenderer(renderer);
		renderer = NULL;
	}
}

void Graphics::finish()
{
	running = false;
	clean2D();

	if (window)
	{
		SDL_DestroyWindow(window);
		window = NULL;
	}

	SDL_Quit();
	TTF_Quit();
}