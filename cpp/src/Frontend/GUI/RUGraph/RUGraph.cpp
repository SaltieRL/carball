// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "RUGraph.h"
#include "Graphable.h"
#include "GraphLine.h"
#include "GraphScatter.h"
#include "Circle.h"
#include "../../GFXUtilities/point2.h"

const SDL_Color RUGraph::axisColor={0x00, 0x00, 0x00, 0xFF};

RUGraph::RUGraph(int newWidth, int newHeight)
{
	width = newWidth;
	height = newHeight;

	// set the origin
	axisOriginX = 0;
	axisOriginY = 0;

	graphSize = DEFAULT_GRAPH_SIZE;
	axisWidth = DEFAULT_AXIS_WIDTH;
	gridEnabled = false;
	gridDotWidth = DEFAULT_GRIDLINE_WIDTH;
	pointTypeFlag=TYPE_FOCAL_POINT;
	cFocalPoint=NULL;
	clickMode=MODE_CIRCLES;
	prevCircle=NULL;

	// plotter mutex
	plotMutex = (pthread_mutex_t*)malloc(sizeof(pthread_mutex_t));
	pthread_mutex_init(plotMutex, NULL);

	buildDotMatrix();
}

RUGraph::~RUGraph()
{
	width = 0;
	height = 0;
	graphSize = 0;
	axisOriginX = 0;
	axisOriginY = 0;
	axisWidth = 0;
	gridEnabled = false;
	gridDotWidth = 0;
	clickMode=MODE_CIRCLES;

	clear();

	// plotter mutex
	pthread_mutex_destroy(plotMutex);
	free(plotMutex);
}

int RUGraph::getGraphSize() const
{
	return graphSize;
}

int RUGraph::getAxisOriginX() const
{
	return axisOriginX;
}

int RUGraph::getAxisOriginY() const
{
	return axisOriginY;
}

int RUGraph::getAxisWidth() const
{
	return axisWidth;
}

bool RUGraph::getGridEnabled() const
{
	return gridEnabled;
}

int RUGraph::getGridDotWidth() const
{
	return gridDotWidth;
}

int RUGraph::getMode() const
{
	return clickMode;
}

void RUGraph::setGraphSize(int newGraphSize)
{
	graphSize = newGraphSize;
	drawUpdate = true;
}

void RUGraph::setAxisWidth(int newAxisWidth)
{
	axisWidth = newAxisWidth;
	drawUpdate = true;
}

void RUGraph::setGridEnabled(bool newGridEnabled)
{
	gridEnabled = newGridEnabled;
	drawUpdate = true;
}

void RUGraph::setGridDotWidth(int newGridDotWidth)
{
	gridDotWidth = newGridDotWidth;
	drawUpdate = true;
}

void RUGraph::toggleMode()
{
	clickMode=!clickMode;
}

void RUGraph::updateBackground(SDL_Renderer* renderer)
{
	// offset
	float offsetX = 0.0f;
	float offsetY = getHeight();

	// draw the lines
	pthread_mutex_lock(plotMutex);
	std::map<std::string, Graphable*>::iterator it;

	for(int i=0;i<lines.size();++i)
	{
		Graphable* g = lines[i];
		if (g)
			g->updateBackground(renderer);
	}
	pthread_mutex_unlock(plotMutex);
}

void RUGraph::buildDotMatrix()
{
	//Lets create the dot grid
	std::vector<std::vector<float> > graphPoints;
	int dotCount = graphSize * DEFAULT_NUM_ZONES; // 20 spaces per axis

	// build the dot matrix
	std::vector<float> xPoints;
	std::vector<float> yPoints;
	for (int i = 0; i < dotCount; ++i)
	{
		for (int j = 0; j < dotCount; ++j)
		{
			xPoints.push_back(i);
			yPoints.push_back(j);
		}
	}
	graphPoints.push_back(xPoints);
	graphPoints.push_back(yPoints);

	// plot the dot grid
	addScatterPoints(graphPoints);
}

void RUGraph::setLine(const std::vector<Point2*>& graphPoints, SDL_Color lineColor, int lineType)
{
	Graphable* newPlotter;
	if (lineType == Graphable::LINE)
		newPlotter = new GraphLine(this, lineColor);
	else if (lineType == Graphable::SCATTER)
		newPlotter = new GraphScatter(this, lineColor);
	else
		return;

	newPlotter->setPoints(graphPoints);
	// add the graph comp to the graph
	pthread_mutex_lock(plotMutex);
	if (newPlotter)
		lines.push_back(newPlotter);
	pthread_mutex_unlock(plotMutex);

	// trigger the draw update
	drawUpdate = true;
}

