package com.itmo.weblab4.ejb;

import com.itmo.weblab4.entity.User;
import com.itmo.weblab4.util.PasswordUtil;
import javax.ejb.Stateless;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.Query;

@Stateless
public class UserService {
    
    @PersistenceContext(unitName = "default")
    private EntityManager em;
    
    public User register(String username, String password) {
        Query query = em.createQuery("SELECT u FROM User u WHERE u.username = :username");
        query.setParameter("username", username);
        if (!query.getResultList().isEmpty()) {
            return null;
        }
        
        String passwordHash = PasswordUtil.hashPassword(password);
        User user = new User(username, passwordHash);
        em.persist(user);
        return user;
    }
    
    public User login(String username, String password) {
        Query query = em.createQuery("SELECT u FROM User u WHERE u.username = :username");
        query.setParameter("username", username);
        
        if (query.getResultList().isEmpty()) {
            return null;
        }
        
        User user = (User) query.getSingleResult();
        
        if (!PasswordUtil.verifyPassword(password, user.getPasswordHash())) {
            return null;
        }
        
        return user;
    }
    
    public User findByUsername(String username) {
        Query query = em.createQuery("SELECT u FROM User u WHERE u.username = :username");
        query.setParameter("username", username);
        
        if (query.getResultList().isEmpty()) {
            return null;
        }
        
        return (User) query.getSingleResult();
    }
}
