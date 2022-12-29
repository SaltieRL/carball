// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "GraphLine.h"
#include "RUGraph.h"
#include "../../GFXUtilities/point2.h"

GraphLine::GraphLine(RUGraph* newParent, SDL_Color newColor) : Graphable(newParent, newColor)
{
	// put code here to initialize private GraphLine variables
}

GraphLine::~GraphLine()
{
	// put code here to destroy private GraphLine variables
}

void GraphLine::draw(SDL_Renderer* renderer)
{
	if(points.empty())
		return;

	SDL_SetRenderDrawColor(renderer, getColor().r, getColor().g, getColor().b, getColor().a);

	float xRange = (float)points.size(); // points per x axis
	float yRange = y_max - y_min;

	float pointXGap = ((float)parent->getWidth()) / xRange;
	float pointYGap = ((float)parent->getHeight()) / yRange;

	Point2* cPoint = NULL;
	Point2* prevPoint = NULL;
	for (int i = 0; i < points.size(); ++i)
	{
		float newXValue = i * pointXGap;
		float newYValue = (points[i]->getY() - y_min) * pointYGap;

		// add it to the background
		cPoint = new Point2(parent->getAxisOriginX() + newXValue,
							parent->getAxisOriginY() + parent->getHeight() - newYValue);

		// draw a thick line from the previous to the current point
		if ((prevPoint) && (i > 0))
		{
			SDL_RenderDrawLine(renderer, prevPoint->getX(), prevPoint->getY() - 1, cPoint->getX(),
							   cPoint->getY() - 1);
			SDL_RenderDrawLine(renderer, prevPoint->getX(), prevPoint->getY(), cPoint->getX(),
							   cPoint->getY());
			SDL_RenderDrawLine(renderer, prevPoint->getX(), prevPoint->getY() + 1, cPoint->getX(),
							   cPoint->getY() + 1);
		}

		// save the previous point for later
		if (prevPoint)
			delete prevPoint;
		prevPoint = cPoint;
	}

	if (cPoint)
		delete cPoint;
}

std::string GraphLine::getType() const
{
	return "GraphLine";
}