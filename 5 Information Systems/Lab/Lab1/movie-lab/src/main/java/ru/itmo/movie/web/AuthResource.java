package ru.itmo.movie.web;

import jakarta.enterprise.context.RequestScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;
import jakarta.servlet.http.*;

import java.util.*;
import ru.itmo.movie.service.AuthService;

@Path("auth")
@RequestScoped
@Produces(MediaType.APPLICATION_JSON)
public class AuthResource {
    @Inject
    AuthService auth;

    @Context
    HttpServletRequest request;

    @GET
    public Map<String, Object> status() {
        HttpSession s = request.getSession(false);
        return s == null ? Map.of("authenticated", false) : Map.of("authenticated", s.getAttribute("user") != null, "user", Objects.toString(s.getAttribute("user"), ""), "csrf", Objects.toString(s.getAttribute("csrf"), ""));
    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public Map<String, Object> login(Map<String, String> data) {
        return session(auth.authenticate(data == null ? null : data.get("username"), data == null ? null : data.get("password")));
    }

    @POST
    @Path("register")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response register(Map<String, String> data) {
        String user = auth.register(data == null ? null : data.get("username"), data == null ? null : data.get("password"));
        return Response.status(Response.Status.CREATED).entity(session(user)).build();
    }

    private Map<String, Object> session(String user) {
        HttpSession old = request.getSession(false);
        if (old != null) old.invalidate();
        HttpSession s = request.getSession(true);
        s.setAttribute("user", user);
        s.setAttribute("csrf", UUID.randomUUID().toString());
        return status();
    }

    @DELETE
    public Map<String, String> logout() {
        request.getSession().invalidate();
        return Map.of("message", "Вы вышли из системы");
    }
}
