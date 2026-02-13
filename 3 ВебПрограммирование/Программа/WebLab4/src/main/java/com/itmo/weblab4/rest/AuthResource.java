package com.itmo.weblab4.rest;

import com.itmo.weblab4.ejb.UserService;
import com.itmo.weblab4.ejb.SessionManager;
import com.itmo.weblab4.entity.User;
import javax.ejb.EJB;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.ws.rs.*;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import java.util.Map;

@Path("/auth")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class AuthResource {
    
    @EJB
    private UserService userService;
    
    @EJB
    private SessionManager sessionManager;
    
    @Context
    private HttpServletRequest request;
    
    @POST
    @Path("/login")
    public Response login(Map<String, String> credentials) {
        String username = credentials.get("username");
        String password = credentials.get("password");
        
        if (username == null || password == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Map.of("error", "Missing username or password"))
                    .build();
        }
        
        User user = userService.login(username, password);
        if (user == null) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(Map.of("error", "Invalid username or password"))
                    .build();
        }
        
        HttpSession session = request.getSession();
        String sessionId = session.getId();
        
        boolean sessionCreated = sessionManager.createSession(user.getUsername(), sessionId);
        if (!sessionCreated) {
            return Response.status(Response.Status.CONFLICT)
                    .entity(Map.of("error", "User is already logged in from another location"))
                    .build();
        }
        
        session.setAttribute("user", user.getUsername());
        
        return Response.ok()
                .entity(Map.of("message", "Login successful", "username", user.getUsername()))
                .build();
    }
    
    @POST
    @Path("/register")
    public Response register(Map<String, String> credentials) {
        String username = credentials.get("username");
        String password = credentials.get("password");
        
        if (username == null || password == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Map.of("error", "Missing username or password"))
                    .build();
        }
        
        User user = userService.register(username, password);
        if (user == null) {
            return Response.status(Response.Status.CONFLICT)
                    .entity(Map.of("error", "Username already exists"))
                    .build();
        }
        
        return Response.status(Response.Status.CREATED)
                .entity(Map.of("message", "Registration successful", "username", user.getUsername()))
                .build();
    }
    
    @POST
    @Path("/logout")
    public Response logout() {
        HttpSession session = request.getSession(false);
        if (session != null) {
            String sessionId = session.getId();
            sessionManager.invalidateSession(sessionId);
            session.invalidate();
        }
        
        return Response.ok()
                .entity(Map.of("message", "Logout successful"))
                .build();
    }
    
    @GET
    @Path("/status")
    public Response getStatus() {
        HttpSession session = request.getSession(false);
        if (session != null && session.getAttribute("user") != null) {
            String username = (String) session.getAttribute("user");
            String sessionId = session.getId();
            
            if (sessionManager.isValidSession(username, sessionId)) {
                return Response.ok()
                        .entity(Map.of("loggedIn", true, "username", username))
                        .build();
            } else {
                session.invalidate();
                return Response.ok()
                        .entity(Map.of("loggedIn", false, "error", "User logged in from another location"))
                        .build();
            }
        }
        
        return Response.ok()
                .entity(Map.of("loggedIn", false))
                .build();
    }
}
