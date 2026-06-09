package com.itmo.model.dao;

import com.itmo.model.pojo.Point;

import javax.ejb.Stateless;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import java.io.Serializable;
import java.util.List;

@Stateless
public class PointDao implements Serializable {

    @PersistenceContext(unitName = "default")
    private EntityManager em;

    public void save(Point point) {
        em.persist(point);
    }

    public void deleteAll() {
        em.createQuery("DELETE FROM Point").executeUpdate();
    }

    public List<Point> getAll() {
        return em.createQuery(
                "SELECT p FROM Point p ORDER BY p.id DESC", Point.class
        ).getResultList();
    }
}
