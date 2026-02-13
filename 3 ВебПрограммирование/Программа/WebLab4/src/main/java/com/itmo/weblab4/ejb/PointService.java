package com.itmo.weblab4.ejb;

import com.itmo.weblab4.entity.Point;
import com.itmo.weblab4.entity.User;
import javax.ejb.Stateless;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.Query;

import java.time.LocalDateTime;
import java.util.List;

@Stateless
public class PointService {
    
    @PersistenceContext(unitName = "default")
    private EntityManager em;
    
    public boolean checkHit(double x, double y, double r) {
        double absR = Math.abs(r);

        if (x <= 0 && y >= 0 && y - x <= absR / 2) {
            return true;
        }
        if (x <= 0 && y <= 0 && x >= -absR && y >= -absR) {
            return true;
        }
        if (x >= 0 && y <= 0 && x * x + y * y <= absR * absR) {
            return true;
        }
        return false;
    }
    
    public Point savePoint(double x, double y, double r, String username) {
        Query userQuery = em.createQuery("SELECT u FROM User u WHERE u.username = :username");
        userQuery.setParameter("username", username);
        User user = (User) userQuery.getSingleResult();
        
        long startTime = System.currentTimeMillis();
        boolean hit = checkHit(x, y, r);
        long executionTime = System.currentTimeMillis() - startTime;
        
        Point point = new Point(x, y, r, hit, LocalDateTime.now(), executionTime, user);
        em.persist(point);
        
        return point;
    }
    
    public List<Point> getPointsByUser(String username) {
        Query query = em.createQuery("SELECT p FROM Point p WHERE p.user.username = :username ORDER BY p.currentTime DESC");
        query.setParameter("username", username);
        return query.getResultList();
    }
    
    public void clearPointsByUser(String username) {
        Query query = em.createQuery("SELECT p FROM Point p WHERE p.user.username = :username");
        query.setParameter("username", username);
        List<Point> points = query.getResultList();
        
        for (Point point : points) {
            em.remove(point);
        }
    }
}
