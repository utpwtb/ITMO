package com.itmo.model.pojo;

import java.time.LocalDateTime;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Point {
    private double x;
    private double y;
    private double r;
    private boolean isHit;
    private LocalDateTime currentTime;
    private String executionTime;
}
