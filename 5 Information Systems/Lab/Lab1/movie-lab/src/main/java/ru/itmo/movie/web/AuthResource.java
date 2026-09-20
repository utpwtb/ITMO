package ru.itmo.movie.web;
import jakarta.enterprise.context.RequestScoped;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;
import jakarta.servlet.http.*;
import java.util.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import ru.itmo.movie.persistence.Database;
import ru.itmo.movie.service.Problem;
@Path("auth") @RequestScoped @Produces(MediaType.APPLICATION_JSON)
public class AuthResource {
 @Context HttpServletRequest request;
 @GET public Map<String,Object> status() {
  HttpSession s=request.getSession(false);
  return s==null?Map.of("authenticated",false):Map.of("authenticated",s.getAttribute("user")!=null,"user",Objects.toString(s.getAttribute("user"),""),"csrf",Objects.toString(s.getAttribute("csrf"),""));
 }
 @POST @Consumes(MediaType.APPLICATION_JSON) public Map<String,Object> login(Map<String,String> data) {
  String user=data.getOrDefault("username","");String password=data.getOrDefault("password","");
  if(!user.equals(Database.config("MOVIE_USER","student"))||!MessageDigest.isEqual(password.getBytes(StandardCharsets.UTF_8),Database.config("MOVIE_PASSWORD","student").getBytes(StandardCharsets.UTF_8)))throw new Problem(401,"Неверное имя пользователя или пароль");
  HttpSession old=request.getSession(false);if(old!=null)old.invalidate();
  HttpSession s=request.getSession(true);s.setAttribute("user",user);s.setAttribute("csrf",UUID.randomUUID().toString());return status();
 }
 @DELETE public Map<String,String> logout() {request.getSession().invalidate();return Map.of("message","Вы вышли из системы");}
}
