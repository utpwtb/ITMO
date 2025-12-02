package com.itmo.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class PointResult {
    private double x;
    private double y;
    private double r;
    private boolean isHit;
    private LocalDateTime currentTime;
    private long executionTime;

}
