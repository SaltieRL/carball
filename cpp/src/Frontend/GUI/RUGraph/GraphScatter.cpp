// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.

#include "GraphScatter.h"
#include "RUGraph.h"
#include "../../GFXUtilities/point2.h"

GraphScatter::GraphScatter(RUGraph* newParent, SDL_Color newColor, int pointSz)
	: Graphable(newParent, newColor)
{
	pointSize = pointSz;
}

GraphScatter::~GraphScatter()
{
	pointSize = 0;
}

void GraphScatter::draw(SDL_Renderer* renderer)
{
	SDL_SetRenderDrawColor(renderer, getColor().r, getColor().g, getColor().b, getColor().a);

	// draw the line
	float xRange = (x_max - x_min) * 1.000001;
	float yRange = y_max - y_min;
	float pointXGap = ((float)parent->getWidth()) / xRange;
	float pointYGap = ((float)parent->getHeight()) / yRange;

	Point2* cPoint = NULL;
	Point2* prevPoint = NULL;
	for (int i = 0; i < points.size(); ++i)
	{
		float newXValue = (points[i]->getX() - x_min) * pointXGap;
		float newYValue = (points[i]->getY() - y_min) * pointYGap;

		// add it to the background
		cPoint = new Point2(parent->getAxisOriginX() + newXValue,
							parent->getAxisOriginY() + parent->getHeight() - newYValue);

		drawPointOutline(renderer, cPoint->getX(), cPoint->getY());

		// save the previous point for later
		if (prevPoint)
			delete prevPoint;
		prevPoint = cPoint;
	}

	if (cPoint)
		delete cPoint;
}

void GraphScatter::drawPointOutline(SDL_Renderer* renderer, int cx, int cy, int r)
{
	if (r < 0 || cx < 0 || cy < 0)
		return;
	if (r == 0)
		r = pointSize / 2;
	int x = r - 1, y = 0, dx = 1, dy = 1, err = dx - (r << 1);
	while (x >= y)
	{
		SDL_RenderDrawPoint(renderer, cx + x, cy + y);
		SDL_RenderDrawPoint(renderer, cx + y, cy + x);
		SDL_RenderDrawPoint(renderer, cx - y, cy + x);
		SDL_RenderDrawPoint(renderer, cx - x, cy + y);
		SDL_RenderDrawPoint(renderer, cx - x, cy - y);
		SDL_RenderDrawPoint(renderer, cx - y, cy - x);
		SDL_RenderDrawPoint(renderer, cx + y, cy - x);
		SDL_RenderDrawPoint(renderer, cx + x, cy - y);

		if (err <= 0)
		{
			++y;
			err += dy;
			dy += 2;
		}
		if (err > 0)
		{
			--x;
			dx += 2;
			err += dx - (r << 1);
		}
	}
}

void GraphScatter::drawPoint(SDL_Renderer* renderer, int cx, int cy, int r)
{
	if(points.empty())
		return;

	if (r == 0)
		r = pointSize / 2;
	for (int i = 1; i <= r; ++i)
		drawPointOutline(renderer, cx, cy, i);
}

std::string GraphScatter::getType() const
{
	return "GraphScatter";
}