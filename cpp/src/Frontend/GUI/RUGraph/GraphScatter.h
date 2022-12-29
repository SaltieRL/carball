// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _GRAPHSCATTER_H
#define _GRAPHSCATTER_H

#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include "Graphable.h"

class RUGraph;
class Point2;

class GraphScatter : public Graphable
{
private:
	void drawPoint(SDL_Renderer*, int, int, int = 0);
	void drawPointOutline(SDL_Renderer*, int, int, int = 0);
	int pointSize;

public:
	// constructors & destructor
	GraphScatter(RUGraph*, SDL_Color, int = 4);
	~GraphScatter();

	void setPointSize(int);
	int getPointSize(int);

	virtual void draw(SDL_Renderer*);
	virtual std::string getType() const;
};

#endif
