package ru.itmo.movie.web;

import jakarta.enterprise.context.RequestScoped;
import jakarta.inject.Inject;
import jakarta.servlet.http.*;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;
import java.io.*;
import java.util.*;
import ru.itmo.movie.service.*;

@Path("imports") @RequestScoped @Produces(MediaType.APPLICATION_JSON)
public class ImportResource {
    @Inject ImportService imports;
    @Inject ImportHistoryService history;
    @Context HttpServletRequest request;
    private String user() { return (String)request.getSession(false).getAttribute("user"); }

    @POST @Consumes(MediaType.MULTIPART_FORM_DATA)
    public Response upload() throws Exception {
        Part file;
        try {
            var parts=request.getParts();
            if (parts.size()!=1 || !parts.iterator().next().getName().equals("file")) throw new Problem(400,"MISSING_FILE","Требуется один файл в поле file");
            file=parts.iterator().next();
        } catch (IllegalStateException tooLarge) { throw new Problem(413,"FILE_TOO_LARGE","Файл превышает допустимый размер"); }
        if (file.getSubmittedFileName()==null || file.getSize()==0) throw new Problem(400,"MISSING_FILE","Выберите JSON-файл");
        if (file.getSize()>ImportParser.maxBytes()) throw new Problem(413,"FILE_TOO_LARGE","Файл превышает допустимый размер");
        if (file.getContentType()==null || !MediaType.valueOf(file.getContentType()).isCompatible(MediaType.APPLICATION_JSON_TYPE))
            throw new Problem(415,"UNSUPPORTED_MEDIA_TYPE","Тип файла должен быть application/json");
        try (InputStream stream=file.getInputStream()) {
            byte[] bytes=stream.readNBytes(ImportParser.maxBytes()+1);
            return Response.status(201).entity(imports.upload(user(),file.getSubmittedFileName(),bytes)).build();
        } finally { file.delete(); }
    }
    @GET public Object list(@QueryParam("page") @DefaultValue("0") int page,@QueryParam("size") @DefaultValue("10") int size) {
        return history.list(user(),page,size);
    }
    @GET @Path("{id}") public Object get(@PathParam("id") long id) { return history.get(user(),id); }
}
