// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _RUGRAPH
#define _RUGRAPH

#include "../RUComponent.h"
#include <SDL2/SDL.h>
#include <map>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include <map>

class Graphable;
class Point2;
class Circle;

class RUGraph : public RUComponent
{
private:

	const static SDL_Color axisColor;

	int graphSize;
	int axisOriginX;
	int axisOriginY;
	int axisWidth;
	bool gridEnabled;
	int gridDotWidth;
	bool pointTypeFlag;
	Point2* cFocalPoint;
	bool clickMode;
	Circle* prevCircle;

	// Change to map!!!
	std::map<int, Circle*> circles;

protected:

	std::vector<Graphable*> lines;
	pthread_mutex_t* plotMutex;

	// events
	virtual void onMouseDown(int, int);
	virtual void onMouseUp(int, int);

public:

	static const int MODE_CIRCLES = 0;
	static const int MODE_NELLIPSE = 1;

	static const int TYPE_FOCAL_POINT = 0;
	static const int TYPE_RADIUS = 1;

	static const int DEFAULT_NUM_ZONES = 20;

	static const int DEFAULT_GRAPH_SIZE = 1;
	static const int DEFAULT_AXIS_WIDTH = 3;
	static const int DEFAULT_GRIDLINE_WIDTH = 1;

	// constructors & destructor
	RUGraph(int, int);
	~RUGraph();

	// gets
	int getGraphSize() const;
	int getAxisOriginX() const;
	int getAxisOriginY() const;
	int getAxisWidth() const;
	bool getGridEnabled() const;
	int getGridDotWidth() const;
	int getMode() const;

	// sets
	void setGraphSize(int);
	void setAxisWidth(int);
	void setGridEnabled(bool);
	void setGridDotWidth(int);
	void toggleMode();

	// render
	void updateBackground(SDL_Renderer*);
	virtual std::string getType() const;
	void buildDotMatrix();
	void addScatterPoints(const std::vector<std::vector<float> >&);
	void setLine(const std::vector<Point2*>&, SDL_Color, int = 0);
	void clear();

	//Circle functions
	void csvHeatmap(const std::vector<std::vector<std::vector<float> > >&);
	void addCircle(const Point2*, double);
	void combineCirclesToEllipse(int, int);
	bool clearCircle(int);
	void clearCircles();
};

#endif
