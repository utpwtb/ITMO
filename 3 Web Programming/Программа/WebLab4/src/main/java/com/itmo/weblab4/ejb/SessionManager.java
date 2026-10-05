package com.itmo.weblab4.ejb;

import javax.ejb.Singleton;
import javax.ejb.Startup;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

@Singleton
@Startup
public class SessionManager {
    
    private final Map<String, Set<String>> userSessions = new HashMap<>();
    
    private final Map<String, String> sessionUsers = new HashMap<>();
    
    public boolean createSession(String username, String sessionId) {
        synchronized (this) {
            userSessions.computeIfAbsent(username, k -> new HashSet<>()).add(sessionId);
            sessionUsers.put(sessionId, username);
            return true;
        }
    }
    
    public void invalidateSession(String sessionId) {
        synchronized (this) {
            String username = sessionUsers.remove(sessionId);
            if (username != null) {
                Set<String> sessions = userSessions.get(username);
                if (sessions != null) {
                    sessions.remove(sessionId);
                    if (sessions.isEmpty()) {
                        userSessions.remove(username);
                    }
                }
            }
        }
    }
    
    public boolean isValidSession(String username, String sessionId) {
        synchronized (this) {
            Set<String> sessions = userSessions.get(username);
            return sessions != null && sessions.contains(sessionId);
        }
    }
    
    public Set<String> getSessionIds(String username) {
        synchronized (this) {
            return userSessions.getOrDefault(username, new HashSet<>());
        }
    }
    
    public String getUsername(String sessionId) {
        synchronized (this) {
            return sessionUsers.get(sessionId);
        }
    }
    
    public boolean isUserLoggedIn(String username) {
        synchronized (this) {
            Set<String> sessions = userSessions.get(username);
            return sessions != null && !sessions.isEmpty();
        }
    }
}