package com.itmo.core.utils.models;

/**
 * 带间断点处理的积分计算结果
 */
public record IntegrationWithDiscontinuity(double value, int maxN, boolean success, String detailLog, String errorMessage) {}
