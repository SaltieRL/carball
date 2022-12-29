// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _GRAPHABLE_H
#define _GRAPHABLE_H

#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>

class RUGraph;
class Point2;

class Graphable
{
protected:
	std::vector<Point2*> points;
	float x_max, x_min, y_max, y_min;
	RUGraph* parent;

private:
	SDL_Color lineColor;
	pthread_mutex_t* plotMutex;

	void computeAxisRanges(const std::vector<Point2*>&);

public:
	static const int LINE = 0;
	static const int SCATTER = 1;

	// constructors & destructor
	Graphable(RUGraph*, SDL_Color);
	virtual ~Graphable();

	// gets
	SDL_Color getColor() const;

	// sets
	void setParent(RUGraph*);
	void setColor(SDL_Color);
	void setPoints(const std::vector<Point2*>&);
	virtual void clear();

	// render
	virtual void updateBackground(SDL_Renderer*);
	virtual void draw(SDL_Renderer*) = 0;
	virtual std::string getType() const=0;
};

#endif
