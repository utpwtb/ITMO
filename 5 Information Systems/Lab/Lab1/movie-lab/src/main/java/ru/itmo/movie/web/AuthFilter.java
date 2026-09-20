package ru.itmo.movie.web;
import jakarta.ws.rs.container.*;
import jakarta.ws.rs.core.*;
import jakarta.ws.rs.ext.Provider;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.util.Map;
@Provider public class AuthFilter implements ContainerRequestFilter {
 @Context HttpServletRequest request;
 public void filter(ContainerRequestContext context) throws IOException {
  String path=context.getUriInfo().getPath();String method=context.getMethod();
  if(path.equals("auth")&&(method.equals("POST")||method.equals("GET")))return;
  HttpSession session=request.getSession(false);
  if(session==null||session.getAttribute("user")==null){context.abortWith(Response.status(401).entity(Map.of("error","Войдите в систему")).build());return;}
  if(!method.equals("GET")&&!method.equals("HEAD")&&!String.valueOf(session.getAttribute("csrf")).equals(context.getHeaderString("X-CSRF-Token")))context.abortWith(Response.status(403).entity(Map.of("error","Недействительный CSRF-токен")).build());
 }
}
