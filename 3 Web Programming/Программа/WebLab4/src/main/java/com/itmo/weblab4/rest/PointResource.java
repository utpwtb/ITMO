package com.itmo.weblab4.rest;

import com.itmo.weblab4.ejb.PointService;
import com.itmo.weblab4.entity.Point;
import javax.ejb.EJB;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.ws.rs.*;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import java.util.List;
import java.util.Map;

@Path("/points")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class PointResource {
    
    @EJB
    private PointService pointService;
    
    @Context
    private HttpServletRequest request;
    
    private String getCurrentUsername() {
        HttpSession session = request.getSession(false);
        if (session == null) {
            return null;
        }
        return (String) session.getAttribute("user");
    }
    
    @POST
    @Path("/check")
    public Response checkPoint(Map<String, Double> pointData) {
        String username = getCurrentUsername();
        if (username == null) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(Map.of("error", "User not authenticated"))
                    .build();
        }
        
        Double x = pointData.get("x");
        Double y = pointData.get("y");
        Double r = pointData.get("r");
        
        if (x == null || y == null || r == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Map.of("error", "Missing required parameters"))
                    .build();
        }
        
        if (!isValidX(x) || !isValidY(y) || !isValidR(r)) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Map.of("error", "Invalid parameter values"))
                    .build();
        }
        
        Point point = pointService.savePoint(x, y, r, username);
        
        return Response.ok()
                .entity(Map.of(
                        "x", point.getX(),
                        "y", point.getY(),
                        "r", point.getR(),
                        "hit", point.isHit(),
                        "currentTime", point.getCurrentTime(),
                        "executionTime", point.getExecutionTime()
                ))
                .build();
    }
    
    @GET
    public Response getPoints() {
        String username = getCurrentUsername();
        if (username == null) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(Map.of("error", "User not authenticated"))
                    .build();
        }
        
        List<Point> points = pointService.getPointsByUser(username);
        
        return Response.ok()
                .entity(points)
                .build();
    }
    
    @DELETE
    public Response clearPoints() {
        String username = getCurrentUsername();
        if (username == null) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(Map.of("error", "User not authenticated"))
                    .build();
        }
        
        pointService.clearPointsByUser(username);
        
        return Response.ok()
                .entity(Map.of("message", "Points cleared successfully"))
                .build();
    }
    
    private boolean isValidX(double x) {
        return true;
    }
    
    private boolean isValidY(double y) {
        return y >= -3 && y <= 3;
    }
    
    private boolean isValidR(double r) {
        double[] validRValues = {-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2};
        for (double validR : validRValues) {
            if (Math.abs(r - validR) < 0.0001) {
                return true;
            }
        }
        return false;
    }
}
