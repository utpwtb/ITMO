package ru.itmo.movie.web;
import jakarta.ws.rs.ApplicationPath;
import jakarta.ws.rs.core.Application;
@ApplicationPath("/api") public class ApiApplication extends Application {
 @Override public java.util.Set<Class<?>> getClasses(){return java.util.Set.of(MovieResource.class,AuthResource.class,AuthFilter.class,ErrorMapper.class);}
}