void RUGraph::addScatterPoints(const std::vector<std::vector<float> >& graphPoints)
{
	// pairs of (expected, predicted)
	if (graphPoints.size() % 2 == 1)
		return;

	// set line colors
	SDL_Color lineColor={0x00, 0x00, 0x00, 0xFF};

	// jump pairs
	for (int i = 0; i < graphPoints.size(); i += 2)
	{
		std::vector<float> xPoints = graphPoints[i];
		std::vector<float> yPoints = graphPoints[i + 1];

		// build the line
		std::vector<Point2*> points;
		for (int p = 0; p < xPoints.size(); ++p)
		{
			points.push_back(new Point2(xPoints[p], yPoints[p]));
		}

		// set the line
		setLine(points, lineColor, 1);
	}
}

void RUGraph::clear()
{
	pthread_mutex_lock(plotMutex);
	for(int i=0;i<lines.size();++i)
		delete lines[i];
	lines.clear();
	pthread_mutex_unlock(plotMutex);

	if(cFocalPoint)
		delete cFocalPoint;
	cFocalPoint=NULL;

	clearCircles();
}

void RUGraph::addCircle(const Point2* focalPoint, double radius)
{
	printf("Circle(%f, %f, %f)\n", focalPoint->getX(), focalPoint->getY(), radius);

	SDL_Color newCircleColor={0x00, 0x00, 0xFF, 0xFF};
	Circle* newCircle=new Circle(this, newCircleColor);
	newCircle->addFocalPoint(focalPoint);
	newCircle->setRadius(radius);
	prevCircle=newCircle;

	pthread_mutex_lock(plotMutex);
	if (newCircle)
		lines.push_back(newCircle);
	circles.insert(std::pair<int, Circle*>(lines.size()-1, newCircle));
	pthread_mutex_unlock(plotMutex);

	drawUpdate=true;
}

void RUGraph::combineCirclesToEllipse(int index1, int index2)
{
	if((circles.find(index1) == circles.end()) || (circles.find(index2) == circles.end()))
		return;

	drawUpdate=true;
}

bool RUGraph::clearCircle(int index)
{
	if(circles.find(index) == circles.end())
		return false;

	if((index < 0) || (index >= lines.size()))
		return false;

	pthread_mutex_lock(plotMutex);

	Graphable* cLine=lines[index];
	if(cLine)
		lines.erase(lines.begin()+index);

	circles.clear();
	for(int i=0;i<lines.size();++i)
	{
		cLine=lines[i];
		if(!cLine)
			continue;

		if(cLine->getType() == "Circle")
			circles.insert(std::pair<int, Circle*>(i, (Circle*)cLine));
	}

	pthread_mutex_unlock(plotMutex);

	drawUpdate=true;

	return true;
}

void RUGraph::clearCircles()
{
	for(int i=0;i<lines.size();++i)
	{
		if(clearCircle(i))
			--i;
	}

	drawUpdate=true;
}

void RUGraph::onMouseDown(int eventX, int eventY)
{
	if(clickMode == MODE_CIRCLES)
	{
		if(pointTypeFlag == TYPE_RADIUS)
		{
			if(!cFocalPoint)
				return;

			//Radius
			double radius=sqrt(pow(cFocalPoint->getX()-((double)eventX), 2.0f) + pow(cFocalPoint->getY()-((double)eventY), 2.0f));
			addCircle(cFocalPoint, radius);

			//Cleanup
			if(cFocalPoint)
				delete cFocalPoint;
			cFocalPoint=NULL;
		}
		else if(pointTypeFlag == TYPE_FOCAL_POINT)
		{
			//Focal Point
			cFocalPoint=new Point2(eventX, eventY);
		}

		// Switch the type of point we are waiting for
		pointTypeFlag=!pointTypeFlag;
	}
	else if(clickMode == MODE_NELLIPSE)
	{
		if(pointTypeFlag == TYPE_RADIUS)
		{
			if(!cFocalPoint)
				return;

			//Radius
			double radius=sqrt(pow(cFocalPoint->getX()-((double)eventX), 2.0f) + pow(cFocalPoint->getY()-((double)eventY), 2.0f));
			addCircle(cFocalPoint, radius);

			//Cleanup
			if(cFocalPoint)
				delete cFocalPoint;
			cFocalPoint=NULL;

			// Switch the type of point we are waiting for
			pointTypeFlag=!pointTypeFlag;
		}
		else if(pointTypeFlag == TYPE_FOCAL_POINT)
		{
			//Focal Point
			cFocalPoint=new Point2(eventX, eventY);

			// Switch the type of point we are waiting for
			if(circles.size() == 0)
				pointTypeFlag=!pointTypeFlag;
			else
			{
				if(prevCircle)
					prevCircle->addFocalPoint(cFocalPoint);

				//Cleanup
				if(cFocalPoint)
					delete cFocalPoint;
				cFocalPoint=NULL;

				drawUpdate=true;
			}
		}
	}
}

void RUGraph::csvHeatmap(const std::vector<std::vector<std::vector<float> > >& csv)
{
	clickMode=MODE_NELLIPSE;

	//Use the mouse events to add foci
	//onMouseDown();
}

void RUGraph::onMouseUp(int eventX, int eventY)
{
	//keep track of coords for mouse up?
}

std::string RUGraph::getType() const
{
	return "RUGraph";
}
