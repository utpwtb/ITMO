package ru.itmo.movie.web;

import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;
import jakarta.ws.rs.ext.*;
import jakarta.persistence.PersistenceException;

import java.util.Map;
import java.util.logging.*;

import ru.itmo.movie.service.Problem;

@Provider
public class ErrorMapper implements ExceptionMapper<Exception> {
    public Response toResponse(Exception e) {
        int status = 500;
        String message = "Внутренняя ошибка сервера. Подробности в журнале.";
        if (e instanceof Problem p) {
            return Response.status(p.status).type(MediaType.APPLICATION_JSON).entity(p.body()).build();
        } else if (e instanceof WebApplicationException w) {
            status = w.getResponse().getStatus();
            message = status == 404 ? "Объект или адрес не найден" : "Некорректный запрос (" + status + ")";
        } else if (e instanceof PersistenceException) {
            var p = ru.itmo.movie.service.ImportService.databaseProblem(e);
            status = p.status;
            message = p.getMessage();
            Logger.getLogger(getClass().getName()).log(Level.SEVERE,"Database request failed",e);
            return Response.status(status).type(MediaType.APPLICATION_JSON).entity(p.body()).build();
        } else if (e instanceof IllegalArgumentException) {
            status = 400;
            message = "Проверьте формат входных данных";
        }
        if (status >= 500 || e instanceof PersistenceException)
            Logger.getLogger(getClass().getName()).log(Level.SEVERE, "Request failed", e);
        return Response.status(status).type(MediaType.APPLICATION_JSON).entity(Map.of("error", message)).build();
    }
}
