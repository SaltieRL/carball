// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _RUCIRCLE
#define _RUCIRCLE

#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include <map>
#include "Graphable.h"

class RUGraph;
class Point2;

class Circle : public Graphable
{
private:

	std::map<int, std::map<int, int> > heatmap;
	std::vector<const Point2*> foci;
	double radius;
	int maxHit;

public:

	// constructors & destructor
	Circle(RUGraph*, SDL_Color);
	~Circle();

	void addFocalPoint(const Point2*);
	void setRadius(double);
	void createHeatmap();

	const Point2* getFocalPoint(int) const;
	double getRadius() const;

	virtual void draw(SDL_Renderer*);
	virtual std::string getType() const;
};

#endif
