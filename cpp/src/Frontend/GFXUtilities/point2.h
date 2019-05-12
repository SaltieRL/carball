// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _GPOINT2
#define _GPOINT2

#include <float.h>
#include <iostream>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>

class Point2
{
private:

	double x, y;

public:

	Point2();
	Point2(double, double);
	Point2(const Point2&);
	~Point2();

	// get
	double getX() const;
	double getY() const;
	double length();

	// set
	void set(double, double);
	void setX(double);
	void setY(double);
	void normalize();

	// operators
	inline Point2 operator+(Point2 v)
	{
		v.x += x;
		v.y += y;
		return v;
	}

	inline Point2 operator-(Point2 v)
	{
		v.x = x - v.x;
		v.y = y - v.y;
		return v;
	}

	inline Point2 operator*(double scalar)
	{
		return Point2(scalar * x, scalar * y);
	}

	inline Point2 operator/(double scalar)
	{
		return Point2(x / scalar, y / scalar);
	}

	bool operator==(const Point2 v) const
	{
		// x
		double deltaX = v.x - x;
		bool xChange = ((deltaX > -DBL_EPSILON) && (deltaX < DBL_EPSILON));
		// y
		double deltaY = v.y - y;
		bool yChange = ((deltaY > -DBL_EPSILON) && (deltaY < DBL_EPSILON));

		return (xChange && yChange);
	}
};

#endif