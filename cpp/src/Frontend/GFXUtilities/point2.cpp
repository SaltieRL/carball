// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "point2.h"

Point2::Point2()
{
	setX(0.0f);
	setY(0.0f);
}

Point2::Point2(double newX, double newY)
{
	setX(newX);
	setY(newY);
}

Point2::Point2(const Point2& p)
{
	setX(p.x);
	setY(p.y);
}

Point2::~Point2()
{
	setX(0.0f);
	setY(0.0f);
}

double Point2::getX() const
{
	return x;
}

double Point2::getY() const
{
	return y;
}

double Point2::length()
{
	return sqrt(x * x + y * y);
}

void Point2::set(double newX, double newY)
{
	setX(newX);
	setY(newY);
}

void Point2::setX(double newX)
{
	x = newX;
}

void Point2::setY(double newY)
{
	y = newY;
}

void Point2::normalize()
{
	double len = length();
	if (len == 0.0f)
		return;

	x /= len;
	y /= len;
}