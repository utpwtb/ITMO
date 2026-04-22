package com.itmo.core.utils.models;

/**
 * 收敛性检查结果
 */
public record ConvergenceCheck(boolean converges, String message) {}
