package ru.itmo.movie.web;
import jakarta.enterprise.context.RequestScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;
import java.util.*;
import ru.itmo.movie.domain.MovieGenre;
import ru.itmo.movie.service.MovieService;
@Path("/") @RequestScoped @Produces(MediaType.APPLICATION_JSON)
public class MovieResource {
 @Inject MovieService service;
 @GET @Path("revision") public Map<String,Long> revision(){return Map.of("revision",service.revision());}
 @GET @Path("movies") public Object movies(@QueryParam("page") @DefaultValue("0") int page,@QueryParam("size") @DefaultValue("10") int size,@QueryParam("filter") @DefaultValue("name") String filter,@QueryParam("value") String value,@QueryParam("sort") @DefaultValue("id") String sort,@QueryParam("desc") @DefaultValue("false") boolean desc){return service.page(page,size,filter,value,sort,desc);}
 @GET @Path("{kind:people|coordinates|locations}") public Object all(@PathParam("kind")String kind){return service.all(kind);}
 @GET @Path("{kind:movies|people|coordinates|locations}/{id}") public Object get(@PathParam("kind")String kind,@PathParam("id")long id){return service.get(kind,id);}
 @POST @Path("{kind:movies|people|coordinates|locations}") @Consumes(MediaType.APPLICATION_JSON) public Response create(@PathParam("kind")String kind,Map<String,Object> data){return Response.status(201).entity(service.save(kind,null,data)).build();}
 @PUT @Path("{kind:movies|people|coordinates|locations}/{id}") @Consumes(MediaType.APPLICATION_JSON) public Object update(@PathParam("kind")String kind,@PathParam("id")long id,Map<String,Object> data){return service.save(kind,id,data);}
 @DELETE @Path("{kind:movies|people|coordinates|locations}/{id}") public Object delete(@PathParam("kind")String kind,@PathParam("id")long id,@QueryParam("version")long version){return Map.of("deleted",service.delete(kind,id,version));}
 @DELETE @Path("operations/box-office") public Object deleteBox(@QueryParam("value")int value){return Map.of("deleted",service.deleteByBoxOffice(value));}
 @GET @Path("operations/average") public Object average(){Map<String,Object> result=new HashMap<>();result.put("average",service.average());return result;}
 @GET @Path("operations/prefix") public Object prefix(@QueryParam("value") @DefaultValue("")String value){return service.prefix(value);}
 @POST @Path("operations/redistribute") public Object redistribute(@QueryParam("from")MovieGenre from,@QueryParam("to")MovieGenre to){return service.redistribute(from,to);}
 @POST @Path("operations/award") public Object award(@QueryParam("length")int length,@QueryParam("count")int count){return Map.of("updated",service.award(length,count));}
}
