// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "Graphable.h"
#include "RUGraph.h"
#include "../../GFXUtilities/point2.h"

Graphable::Graphable(RUGraph* newParent, SDL_Color newColor)
{
	parent = newParent;
	setColor(newColor);

	x_max = 0.0f;
	x_min = 0.0f;
	y_max = 0.0f;
	y_min = 0.0f;

	// plotter mutex
	plotMutex = (pthread_mutex_t*)malloc(sizeof(pthread_mutex_t));
	pthread_mutex_init(plotMutex, NULL);
}

Graphable::~Graphable()
{
	// dangling parent pointer (get it?)
	parent = NULL;

	x_max = 0.0f;
	x_min = 0.0f;

	y_min = 0.0f;
	y_max = 0.0f;

	clear();

	// plotter mutex
	pthread_mutex_destroy(plotMutex);
	free(plotMutex);
}

SDL_Color Graphable::getColor() const
{
	return lineColor;
}

void Graphable::setColor(SDL_Color newColor)
{
	lineColor = newColor;
}

void Graphable::computeAxisRanges(const std::vector<Point2*>& _points)
{
	if (_points.empty())
		return;
	y_max = _points[0]->getY();
	y_min = y_max;

	x_max = _points[0]->getX();
	x_min = x_max;

	for (int i = 1; i < _points.size(); ++i)
	{
		Point2* pt = _points[i];
		float y_pt = pt->getY(), x_pt = pt->getX();
		if (y_pt > y_max)
			y_max = y_pt;

		else if (y_pt < y_min)
			y_min = y_pt;

		if (x_pt < x_min)
			x_min = x_pt;

		else if (x_pt > x_max)
			x_max = x_pt;
	}
}

void Graphable::setPoints(const std::vector<Point2*>& _points)
{
	if (_points.empty())
		return;
	pthread_mutex_lock(plotMutex);
	points = _points;
	pthread_mutex_unlock(plotMutex);
	computeAxisRanges(_points);
}

void Graphable::clear()
{
	pthread_mutex_lock(plotMutex);
	points.clear();
	pthread_mutex_unlock(plotMutex);

	parent = NULL;
	x_max = 0.0f;
	x_min = 0.0f;
	y_max = 0.0f;
	y_min = 0.0f;
}

void Graphable::updateBackground(SDL_Renderer* renderer)
{
	if (!parent || !parent->isVisible() || !(parent->getWidth() > 0 && parent->getHeight() > 0))
		return;

	// draw the line
	pthread_mutex_lock(plotMutex);
	draw(renderer);
	pthread_mutex_unlock(plotMutex);
}
