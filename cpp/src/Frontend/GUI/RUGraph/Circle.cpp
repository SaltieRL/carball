// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "Circle.h"
#include "RUGraph.h"
#include "../../GFXUtilities/point2.h"
#include "../../../graphics.h"

Circle::Circle(RUGraph* newParent, SDL_Color newColor) : Graphable(newParent, newColor)
{
	radius=0.0f;
	maxHit=0;
}

Circle::~Circle()
{
	radius=0.0f;
	maxHit=0;
}

void Circle::addFocalPoint(const Point2* newFocalPoint)
{
	if(!newFocalPoint)
		return;

	const Point2* newFocalPointCopy=new Point2(floor(newFocalPoint->getX()), floor(newFocalPoint->getY()));
	foci.push_back(newFocalPointCopy);
	createHeatmap();
}

void Circle::setRadius(double newRadius)
{
	radius=newRadius;
	createHeatmap();
}

void Circle::createHeatmap()
{
	heatmap.clear();

	//Circle
	if(foci.size() == 1)
	{
		for(int focalIndex=0;focalIndex<foci.size();++focalIndex)
		{
			const Point2* cFocalPoint=foci[focalIndex];
			for (int i = -radius; i < radius; ++i)
			{
				int xIndex=cFocalPoint->getX() + i;

				std::map<int, int> newMap;
				for (int j = -radius; j < radius; ++j)
				{
					int yIndex=cFocalPoint->getY() + j;

					// calculate the distance
					double distance=sqrt(pow(((double)i), 2.0f) + pow(((double)j), 2.0f));
					double hue=distance/sqrt(pow(((double)radius), 2.0f) + pow(((double)radius), 2.0f));
					if(distance > radius)
						continue;

					//printf("i(%d,%d:%ld)\n", focalIndex, xIndex, heatmap.size());
					if(heatmap.find(xIndex) == heatmap.end())
						heatmap.insert(std::pair<int, std::map<int, int> >(xIndex, newMap));

					//printf("j(%d:%d:%ld)\n", focalIndex, yIndex, heatmap[xIndex].size());
					if(heatmap[xIndex].find(yIndex) == heatmap[xIndex].end())
						heatmap[xIndex].insert(std::pair<int, int>(yIndex, 0));

					//tick
					++heatmap[xIndex][yIndex];

					if(heatmap[xIndex][yIndex] > maxHit)
						maxHit=heatmap[xIndex][yIndex];
				}
			}
		}
	}
	//Ellipse
	else if(foci.size() > 1)
	{
		// Keep ellipseDetail (0,1]
		double ellipseDetail=0.25f;
		for(int focalIndex1=0;focalIndex1<foci.size();++focalIndex1)
		{
			const Point2* fp1=foci[focalIndex1];
			for(int focalIndex2=0;focalIndex2<foci.size();++focalIndex2)
			{
				const Point2* fp2=foci[focalIndex2];

				if(focalIndex1 == focalIndex2)
					continue;

				//slope of a line
				double deltaX=fp2->getX()-fp1->getX();
				double deltaY=fp2->getY()-fp1->getY();
				double slope=deltaY/deltaX;

				double stepX=abs(deltaX*ellipseDetail);
				double stepY=abs(deltaY*ellipseDetail);

				Point2 cp((deltaX >= 0)? fp1->getX(): fp2->getX(), (deltaY >= 0)? fp1->getY(): fp2->getY());
				while(((deltaX >= 0)? cp.getX()<=fp2->getX() : cp.getX()<=fp1->getX()) &&
					((deltaY >= 0)? cp.getY()<=fp2->getY() : cp.getY()<=fp1->getY()))
				{
					//draw a circle around a point
					for (int i = -radius; i < radius; ++i)
					{
						int xIndex=cp.getX() + i;
						std::map<int, int> newMap;
						for (int j = -radius; j < radius; ++j)
						{
							int yIndex=cp.getY() + j;

							// calculate the distance
							double distance=sqrt(pow(((double)i), 2.0f) + pow(((double)j), 2.0f));
							if(distance > radius)
								continue;

							//printf("i(%d,%d:%ld)\n", focalIndex, xIndex, heatmap.size());
							if(heatmap.find(xIndex) == heatmap.end())
								heatmap.insert(std::pair<int, std::map<int, int> >(xIndex, newMap));

							//printf("j(%d:%d:%ld)\n", focalIndex, yIndex, heatmap[xIndex].size());
							if(heatmap[xIndex].find(yIndex) == heatmap[xIndex].end())
								heatmap[xIndex].insert(std::pair<int, int>(yIndex, 0));

							//tick
							++heatmap[xIndex][yIndex];

							if(heatmap[xIndex][yIndex] > maxHit)
								maxHit=heatmap[xIndex][yIndex];
						}
					}

					cp.setX(cp.getX()+stepX);
					cp.setY(cp.getY()+stepY);
				}
			}
		}
	}
}

const Point2* Circle::getFocalPoint(int index) const
{
	if((index < 0) || (index >= foci.size()))
		return NULL;
	
	return foci[index];
}

double Circle::getRadius() const
{
	return radius;
}

void Circle::draw(SDL_Renderer* renderer)
{
	if(radius <= 0)
		return;

	if(foci.size() == 0)
		return;

	SDL_SetRenderDrawColor(renderer, getColor().r, getColor().g, getColor().b, getColor().a);

	std::map<int, std::map<int, int> >::const_iterator itr=heatmap.begin();
	for(;itr!=heatmap.end();++itr)
	{
		int xIndex=itr->first;
		std::map<int, int>::const_iterator itr2=heatmap[xIndex].begin();
		for(;itr2!=heatmap[xIndex].end();++itr2)
		{
			int yIndex=itr2->first;
			int cHeat=itr2->second;
			//printf("heatmap[%d][%d]: %d\n", xIndex, yIndex, cHeat);

			// calculate the hue
			double hue=((double)cHeat)/((double)maxHit);
			hue=1.0f-hue;

			// get the color
			int8_t redMask = 0;
			int8_t greenMask = 0;
			int8_t blueMask = 0;
			unsigned int colorMask = Graphics::RGBfromHue(hue, &redMask, &greenMask, &blueMask);

			// set the color and draw the point
			SDL_SetRenderDrawColor(renderer, redMask, greenMask, blueMask, SDL_ALPHA_OPAQUE);
			SDL_RenderDrawPoint(renderer, parent->getX() + xIndex, parent->getY() + yIndex);
		}
	}
}

std::string Circle::getType() const
{
	return "Circle";
}