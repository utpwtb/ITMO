package com.itmo.weblab4.entity;

import javax.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.io.Serializable;
import java.time.LocalDateTime;
import javax.json.bind.annotation.JsonbTransient;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "points")
public class Point implements Serializable {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "x", nullable = false)
    private double x;
    
    @Column(name = "y", nullable = false)
    private double y;
    
    @Column(name = "r", nullable = false)
    private double r;
    
    @Column(name = "hit", nullable = false)
    private boolean hit;
    
    @Column(name = "current_time", nullable = false)
    private LocalDateTime currentTime;
    
    @Column(name = "execution_time", nullable = false)
    private long executionTime;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @JsonbTransient
    private User user;

    public Point(double x, double y, double r, boolean hit, LocalDateTime currentTime, long executionTime, User user) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.hit = hit;
        this.currentTime = currentTime;
        this.executionTime = executionTime;
        this.user = user;
    }

}
