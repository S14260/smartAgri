//package com.example.dormitoryadmin.utils;
//
//import org.locationtech.jts.geom.*;
//import org.locationtech.jts.geom.GeometryFactory;
//
//import java.util.List;
//
//public class GeoUtils {
//    public static boolean isPointInPolygon(double lat, double lng, List<Coordinate> polygonCoords) {
//        GeometryFactory factory = new GeometryFactory();
//        Coordinate point = new Coordinate(lng, lat); // 注意顺序 lng, lat
//        Point p = factory.createPoint(point);
//
//        polygonCoords.add(polygonCoords.get(0)); // 封闭多边形
//        Polygon polygon = factory.createPolygon(polygonCoords.toArray(new Coordinate[0]));
//
//        return polygon.contains(p);
//    }
//}
